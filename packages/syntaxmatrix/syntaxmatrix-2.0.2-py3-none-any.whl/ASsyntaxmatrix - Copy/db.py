# syntaxmatrix/db.py
from datetime import datetime
import sqlite3
import time
import os
import json
from werkzeug.utils import secure_filename
from syntaxmatrix.project_root import detect_project_root

_CLIENT_DIR = detect_project_root()
DB_PATH = os.path.join(_CLIENT_DIR, "data", "syntaxmatrix.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)



# ***************************************
# Pages Table Functions
# ***************************************
def init_db():
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            name TEXT PRIMARY KEY,
            content TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS askai_cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            question TEXT,
            output TEXT,
            code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    

def get_pages():
    """Return {page_name: full_html_string} by reading each stored file path."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT name, content FROM pages").fetchall()
    conn.close()

    pages = {}
    for name, file_path in rows:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                pages[name] = f.read()
        except FileNotFoundError:
            pages[name] = f"<p>Missing file for page '{name}'.</p>"
    return pages


def add_page(name, html):
    """Create *.html file, save its path in the DB."""
    filename = secure_filename(name.lower()) + ".html"
    file_dir = os.path.join(_CLIENT_DIR, "templates")
    os.makedirs(file_dir, exist_ok=True)
    file_path = os.path.join(file_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pages (name, content) VALUES (?, ?)", (name, file_path))
    conn.commit()
    conn.close()


def update_page(old_name, new_name, html):
    """Overwrite the file; rename it (and DB row) if the title changes."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT content FROM pages WHERE name = ?", (old_name,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return
    file_path = row[0]

    # Rename file & path if page title changed
    if old_name != new_name:
        new_filename = secure_filename(new_name.lower()) + ".html"
        new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
        os.rename(file_path, new_file_path)
        file_path = new_file_path

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    cur.execute("UPDATE pages SET name = ?, content = ? WHERE name = ?",
                (new_name, file_path, old_name))
    conn.commit()
    conn.close()


def delete_page(name):
    """Remove file from disk, then delete the DB row."""
    conn   = sqlite3.connect(DB_PATH)
    cur    = conn.cursor()
    cur.execute("SELECT content FROM pages WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        file_path = row[0]
        if os.path.exists(file_path):
            os.remove(file_path)

    cur.execute("DELETE FROM pages WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def add_askai_cell(session_id, question, output, code):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO askai_cells (session_id, question, output, code) VALUES (?, ?, ?, ?)",
        (session_id, question, output, code)
    )
    conn.commit()
    conn.close()

def get_askai_cells(session_id, limit=15):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT question, output, code FROM askai_cells WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    cells = [{"question": q, "output": o, "code": c} for q, o, c in cursor.fetchall()]
    conn.close()
    return cells

