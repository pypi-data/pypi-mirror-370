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
    conn.commit()
    conn.close()


    # --- Roles table + seed ---
    conn.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT '',
        is_admin INTEGER NOT NULL DEFAULT 0,
        is_superadmin INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # canonical roles
    seed_roles = [
        ("user", "Default non-privileged user", 0, 0),
        ("admin", "Administrative user", 1, 0),
        ("superadmin", "Super administrator", 1, 1),
    ]
    for r in seed_roles:
        conn.execute("""
            INSERT OR IGNORE INTO roles (name, description, is_admin, is_superadmin)
            VALUES (?, ?, ?, ?)
        """, r)


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

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.")
            return redirect(url_for("login", next=request.path))
        if session.get("role") not in ("admin", "superadmin"):
            flash("You do not have permission to access this page.")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

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
    