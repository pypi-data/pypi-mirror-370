# syntaxmatrix/llm_store.py
import os
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet, InvalidToken
from .workspace_db import SessionLocal, Workspace, LLMModel, LLMProfile 
from typing import Optional, List, Dict
from syntaxmatrix.project_root import detect_project_root

# ------------------------------------------------------------------
#   This file handles LLM profiles and settings, using a local SQLite database.
#   It uses SQLAlchemy for ORM and Fernet for symmetric encryption of API keys.
#   Ensures a stable encryption key, no env var needed.
# ------------------------------------------------------------------
_CLIENT_DIR = detect_project_root()
KEY_PATH = os.path.join(_CLIENT_DIR, "data", "fernet.key")
if os.path.exists(KEY_PATH):
    __FERNET = Fernet(open(KEY_PATH, "rb").read())
else:
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
    open(KEY_PATH, "wb").write(key)
    __FERNET = Fernet(key)

def _session_and_ws() -> tuple[Session, Workspace]:
    sess = SessionLocal()
    ws  = sess.query(Workspace).filter_by(name="default").first()
    if ws is None:
        ws = Workspace(name="default")
        sess.add(ws)
        sess.commit()
    return sess, ws


# ------------------------------------------------------------------
#  LLM Settings helpers (Provider, Model, API Key)
# ------------------------------------------------------------------
def save_embed_model(provider: str, model: str, api_key: str):
    try:
        sess, ws = _session_and_ws()
        ws.llm_provider = provider
        ws.llm_model = model
        if api_key and api_key != "********":          
            ws.llm_api_key = __FERNET.encrypt(api_key.encode())
        sess.commit()
        sess.close()
        return True
    except:
        return False

def load_embed_model() -> dict:
    sess, ws = _session_and_ws()
    try:
        key = (
            __FERNET.decrypt(ws.llm_api_key).decode()
            if ws.llm_api_key
            else ""
        )
    except InvalidToken:
        key = ""
    result = {
        "provider": ws.llm_provider,
        "model": ws.llm_model,
        "api_key": key,
    }
    sess.close()
    return result

def delete_embed_key() -> bool:
    sess, ws = _session_and_ws()
    if ws.llm_api_key:
        ws.llm_api_key = b""
        sess.commit()
        sess.close()
        return True
    sess.close()
    return False


# ------------------------------------------------------------------
# Catalog helpers (Provider ⇢ Model ⇢ Purpose)
# ------------------------------------------------------------------
def add_model(provider: str, model: str, purpose: str, llm_desc: Optional[str] = None) -> bool:
    """Insert one row unless it already exists (returns True if created)."""
    sess, _ = _session_and_ws()
    
    exists = sess.query(LLMModel).filter_by(provider=provider, model=model).first()
    if exists:
        sess.close()
        return False
    
    sess.add(LLMModel(
        provider=provider,
        model=model,
        purpose_tag=purpose,
        desc=llm_desc,
    ))
    sess.commit()
    sess.close()
    return True


def list_models() -> list[dict]:
    sess, _ = _session_and_ws()

    rows = sess.query(LLMModel).order_by(LLMModel.provider, LLMModel.model).all()
    out  = [dict(
            id=r.id,
            provider=r.provider,
            model=r.model,
            purpose=r.purpose_tag,
            desc=r.desc,
        )
        for r in rows]
    sess.close()
    return out


def get_model(model_id: int) -> Optional[dict]:
    """Fetch one model by its ID."""
    sess, _ = _session_and_ws()
    from .workspace_db import LLMModel

    row = sess.query(LLMModel).filter_by(id=model_id).first()
    sess.close()
    if not row:
        return None

    return {
        "id":        row.id,
        "provider":  row.provider,
        "model":     row.model,
        "purpose":   row.purpose_tag,
        "desc":  row.desc,
    }


def update_model(
    model_id: int,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    purpose: Optional[str] = None,
    desc: Optional[str] = None,
) -> bool:
    """Update any of the fields on an existing model."""
    sess, _ = _session_and_ws()
    
    row = sess.query(LLMModel).filter_by(id=model_id).first()
    if not row:
        sess.close()
        return False

    if provider:    row.provider    = provider
    if model:       row.model       = model
    if purpose:     row.purpose_tag = purpose
    # allow empty string vs. None to clear vs. leave untouched
    if desc is not None:
        row.llm_desc = desc

    sess.commit()
    sess.close()
    return True


def delete_model(row_id: int) -> None:
    sess, _ = _session_and_ws()

    row = sess.query(LLMModel).filter_by(id=row_id).first()
    if row:
        sess.delete(row)
        sess.commit()
    sess.close()


# ------------------------------------------------------------------
# 1. LLM Profile helpers (multi-model support)
# ------------------------------------------------------------------
def upsert_profile(name: str, provider: str, model: str, api_key: str, desc: str, purpose: str = "general"):
    sess, ws = _session_and_ws()

    # only consider profiles in this workspace
    prof = sess.query(LLMProfile)\
               .filter_by(name=name, workspace_id=ws.id)\
               .first()
    if not prof:
        prof = LLMProfile(
            name=name,
            workspace_id=ws.id    # tie to current workspace
        )
        sess.add(prof)

    prof.provider = provider
    prof.model = model
    prof.purpose_tag = purpose
    prof.desc = desc
    if api_key and api_key != "********":
        prof.api_key = __FERNET.encrypt(api_key.encode())
    
    sess.commit()
    sess.close()
    return True


def load_profile(name: str) -> Optional[dict]:
    sess, ws = _session_and_ws()

    # only load from this workspace
    prof = sess.query(LLMProfile)\
               .filter_by(name=name, workspace_id=ws.id)\
               .first()
    if not prof:
        sess.close()
        return None
    try:
        key = __FERNET.decrypt(prof.api_key).decode() if prof.api_key else ""
    except InvalidToken:
        key = ""
    result = {
        "name":      prof.name,
        "purpose":   prof.purpose_tag,
        "provider":  prof.provider,
        "model":     prof.model,
        "api_key":   key,
    }
    sess.close()
    return result

def list_profiles() -> List[Dict]:
    sess, ws = _session_and_ws()

    # only list profiles for this workspace
    rows = sess.query(LLMProfile)\
               .filter_by(workspace_id=ws.id)\
               .all()
    profiles = [
        {
            "name":      r.name,
            "purpose":   r.purpose_tag,
            "provider":  r.provider,
            "model":     r.model,
        }
        for r in rows
    ]
    sess.close()
    return profiles

def delete_profile(name: str) -> None:
    """Remove a stored LLM profile by its unique name."""
    sess, _ = _session_and_ws()
    from .workspace_db import LLMProfile

    prof = sess.query(LLMProfile).filter_by(name=name).first()
    if prof:
        sess.delete(prof)
        sess.commit()
    sess.close()
