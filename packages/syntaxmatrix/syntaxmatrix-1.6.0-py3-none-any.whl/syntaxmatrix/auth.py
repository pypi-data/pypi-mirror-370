from __future__ import annotations
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Dict
from functools import wraps
from flask import session, redirect, url_for, flash, request, render_template_string, redirect, url_for, flash
from dotenv import load_dotenv
from syntaxmatrix.project_root import detect_project_root
from .project_root import detect_project_root
import secrets, stat


_CLIENT_DIR = detect_project_root()
AUTH_DB_PATH = os.path.join(_CLIENT_DIR, "data", "auth.db")
os.makedirs(os.path.dirname(AUTH_DB_PATH), exist_ok=True)

dotenv_path  = os.path.join(str(_CLIENT_DIR.parent), ".env")
if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path, override=True)


def _get_conn():
    conn = sqlite3.connect(AUTH_DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_auth_db():
    """Create users table and seed the superadmin from env vars."""
    # --- Users table ---
    conn = _get_conn()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # --- Roles table ---
    conn.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT '',
        is_employee INTEGER NOT NULL DEFAULT 0,
        is_admin INTEGER NOT NULL DEFAULT 0,
        is_superadmin INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # --- Role change audit table ---
    conn.execute("""
    CREATE TABLE IF NOT EXISTS role_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor_id INTEGER,
        actor_label TEXT,
        target_id INTEGER NOT NULL,
        target_label TEXT,
        from_role TEXT NOT NULL,
        to_role TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)

    row = conn.execute(
        "SELECT 1 FROM users WHERE username = 'ceo' AND role='superadmin'"
    ).fetchone()

    if not row:
        # (a) generate or read the one-off password file
        fw_data_dir = _CLIENT_DIR  # returns Path to <project>/.syntaxmatrix
        cred_file = fw_data_dir / "superadmin_creds.txt"

        superadmin_email = "ceo@syntaxmatrix.sx"
        superadmin_username = "ceo"

        if cred_file.exists():
            raw_pw = cred_file.read_text().strip()

        else:
            raw_pw = secrets.token_urlsafe(16)       # ~128 bits of entropy
            fw_data_dir.mkdir(exist_ok=True)        # ensure folder exists
            cred_file.write_text(f"""
                                Email: {superadmin_email} \n
                                Username: {superadmin_username} \n
                                Password: {raw_pw}
                            """)
            cred_file.chmod(0o600)
        
        pw_hash = generate_password_hash(raw_pw)
        conn.execute(
            "INSERT INTO users (email, username, password, role) "
            "VALUES (?, ?, ?, ?)",
            (superadmin_email, superadmin_username, pw_hash, "superadmin")
        )

    # --- Roles table + seed ---
    # canonical roles
    seed_roles = [
        ("user", "Default registration", 0, 0, 0),
        ("employee", "Employee", 1, 0, 0),
        ("admin", "Administrator", 1, 1, 0),
        ("superadmin", "Super administrator", 1, 1, 1),
    ]
    for r in seed_roles:
        conn.execute("""
            INSERT OR IGNORE INTO roles (name, description, is_employee, is_admin, is_superadmin)
            VALUES (?, ?, ?, ?, ?)
        """, r)
    
    conn.commit()
    conn.close()


def list_roles():
    conn = _get_conn()
    rows = conn.execute("""
        SELECT id, name, description, is_employee, is_admin, is_superadmin, created_at
        FROM roles
        ORDER BY
          CASE name
            WHEN 'superadmin' THEN 0
            WHEN 'admin' THEN 1
            WHEN 'employee' THEN 2
            WHEN 'user' THEN 3
            ELSE 4
          END, name
    """).fetchall()
    conn.close()
    return [
        {
            "id": r[0], "name": r[1], "description": r[2],
            "is_employee": bool(r[3]), "is_admin": bool(r[4]),
            "is_superadmin": bool(r[5]), "created_at": r[6]
        } for r in rows
    ]


RESERVED_ROLES = {"user", "employee", "admin", "superadmin"}

def create_role(name: str, description: str = "", *, is_employee: bool = False, is_admin: bool = False) -> bool:
    name = (name or "").strip().lower()
    if not name or name in RESERVED_ROLES:
        return False
    if is_employee and is_admin:
        # keep the hierarchy simple: a role can't be both employee and admin
        return False
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO roles (name, description, is_employee, is_admin, is_superadmin) VALUES (?, ?, ?, ?, 0)",
            (name, description or "", 1 if is_employee else 0, 1 if is_admin else 0)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_role(role_name: str):
    """
    Delete a custom role if:
      - it is not reserved (superadmin, admin, employee, user)
      - no users are currently assigned to it
    Returns (ok, error_message_or_None)
    """
    import sqlite3
    from . import db as _db

    if not role_name:
        return (False, "missing role_name")

    name_l = role_name.strip().lower()
    if name_l in {"superadmin", "admin", "employee", "user"}:
        return (False, "reserved role")

    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ensure role exists
    cur.execute("SELECT id FROM roles WHERE lower(name)=?", (name_l,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return (False, "not found")

    # block if any user has this role
    cur.execute("SELECT COUNT(*) AS c FROM users WHERE lower(role)=?", (name_l,))
    in_use = (cur.fetchone() or {"c": 0})["c"]
    if in_use:
        conn.close()
        return (False, "role in use by users")

    cur.execute("DELETE FROM roles WHERE lower(name)=?", (name_l,))
    conn.commit()
    conn.close()
    return (True, None)

#############################################################
# --- Minimal helpers for the Admin Users card ---
def list_users():
    """Return users for admin listing."""
    conn = _get_conn()
    rows = conn.execute("""
        SELECT id, email, username, role, created_at
        FROM users
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "email": r[1],
            "username": r[2],
            "role": (r[3] or "user"),
            "created_at": r[4],
        })
    return out


