# syntaxmatrix/session.py
import uuid
from flask import request, g

COOKIE_NAME = "smx_session"

def ensure_session_cookie():
    """
    If the visitor has no smx_session cookie, generate a UUID4 and remember
    it for the response phase.  Store the final ID in flask.g so the rest
    of the request can reuse it.
    """
    sid = request.cookies.get(COOKIE_NAME)
    if not sid:
        sid = str(uuid.uuid4())
        g._smx_new_sid = sid          # flag for after_request
    else:
        sid = str(sid)
    g.smx_session_id = sid            # always available downstream
