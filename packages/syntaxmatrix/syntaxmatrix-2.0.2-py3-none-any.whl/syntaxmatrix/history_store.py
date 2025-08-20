from __future__ import annotations

import os, json, sqlite3
import atexit, logging, json, os, uuid, sqlite3
from pathlib import Path
from flask import session, has_request_context
from threading import Lock
from datetime import datetime
from syntaxmatrix.project_root import detect_project_root


_CLIENT_DIR =  detect_project_root()
# ——— Anonymous-user JSON fallback store ——————————————
_fallback_dir = os.path.join(_CLIENT_DIR, "data", "smx_history")
os.makedirs(_fallback_dir, exist_ok=True)

# Persist chats.db under dev app’s data/ directory
CHAT_DB_PATH = os.path.join(_CLIENT_DIR, "data", "chats.db")
os.makedirs(os.path.dirname(CHAT_DB_PATH), exist_ok=True)

# Initialize the chats table if needed
_sql_conn = sqlite3.connect(CHAT_DB_PATH, check_same_thread=False)
_sql_conn.execute("""
CREATE TABLE IF NOT EXISTS chats (
    user_id TEXT NOT NULL,
    chat_id TEXT NOT NULL,
    title TEXT NOT NULL,
    history TEXT NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (user_id, chat_id)
);
""")
_sql_conn.commit()
_sql_conn.close()


class SQLHistoryStore:
    """Load/save full histories for logged-in users."""
    # ---------------------------------------------
    def load(user_id: str, chat_id: str) -> list[tuple[str, str]]:
        """
        Return just the chat history for this (user_id, chat_id).
        """
        conn = sqlite3.connect(CHAT_DB_PATH)
        cur = conn.execute(
            "SELECT history FROM chats WHERE user_id=? AND chat_id=?",
            (user_id, chat_id)
        )
        row = cur.fetchone()
        conn.close()
        if not row or row[0] is None:
            return []
        return json.loads(row[0])

    @staticmethod
    def load_with_title(user_id: str, chat_id: str) -> tuple[str | None, list[tuple[str, str]]]:
        """
        Returns (title, history) for that chat; title may be None if never set.
        """
        conn = sqlite3.connect(CHAT_DB_PATH)
        cur = conn.execute(
            "SELECT title, history FROM chats WHERE user_id=? AND chat_id=?",
            (user_id, chat_id)
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None, []
        title, hist_json = row
        return title, json.loads(hist_json)

    
    @staticmethod
    def save(user_id: str, chat_id: str, history: list[tuple[str, str]], title: str = None):
        """
        Upsert this chat’s history *and* title into chats.db.
        """
        conn = sqlite3.connect(CHAT_DB_PATH)
        payload = json.dumps(history, ensure_ascii=False)
        now = datetime.utcnow().isoformat()
        # if caller didn’t supply a title, preserve existing or default
        if title is not None:
            conn.execute(
                "INSERT OR REPLACE INTO chats (user_id, chat_id, title, history, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, chat_id, title, payload, now)
            )
        else:
            conn.execute(
                "UPDATE chats SET history = ?, updated_at = ? WHERE user_id = ? AND chat_id = ?",
                (payload, now, user_id, chat_id)
            )
        conn.commit()
        conn.close()
    
    @staticmethod
    def list_chats(user_id: str) -> list[str]:
        conn = sqlite3.connect(CHAT_DB_PATH)
        cur  = conn.execute(
            "SELECT chat_id FROM chats WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,)
        )
        ids = [r[0] for r in cur.fetchall()]
        conn.close()
        return ids
        
    
    @staticmethod
    def delete(user_id:str, chat_id:str):
        conn = sqlite3.connect(CHAT_DB_PATH)
        conn.execute(
            "DELETE FROM chats WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        conn.commit()
        conn.close()


class PersistentHistoryStore:

    # for serializing access to the JSON fallback files
    _lock = Lock()

    @classmethod
    def _sid(cls, candidate: str | None) -> str:
        # If the user is logged in, we key off their user_id so history persists across sessions
        if has_request_context() and session.get("user_id"):
            return str(session["user_id"])
        return candidate or str(uuid.uuid4())

    @classmethod
    def load(cls, session_cookie: str | None, chat_id: str) -> list[tuple[str, str]]:
        """For logged-in users, hit the SQL store. Otherwise, load data/smx_history/<chat_id>.json."""
        # 1) SQL-backed
        if has_request_context() and session.get("user_id"):
            sid = cls._sid(session_cookie)
            return SQLHistoryStore.load(sid, chat_id)

        # 2) JSON fallback: one file per chat
        file_path = os.path.join(_fallback_dir, f"{chat_id}.json")
        if not os.path.exists(file_path):
            return []
        with cls._lock:
            return json.load(open(file_path, "r", encoding="utf-8"))

    @classmethod    
    def save(cls, session_cookie: str | None, chat_id: str, history: list[tuple[str, str]]):
        """For logged-in users, write into SQL. Otherwise, overwrite data/smx_history/<chat_id>.json."""
        # 1) SQL-backed
        if has_request_context() and session.get("user_id"):
            sid = cls._sid(session_cookie)
            SQLHistoryStore.save(sid, chat_id, history)
            return

        # 2) JSON fallback
        file_path = os.path.join(_fallback_dir, f"{chat_id}.json")
        with cls._lock:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
    

    @classmethod
    def delete(cls, session_cookie: str | None, chat_id: str):
        """Delete one chat: SQL row for logged-in users, or remove <chat_id>.json for anonymous."""
        # 1) SQL-backed
        if has_request_context() and session.get("user_id"):
            sid = cls._sid(session_cookie)
            return SQLHistoryStore.delete(sid, chat_id)

        # 2) JSON fallback: just drop the file
        file_path = os.path.join(_fallback_dir, f"{chat_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)


@atexit.register
def _clear_anonymous_history_on_exit() -> None:
    """
    On clean shutdown, delete all JSON chat files for anonymous users
    under data/smx_history/, leaving chats.db untouched.
    """
    history_dir = Path(_fallback_dir)
    if not history_dir.is_dir():
        return

    for file_path in history_dir.glob("*.json"):
        try:
            file_path.unlink()
        except Exception as e:
            logging.warning(
                f"syntaxmatrix: failed to delete anonymous history file {file_path}: {e}"
            )