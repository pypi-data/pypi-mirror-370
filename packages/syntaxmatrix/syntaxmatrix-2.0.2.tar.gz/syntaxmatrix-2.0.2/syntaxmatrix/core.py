from __future__ import annotations
from pyexpat import model
import os, webbrowser, uuid, secrets

from flask import Flask, session, request, has_request_context
from .history_store import SQLHistoryStore as Store, PersistentHistoryStore as _Store
from collections import OrderedDict
from syntaxmatrix.llm_store import save_embed_model, load_embed_model, delete_embed_key
from . import db, routes
from .themes import DEFAULT_THEMES
from .ui_modes import UI_MODES
from .plottings import render_plotly, pyplot
from .file_processor import process_admin_pdf_files
from google import genai
from openai import OpenAI
from .vector_db import query_embeddings
from .vectorizer import embed_text
from syntaxmatrix.settings.prompts import SMX_PROMPT_PROFILE, SMX_PROMPT_INSTRUCTIONS, SMX_WEBSITE_DESCRIPTION
from typing import List
from .auth import init_auth_db
from . import profiles as _prof
from syntaxmatrix.utils import strip_describe_slice, drop_bad_classification_metrics
from syntaxmatrix.smiv import SMIV
from .project_root import detect_project_root
from syntaxmatrix.gpt_models_latest import extract_output_text as _out, set_args 
from dotenv import load_dotenv


# ──────── framework‐local storage paths ────────
# this ensures the key & data always live under the package dir,
# regardless of where the developer `cd` into before launching.
_CLIENT_DIR = detect_project_root()
_HISTORY_DIR   = os.path.join(_CLIENT_DIR, "data", "smx_history")
os.makedirs(_HISTORY_DIR, exist_ok=True)
_SECRET_PATH   = os.path.join(_CLIENT_DIR, "data", ".smx_secret_key")

dotenv_path  = os.path.join(str(_CLIENT_DIR.parent), ".env")

if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path, override=True)

EDA_OUTPUT = {}  # global buffer for EDA output by session