def _can_assign_role(actor_role: str, from_role: str, to_role: str) -> bool:
    """Business rules:
       - Admin can only do user -> employee
       - Only superadmin can promote employee -> admin (or user -> admin)
       - Never demote a superadmin
    """
    actor_role = (actor_role or "").lower()
    from_role  = (from_role or "").lower()
    to_role    = (to_role   or "").lower()

    if actor_role == "superadmin":
        if from_role == "superadmin" and to_role != "superadmin":
            return False
        return True

    if actor_role == "admin":
        # admins can: user -> employee  OR  employee -> user
        return (from_role == "user" and to_role == "employee") or \
               (from_role == "employee" and to_role == "user")

    return False


def set_user_role(actor_role: str, user_id: int, role_name: str) -> bool:
    """Assign a role to a user, enforcing the rules above."""
    role_name = (role_name or "").strip().lower()
    if not role_name:
        return False

    conn = _get_conn()
    try:
        # ensure target role exists
        exists = conn.execute(
            "SELECT 1 FROM roles WHERE name = ?", (role_name,)
        ).fetchone()
        if not exists:
            return False

        # current role of target user
        row = conn.execute(
            "SELECT role FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not row:
            return False
        from_role = (row[0] or "user")

        if not _can_assign_role(actor_role, from_role, role_name):
            return False

        conn.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (role_name, user_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()



def register_user(email:str, username:str, password:str, role:str = "user") -> bool:
    """Return True if registration succeeded, False if username taken."""
    hashed = generate_password_hash(password)
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            (email, username, hashed, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate(email:str, password:str) -> Optional[Dict]:
    """Return user dict if creds match, else None."""
    conn = _get_conn()
    cur = conn.execute(
        "SELECT id, email, username, password, role FROM users WHERE email = ?",
        (email,)
    )
    row = cur.fetchone()
    conn.close()
    if row and check_password_hash(row[3], password):
        return {"id": row[0], "email":row[1], "username": row[2], "role": row[4]}
    return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        role = (session.get("role") or "").lower()
        if not has_admin_privileges(role):
            flash("You do not have permission to access that page.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def superadmin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.")
            return redirect(url_for("login", next=request.path))
        if session.get("role") != "superadmin":
            flash("You do not have permission to access this page.")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


def has_admin_privileges(role_name: str) -> bool:
    role = (role_name or "").strip().lower()
    if role == "superadmin":
        return True
    conn = _get_conn()
    row = conn.execute("SELECT is_admin FROM roles WHERE name = ?", (role,)).fetchone()
    conn.close()
    return bool(row and row[0])


def get_user_basic(user_id: int):
    if not user_id:
        return None
    conn = _get_conn()
    row = conn.execute(
        "SELECT id, email, username, role FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "email": row[1], "username": row[2], "role": (row[3] or "user")}

def add_role_audit(actor_id: int, actor_label: str, target_id: int, target_label: str, from_role: str, to_role: str):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO role_audit (actor_id, actor_label, target_id, target_label, from_role, to_role) VALUES (?,?,?,?,?,?)",
        (actor_id, actor_label or "", target_id, target_label or "", (from_role or "user"), (to_role or "user"))
    )
    conn.commit()
    conn.close()

def list_role_audit(limit: int = 50):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT actor_label, target_label, from_role, to_role, created_at FROM role_audit ORDER BY id DESC LIMIT ?",
        (int(limit),)
    ).fetchall()
    conn.close()
    return [
        {"actor_label": r[0], "target_label": r[1], "from_role": r[2], "to_role": r[3], "created_at": r[4]}
        for r in rows
    ]


def delete_user(actor_id: int, target_id: int) -> bool:
    """Delete a user account. Blocks deleting superadmin and self."""
    if not target_id or (actor_id and actor_id == target_id):
        return False
    conn = _get_conn()
    try:
        row = conn.execute("SELECT role FROM users WHERE id = ?", (target_id,)).fetchone()
        if not row:
            return False
        if (row[0] or "user").lower() == "superadmin":
            return False
        conn.execute("DELETE FROM users WHERE id = ?", (target_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def clear_role_audit(before_iso: Optional[str] = None) -> int:
    """
    Delete audit rows. If before_iso is provided (ISO timestamp or 'YYYY-MM-DD'),
    delete only rows older than that. Returns number of rows removed.
    """
    conn = _get_conn() 

    if before_iso:
        conn.execute(
            "DELETE FROM role_audit WHERE datetime(created_at) < datetime(?)",
            (before_iso,)
        )
    else:
        conn.execute("DELETE FROM role_audit")
    deleted = conn.rowcount if hasattr(conn, "rowcount") else 0
    conn.commit()
    return int(deleted)