class SyntaxMUI:
    def __init__(
            self, 
            host="127.0.0.1", 
            port="5050", 
            user_icon="👩🏿‍🦲",
            bot_icon='<img src="../static/icons/favicon.ico" alt="bot icon" width="20"/>',           
            favicon='<img src="../static/icons/favicon.ico" width="15"/>',          
            site_logo='<img src="../static/icons/logo.png" width="30" alt="SMX Logo"/>',
            site_title="SyntaxMatrix", 
            project_title="smxAI Engine", 
            theme_name="light"
        ):
        self.app = Flask(__name__)   
        self.get_app_secrete()      
        self.host = host
        self.port = port
        self.user_icon = user_icon
        self.bot_icon = bot_icon
        self.favicon = favicon
        self.site_title = site_title
        self.site_logo = site_logo
        self.project_title = project_title
        self.ui_mode = "default"
        self.theme_toggle_enabled = True
        self.user_files_enabled = True
        self.prompt_profile = SMX_PROMPT_PROFILE
        self.prompt_instructions = SMX_PROMPT_INSTRUCTIONS    
        self.website_description = SMX_WEBSITE_DESCRIPTION

        db.init_db()
        self.page = ""
        self.pages = db.get_pages()
        init_auth_db() 

        self.widgets = OrderedDict()
        self.theme = DEFAULT_THEMES.get(theme_name, DEFAULT_THEMES["light"])     
        self.system_output_buffer = ""  # Ephemeral buffer initialized  
        self.app_token = str(uuid.uuid4())  # NEW: Unique token for each app launch.
        self.admin_pdf_chunks = {}   # In-memory store for admin PDF chunks
        self.user_file_chunks = {}  # In-memory store of user‑uploaded chunks, scoped per chat session
        routes.setup_routes(self)

        self._chat_profile = {}
        self._coding_profile = {}
        self._classification_profile = {}
        self._summarization_profile = {}
        self._admin_profile = {}
        
        self._gpt_models_latest_prev_resp_ids = {}

    def init_app(app):
        import os, secrets
        if not app.secret_key:
            app.secret_key = secrets.token_urlsafe(32)   
    

    def get_app_secrete(self):
        if os.path.exists(_SECRET_PATH):
            self.app.secret_key = open(_SECRET_PATH, "r", encoding="utf-8").read().strip()
        else:
            new_key = secrets.token_urlsafe(32)
            open(_SECRET_PATH, "w", encoding="utf-8").write(new_key)
            self.app.secret_key = new_key


    def _get_visual_context(self):
        """Return the concatenated summaries for prompt injection."""
        if not self._recent_visual_summaries:
            return ""
        joined = "\n• " + "\n• ".join(self._recent_visual_summaries)
        return f"\n\nRecent visualizations:{joined}"


    def set_plottings(self, fig_or_html, note=None):
        sid = session.get("current_session", {}).get("id", "default")
        if not fig_or_html or (isinstance(fig_or_html, str) and fig_or_html.strip() == ""):
            EDA_OUTPUT[sid] = ""
            return

        html = None

        # ---- Plotly Figure support ----
        try:
            import plotly.graph_objs as go
            if isinstance(fig_or_html, go.Figure):
                html = fig_or_html.to_html(full_html=False)
        except ImportError:
            pass

        # ---- Matplotlib Figure support ----
        if html is None and hasattr(fig_or_html, "savefig"):
            html = pyplot(fig_or_html)

        # ---- Bytes (PNG etc.) support ----
        if html is None and isinstance(fig_or_html, bytes):
            import base64
            img_b64 = base64.b64encode(fig_or_html).decode()
            html = f"<img src='data:image/png;base64,{img_b64}'/>"

        # ---- HTML string support ----
        if html is None and isinstance(fig_or_html, str):
            html = fig_or_html

        if html is None:
            raise TypeError("Unsupported object type for plotting.")

        if note:
            html += f"<div style='margin-top:10px; text-align:center; color:#888;'><strong>{note}</strong></div>"

        wrapper = f'''
        <div style="
            position:relative; max-width:650px; margin:30px auto 20px auto;
            padding:20px 28px 10px 28px; background:#fffefc;
            border:2px solid #2da1da38; border-radius:16px;
            box-shadow:0 3px 18px rgba(90,130,230,0.06); min-height:40px;">
            <button id="eda-close-btn" onclick="closeEdaPanel()" style="
                position: absolute; top: 20px; right: 12px;
                font-size: 1.25em; background: transparent;
                border: none; color: #888; cursor: pointer;
                z-index: 2; transition: color 0.2s;">&times;</button>
            {html}
        </div>
        '''
        EDA_OUTPUT[sid] = wrapper


    def get_plottings(self):
        sid = session.get("current_session", {}).get("id", "default")
        return EDA_OUTPUT.get(sid, "")
    

    def load_sys_chunks(self, directory: str = "uploads/sys"):
        """
        Process all PDFs in `directory`, store chunks in DB and cache in-memory.
        Returns mapping { file_name: [chunk, ...] }.
        """
        mapping = process_admin_pdf_files(directory)
        self.admin_pdf_chunks = mapping
        return mapping


    def smpv_search(self, q_vec: List[float], top_k: int = 5):
        """
        Embed the input text and return the top_k matching PDF chunks.
        Each result is a dict with keys:
        - 'id': the embedding record UUID
        - 'score': cosine similarity score (0–1)
        - 'metadata': dict, e.g. {'file_name': ..., 'chunk_index': ...}
        """
        # 2) Fetch nearest neighbors from our sqlite vector store
        results = query_embeddings(q_vec, top_k=top_k)
        return results


    def set_ui_mode(self, mode):
        if mode not in self.list_ui_modes():  # ["default", "card", "bubble", "smx"]:
            raise ValueError("UI mode must be one of: 'default', 'card', 'bubble', 'smx'.")
        self.ui_mode = mode


    @staticmethod
    def list_ui_modes():
        return list(UI_MODES.keys())
        return "default", "card", "bubble", "smx"
    
    @staticmethod
    def list_themes():
        return list(DEFAULT_THEMES.keys())
    

    def set_theme(self, theme_name, theme):
        if theme_name in DEFAULT_THEMES:
            self.theme = DEFAULT_THEMES[theme_name]
        elif isinstance(theme, dict):
            self.theme["custom"] = theme
            DEFAULT_THEMES[theme_name] = theme
        else:
            self.theme = DEFAULT_THEMES["light"]
            raise ValueError("Theme must be 'light', 'dark', or a custom dict.")
    

    def enable_theme_toggle(self):
        self.theme_toggle_enabled = True
    

    def disable_theme_toggle(self):
        self.theme_toggle_enabled = False
    
    def enable_user_files(self):
        self.user_files_enabled = True

    def disable_user_files(self):
        self.user_files_enabled = False

    def columns(self, components):
        col_html = "<div style='display:flex; gap:10px;'>"
        for comp in components:
            col_html += f"<div style='flex:1;'>{comp}</div>"
        col_html += "</div>"
        return col_html
    

    def set_favicon(self, icon):
        self.favicon = icon


    def set_site_title(self, title):
        self.site_title = title
    

    def set_site_logo(self, logo):
        self.site_logo = logo


    def set_project_title(self, project_title):
        self.project_title = project_title


    def set_user_icon(self, icon):
        self.user_icon = icon


    def set_bot_icon(self, icon):
        self.bot_icon = icon


    def text_input(self, key, label, placeholder="Ask me anything"):
        if key not in self.widgets:
            self.widgets[key] = {"type": "text_input", "key": key, "label": label, "placeholder": placeholder}


    def clear_text_input_value(self, key):
        session[key] = ""
        session.modified = True
    

    def button(self, key, label, callback=None, stream=False):
        self.widgets[key] = {
            "type": "button", "key": key,
            "label": label,  "callback": callback,
            "stream": stream       
        }


    def file_uploader(self, key, label, accept_multiple_files=False, callback=None):
        if key not in self.widgets:
            self.widgets[key] = {
                "type": "file_upload",
                "key": key, "label": label,
                "accept_multiple": accept_multiple_files,
               "callback": callback
        }


    def get_file_upload_value(self, key):
        return session.get(key, None)
    

    def dropdown(self, key, options, label=None, callback=None):
        self.widgets[key] = {
            "type": "dropdown",
            "key": key,
            "label": label if label else key,
            "options": options,
            "callback": callback,
            "value": options[0] if options else None
        }


    def get_widget_value(self, key):
        return self.widgets[key]["value"] if key in self.widgets else None


    # ──────────────────────────────────────────────────────────────
    # Session-safe chat-history helpers
    # ──────────────────────────────────────────────────────────────
    @staticmethod
    def _sid() -> str:
        sid = session.get("_smx_sid")
        if not sid:
            # use the new _sid helper on the store instead of the old ensure_session_id
            sid = _Store._sid(request.cookies.get("_smx_sid"))
        session["_smx_sid"] = sid
        session.modified = True
        return sid
    

    def get_chat_history(self) -> list[tuple[str, str]]:
        # now load the history for the _current_ chat session
        sid = self._sid()
        cid = self.get_session_id()
        return _Store.load(sid, cid)
    

    def set_chat_history(self, history: list[tuple[str, str]], *, max_items: int | None = None) -> list[tuple[str, str]]:
        sid = self._sid()
        cid = self.get_session_id()
        _Store.save(sid, cid, history)
        session["chat_history"] = history[-30:]  # still mirror a thin copy into Flask’s session cookie for the UI
        session.modified = True

        if session.get("user_id"):
            user_id = session["user_id"]
            cid = session["current_session"]["id"]
            title = session["current_session"]["title"]
            # persist both title + history 
            Store.save(user_id, cid, session["chat_history"], title)

        return history if max_items is None else history[-max_items:]


    def clear_chat_history(self):
        """
        Clear both the UI slice *and* the server-side history bucket
        for this session_id + chat_id.
        """
        if has_request_context():
            # 1) Clear the in-memory store
            from .history_store import PersistentHistoryStore as _Store
            sid = self._sid()                 # your per-browser session ID
            cid = self.get_session_id()       # current chat UUID
            _Store.save(sid, cid, [])         # wipe server history

            # 2) Clear the cookie slice shown in the UI
            session["chat_history"] = []
            # 3) Also clear out the “current_session” and past_sessions histories
            if "current_session" in session:
                session["current_session"]["history"] = []
            if "past_sessions" in session:
                session["past_sessions"] = [
                    {**s, "history": []} if s.get("id") == cid else s
                    for s in session["past_sessions"]
                ]
            session.modified = True
        else:
            self._fallback_chat_history = []

    
    def bot_message(self, content, max_length=20):
        history = self.get_chat_history()
        history.append(("Bot", content))
        self.set_chat_history(history)


    def plt_plot(self, fig):
        summary = describe_matplotlib(fig)
        self._add_visual_summary(summary)          
        html = pyplot(fig)
        self.bot_message(html)

    def plotly_plot(self, fig):
        try:
            summary = describe_plotly(fig)
            self._add_visual_summary(summary)      
            html = render_plotly(fig)
            self.bot_message(html)
        except Exception as e:
            self.error(f"Plotly rendering failed: {e}")


    def write(self, content):
        self.bot_message(content)


    def markdown(self, md_text):
        try:
            import markdown
            html = markdown.markdown(md_text)
        except ImportError:
            html = md_text
        self.write(html)
    

    def latex(self, math_text):
        self.write(f"\\({math_text}\\)")
    

    def error(self, content):
        self.bot_message(f'<div style="color:red; font-weight:bold;">{content}</div>')


    def warning(self, content):
        self.bot_message(f'<div style="color:orange; font-weight:bold;">{content}</div>')


    def success(self, content):
        self.bot_message(f'<div style="color:green; font-weight:bold;">{content}</div>')


    def info(self, content):
        self.bot_message(f'<div style="color:blue;">{content}</div>')


    def get_session_id(self):
        """Return current chat’s UUID (so we can key uploaded chunks)."""
        return session.get("current_session", {}).get("id")


    def add_user_chunks(self, session_id, chunks):
        """Append these text‐chunks under that session’s key."""
        self.user_file_chunks.setdefault(session_id, []).extend(chunks)


    def get_user_chunks(self, session_id):
        """Get any chunks that this session has uploaded."""
        return self.user_file_chunks.get(session_id, [])


    def clear_user_chunks(self, session_id):
        """Remove all stored chunks for a session (on chat‑clear or delete)."""
        self.user_file_chunks.pop(session_id, None)
    

    def stream_write(self, chunk: str, end=False):
        """Push a token to the SSE queue and, when end=True,
        persist the whole thing to chat_history."""
        from .routes import _stream_q
        _stream_q.put(chunk)              # live update
        if end:                           # final flush → history
            self.bot_message(chunk)       # persists the final message
    

    # ──────────────────────────────────────────────────────────────
    #  *********** LLM CLIENT HELPERS  **********************
    # ──────────────────────────────────────────────────────────────
    def set_prompt_profile(self, profile):
        self.prompt_profile = profile
    

    def set_prompt_instructions(self, instructions):
        self.prompt_instructions = instructions


    def set_website_description(self, desc):
        self.website_description = desc


    def embed_query(self, q):
        return embed_text(q)
    

    def smiv_index(self, sid):
            chunks = self.get_user_chunks(sid) or []
            count = len(chunks)

            # Ensure the per-session index stores for user text exist
            if not hasattr(self, "_user_indices"):
                self._user_indices = {}              # gloval dict for user vecs
                self._user_index_counts = {}         # global dict of user vec counts

            # store two maps: _user_indices and _user_index_counts
            if (sid not in self._user_indices or self._user_index_counts.get(sid, -1) != count):
                # (re)build
                try:
                    vecs = [embed_text(txt) for txt in chunks]
                except Exception as e:
                    # show the embedding error in chat and stop building the index
                    self.error(f"Failed to embed user documents: {e}")
                    return None
                index = SMIV(len(vecs[0]) if vecs else 1536)
                for i,(txt,vec) in enumerate(zip(chunks,vecs)):
                    index.add(vector=vec, metadata={"chunk_text": txt, "chunk_index": i, "session_id": sid})
                self._user_indices[sid] = index
                self._user_index_counts[sid] = count
            return self._user_indices[sid]


    def load_embed_model(self):
        client = load_embed_model()
        os.environ["PROVIDER"] = client["provider"]
        os.environ["MAIN_MODEL"] = client["model"]
        os.environ["OPENAI_API_KEY"] = client["api_key"]
        return client
    

    def save_embed_model(self, provider:str, model:str, api_key:str):
        return save_embed_model(provider, model, api_key)
    

    def delete_embed_key(self):
        return delete_embed_key()

    def gpt_models_latest(self):
        from syntaxmatrix.settings.model_map import GPT_MODELS_LATEST
        return GPT_MODELS_LATEST


    def get_text_input_value(self, key, default=""):
        q = session.get(key, default)
        
        intent = self.classify_query_intent(q)      
        if not intent:
            self.error("ERROR: Intent classification failed")
            return q, None   
        return q, intent


    def classify_query_intent(self, query: str) -> str:
        from syntaxmatrix.gpt_models_latest import extract_output_text as _out, set_args 
   
        if not self._classification_profile:
            classification_profile = _prof.get_profile('classification') or _prof.get_profile('admin')
            if not classification_profile:
                return None
            self._classification_profile = classification_profile
            self._classification_profile['client'] = _prof.get_client(classification_profile)

        _client = self._classification_profile['client']
        _provider = self._classification_profile['provider']
        _model = self._classification_profile['model']

        # New instruction format with hybrid option
        instructions = f"""
            Classify the given query into ONE of these intents You must return ONLY the intent name with no comment or any preamble:
            - "none": Casual chat/greetings
            - "user_docs": Requires user-uploaded documents
            - "system_docs": Requires company knowledge/docs
            - "hybrid": Requires BOTH user docs AND company docs
            
            Examples:
            Query: "Hi there!" → none
            Query: "Explain my uploaded contract" → user_docs
            Query: "What's our refund policy?" → system_docs
            Query: "How does my proposal align with company guidelines?" → hybrid
            Query: "What is the weather today?" → none
            Query: "Cross-reference the customer feedback from my uploaded survey results with our product's feature list in the official documentation." → hybrid

            Now classify:
            Query: "{query}"
            Intent: 
        """
        intent_profile = "You are an intent classifier. Respond ONLY with the intent name."

        openai_sdk_messages = [
            {"role": "system", "content": intent_profile},
            {"role": "user", "content": instructions}
        ]

        def google_classify_query():
            response = _client.models.generate_content(
                model=_model,
                contents=f"{intent_profile}\n{instructions}\n\n"
            )
            return response.text.strip().lower()

        def gpt_models_latest_classify_query(reasoning_effort = "medium", verbosity = "low"):
                             
            args = set_args(
                model=_model,
                instructions=intent_profile,
                input=instructions,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity,
            )
            try:
                resp = _client.responses.create(**args)
                answer = _out(resp).strip().lower() 
                return answer if answer else ""
            except Exception as e:
                return f"Error!"
            
        def openai_sdk_classify_query():
            try:
                response = _client.chat.completions.create(
                    model=_model,
                    messages=openai_sdk_messages,
                    temperature=0,
                    max_tokens=100
                )
                intent = response.choices[0].message.content.strip().lower()
                return intent if intent else ""
            except Exception as e:
                return f"Error!"

        if _provider == "google":
            intent = google_classify_query()
            return intent
        elif _model in self.gpt_models_latest():
            intent = gpt_models_latest_classify_query()
            return intent
        else:
            intent = openai_sdk_classify_query()
            return intent
     

    def generate_contextual_title(self, chat_history):
        
        if not self._summarization_profile:
            summarization_profile = _prof.get_profile('summarization') or _prof.get_profile('admin') 
            if not summarization_profile:
                return None
            
            self._summarization_profile = summarization_profile
            self._summarization_profile['client'] = _prof.get_client(summarization_profile)

        conversation = "\n".join([f"{role}: {msg}" for role, msg in chat_history])
        title_profile = "You are a title generator. Your task is to create a concise and relevant title for the given conversation."
        instructions = f"""
                Generate a contextual title (5 short words max) from the given Conversation History 
                The title should be concise - with no preamble, relevant, and capture the essence of this Conversation: \n{conversation}.\n\n
                return only the title.
            """
        
        _client = self._summarization_profile['client']
        _provider = self._summarization_profile['provider']
        _model = self._summarization_profile['model']

        def google_generated_title():
            try:
                response = _client.models.generate_content(
                    model=_model,
                    contents=f"{title_profile}\n{instructions}"
                )
                title = response.text.strip().lower()
                return title
            except Exception as e:
                return f"Error!"

        def gpt_models_latest_generated_title(reasoning_effort = "minimal", verbosity = "low"):
            try:                 
                args = set_args(
                    model=_model,
                    instructions=title_profile,
                    input=instructions,
                    reasoning_effort=reasoning_effort,
                    verbosity=verbosity,
                )
            
                resp = _client.responses.create(**args)
                title = _out(resp).strip().lower()
                return title if title else "none"
            except Exception as e:
                return f"Error!"

        def openai_sdk_generated_title():     
            prompt = [
                { "role": "system", "content": title_profile }, 
                { "role": "user", "content": instructions },
            ]

            try:
                response = _client.chat.completions.create(
                    model=_model,
                    messages=prompt,
                    temperature=0,
                    max_tokens=50
                ) 
                title = response.choices[0].message.content.strip().lower()
                return title if title else ""
            except Exception as e:
                return f"Error!"

        if _provider == "google":
            title = google_generated_title()
        elif _model in self.gpt_models_latest():
            title = gpt_models_latest_generated_title()
        else:
            title = openai_sdk_generated_title()
        return title


    def process_query(self, query, context, history, stream=False):
        
        if not self._chat_profile:
            chat_profile = _prof.get_profile("chat") or _prof.get_profile("admin")
            if not chat_profile:
                self.error("Error: check your profiles setup")
                return None
            
            self._chat_profile = chat_profile
            self._chat_profile['client'] = _prof.get_client(chat_profile) 
        
        google_prompt = f"""
                    {self.prompt_profile}\n\n
                    {self.prompt_instructions}\n\n 
                    Question: {query}\n
                    Context: {context}\n
                    History: {history}
                """
        
        openai_sdk_prompt = [
                {"role": "system", "content": self.prompt_profile},
                {
                    "role": "user", 
                    "content": f"""{self.prompt_instructions}\n\n
                                    Generate response to this query: {query}\n
                                    based on this context:\n{context}\n
                                    and history:\n{history}\n\n"""
                },
            ]

        _client = self._chat_profile['client']
        _provider = self._chat_profile['provider']
        _model = self._chat_profile['model']

        def google_process_query():
            response = _client.models.generate_content(
                model=_model,
                contents=google_prompt
            )
            answer = response.text
            return answer

        def gpt_models_latest_process_query(previous_id: str | None, reasoning_effort = "minimal", verbosity = "low"):
            """
            Returns (answer_text, new_response_id)
            """
            # Prepare the prompt with conversation history and context
            input = (
                f"{self.prompt_instructions}\n\n"
                f"Generate a response to this query:\n{query}\n"
                f"based on the given context:\n{context}\n\n"
                f"(Use conversation continuity if available.)"
            )

            sid = self.get_session_id()
            prev_id = self._gpt_models_latest_prev_resp_ids.get(sid)
            
            args = set_args(
                model=_model,
                instructions=self.prompt_profile,
                input=input,
                previous_id=prev_id,
                store=True,
                reasoning_effort=reasoning_effort,
                verbosity=verbosity
            )
            try:
                if stream:
                    parts = []
                    with _client.responses.stream(args) as s:
                        for event in s:
                            if event.type == "response.output_text.delta":
                                delta = event.delta
                                if not delta:
                                    continue
                                parts.append(delta)
                    
                            elif event.type == "response.error":
                                raise RuntimeError(str(event.error))

                        final = s.get_final_response()                      
                        answer = _out(final) or "".join(parts)   # Prefer server’s consolidated text when present
                        if getattr(final, "id", None):
                            self._gpt_models_latest_prev_resp_ids[sid] = final.id                     
                        self.stream_write("[END]")  # Close the SSE
                        return answer

                # Non-stream path
                resp = _client.responses.create(**args)
                answer = _out(resp)
                if getattr(resp, "id", None):
                    self._gpt_models_latest_prev_resp_ids[sid] = resp.id
                return answer

            except Exception as e:
                return f"Error: {type(e).__name__}: {e}"
        
        def openai_sdk_process_query():
        
            try:
                response = _client.chat.completions.create(
                    model=_model,
                    messages=openai_sdk_prompt,
                stream=False,
                )

                if stream:
                    # -------- token streaming --------
                    parts = []
                    for chunk in response:
                        token = getattr(chunk.choices[0].delta, "content", "")
                        if not token:
                            continue
                        parts.append(token)
                        self.stream_write(token)    

                    self.stream_write("[END]")   # close the SSE bubble  
                    answer = "".join(parts)          
                    return answer      
                else:
                    # -------- one-shot buffered --------
                    answer = response.choices[0].message.content .strip() 
                    return answer
            except Exception as e:
                return f"Error: {str(e)}"

        if _provider == "google":
            return google_process_query()
        elif _model in self.gpt_models_latest():
            return gpt_models_latest_process_query(self._gpt_models_latest_prev_resp_ids.get(self.get_session_id()))
        else:
            return openai_sdk_process_query()


    def ai_generate_code(self, question, df):
    
        if not self._coding_profile:
            coding_profile = _prof.get_profile('coding')  or  _prof.get_profile('admin')
            if not coding_profile:
                return None
            self._coding_profile = coding_profile
            self._coding_profile['client'] = _prof.get_client(coding_profile)

        _client = self._coding_profile['client'] 
        _provider = self._coding_profile['provider']
        _model = self._coding_profile['model']

        context = f"Columns: {list(df.columns)}\n\nDtypes: {df.dtypes.astype(str).to_dict()}\n\n"
        ai_profile = f"""You are an expert Python coder, engineer, data analyst. You study thoroughly a given dataframe (`df`), a given question, and a given Context to provide accurate and efficient code solutions: visualisations, tables, and commentaries in plain texts, as required."""

        instructions = f"""
            Write clean, working Python code that answers the question below. 
            DO NOT explain, just output the code only (Add overview comment or text at the bottom)
            Question: {question}\n
            Context: {context}\n\n
            Output only the working code needed. Assume df is already defined.
            Produce at least one visible result: (syntaxmatrix.display.show(), display(), plt.show()).
        """

        def google_generate_code():
            response = _client.models.generate_content(
                model=_model, 
                contents=f"{ai_profile}\n\n{instructions}"
            )
            return response.text

        def gpt_models_latest_generate_code(reasoning_effort = "medium", verbosity = "medium"):
            try:                 
                args = set_args(
                    model=_model,
                    instructions=ai_profile,
                    input=instructions,
                    reasoning_effort=reasoning_effort,
                    verbosity=verbosity,
                )
            
                resp = _client.responses.create(**args)
                code = _out(resp)
                return code
            except Exception as e:
                return f"Error!"
        

        def openai_sdk_generate_code():
            try:
                response = _client.chat.completions.create(
                    model=_model,
                    messages=[
                        {"role": "system", "content": ai_profile},
                        {"role": "user", "content": instructions},
                        ],
                    temperature=0.0,
                    max_tokens=2048,
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Error!"

        if _provider == 'google':
            code = google_generate_code()
        elif _model in self.gpt_models_latest():
            code = gpt_models_latest_generate_code()
        else:
            code = openai_sdk_generate_code()
        
        if code:
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()

            code = strip_describe_slice(code)
            code = drop_bad_classification_metrics(code, df)
            return code.strip()
    

    def run(self):
        url = f"http://{self.host}:{self.port}/"
        webbrowser.open(url)
        self.app.run(host=self.host, port=self.port, debug=False)
    