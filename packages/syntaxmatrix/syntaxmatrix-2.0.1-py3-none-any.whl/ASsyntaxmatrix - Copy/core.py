from __future__ import annotations
import os, webbrowser, uuid, secrets

from flask import Flask, session, request, has_request_context
from .history_store import SQLHistoryStore as Store, PersistentHistoryStore as _Store
from collections import OrderedDict
from syntaxmatrix.llm_store import save_embed_model, load_embed_model, delete_embed_key
from . import db, routes
from .themes import DEFAULT_THEMES
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
        self.theme_toggle_enabled = False
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

        self._chat_profile = None
        self._code_profile = None
        self._sentiment_profile = None
        self._analytics_profile = None
        self._summary_profile = None

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
        if mode not in ["default", "card", "bubble", "smx"]:
            raise ValueError("UI mode must be one of: 'default', 'card', 'bubble', 'smx'.")
        self.ui_mode = mode


    @staticmethod
    def list_ui_modes():
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


    def get_text_input_value(self, key, default=""):
        q = session.get(key, default)

        intent = self.sentiment(q)
        if not intent:
            self.error("ERROR: There is no LLM profile setup yet.")
            return None
        return q, intent


    def sentiment(self, query: str) -> str:
        
        if not self._sentiment_profile:
            sentiment_profile = _prof.get_profile('sentiment') or _prof.get_profile('chat')
            if not sentiment_profile:
                return
             
            self._sentiment_profile = sentiment_profile
            self._sentiment_profile['client'] = _prof.get_client(sentiment_profile)     

        exp = [
            { "query":"Hi there!", "intent": "none" },
            { "query": "Summarize my uploaded marketing deck.", "intent": "user_doc" },
            { "query": "What’s the SLA for our email-delivery service?", "intent": "system_docs" },
            { "query": "What are my colleaues' surnames, in the contact list I sent you?", "intent": "hybrid" }
        ]
        
        instructions = f"""
                        You are an intent router. Classify questions into exactly one of the following intents: 
                            i. `base`
                            ii. `user_docs`
                            iii. `system_docs`

                        1. Return `base` if the query is a greeting or an opening to a casual chat.

                        2. Return `user_docs` if the user is asking about content the user personally uploaded.

                        3. Return `system_docs` if the user is asking about factual or technical details 
                        about your company and requires that you to look into the system or company files.  
                        
                        Follow the above instructions and criteria and determine the intent of the following Query:\n{query}\n\n 
                        See the Few-shot exmples below and learn from them.
                         
                        Few-shot £xamples below.\n\n{exp}
                    """

        prompt = {
                    "role": "system",
                    "content": instructions
                },
                        
        def google_classify_query():
            response = self._sentiment_profile['client'].models.generate_content(
                model=self._sentiment_profile['model'],
                contents=instructions
            )
            return response.text

        def openai_sdk_classify_query():
            response = self._sentiment_profile['client'].chat.completions.create(
                model=self._sentiment_profile['model'],
                messages=prompt,
                temperature=0,
                max_tokens=100
            )
            intent = response.choices[0].message.content.strip().lower()
            return intent

        if self._sentiment_profile['provider'] == "google":
            intent = google_classify_query()
            return intent
        else:
            intent = openai_sdk_classify_query()
            return intent


    def generate_contextual_title(self, chat_history):
        
        if not self._summary_profile:
            summary_profile = _prof.get_profile('summary') or _prof.get_profile('chat') or {}
            if not summary_profile:
                return 
            
            self._summary_profile = summary_profile
            self._summary_profile['client'] = _prof.get_client(summary_profile)

        conversation = "\n".join([f"{role}: {msg}" for role, msg in chat_history])
        instructions = f"""
                PROMPT_PROFILE: You are a title generator. 
                INSTRUCTIONS: Generate a contextual title (5 short words max) from the given Conversation History 
                The title should be concise - with no preamble, relevant, and capture the essence of this Conversation: \n{conversation}.\n\n
                return only the title.
            """
        client = self._summary_profile['client']
        model = self._summary_profile['model']
        
        def google_generated_title():
            response = client.models.generate_content(
                model=model,
                contents=instructions
            )
            return response.text
        
        def openai_sdk_generated_title():     
            prompt = [
                {
                    "role": "system",
                    "content": instructions
                },            
            ]
        
            response = client.chat.completions.create(
                model=model,
                messages=prompt,
                temperature=0,
                max_tokens=50
            )
        
            title = response.choices[0].message.content.strip().lower()
            return title    

        if self._summary_profile['provider'] == "google":
            title = google_generated_title()
        else:
            title = openai_sdk_generated_title()
        return title


    def process_query(self, query, context, history, stream=False):
        
        if not self._chat_profile:
            chat_profile = _prof.get_profile("chat")
            if not chat_profile:
                self.error("Error: setup a chat profile")
                return
            
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
                {"role": "user",   "content": self.prompt_instructions},
                {"role": "assistant", "content": f"Query: {query}\n\nContext1: {context}\n\n"
                                                    f"History: {history}\n\nAnswer: "}
            ]

        def google_process_query():
            response = self._chat_profile['client'].models.generate_content(
                model=self._chat_profile['model'],
                contents=google_prompt
            )
            answer = response.text
            return answer
        
        def openai_sdk_process_query():
        
            try:
                response = self._chat_profile['client'].chat.completions.create(
                    model=self._chat_profile['model'],
                    messages=openai_sdk_prompt,
                    temperature=0.1,
                    max_tokens=1024,
                    stream=stream
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
                    answer = response.choices[0].message.content  
                    return answer
            except Exception as e:
                return f"Error: {str(e)}"

        if self._chat_profile['provider'] == "google":
            return google_process_query()
        else:
            return openai_sdk_process_query()
        

    def ai_analytics(self, question, df):
    
        if not self._analytics_profile:
            analytics_profile = _prof.get_profile('analytics') or _prof.get_profile('code')  or _prof.get_profile('chat')
            if not analytics_profile:
                return
            
            self._analytics_profile = analytics_profile
            self._analytics_profile['client'] = _prof.get_client(analytics_profile)

        context = f"Columns: {list(df.columns)}\n\nDtypes: {df.dtypes.astype(str).to_dict()}\n\n"
        instructions = f"""
            You are an expert Python data analyst. Given the dataframe `df` with the following Context:\n{context}\n\n
            Write clean, working Python code that answers the question below. 
            DO NOT explain, just output the code only (Add overview comment or text at the bottom)
            Question: {question}\n
            Output only the working code needed. Assume df is already defined.
            Produce at least one visible result: (syntaxmatrix.display.show(), display(), plt.show()).
        """

        def google_generate_code():
            response = self._analytics_profile['client'].models.generate_content(
                model=self._analytics_profile['model'], 
                contents=instructions
            )
            return response.text
        
        def openai_sdk_generate_code():
            response = self._analytics_profile['client'].chat.completions.create(
                model=self._analytics_profile['model'],
                messages=[{"role": "user", "content": instructions}],
                temperature=0.0,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        
        if self._analytics_profile['provider'] == 'google':
            code = google_generate_code()
        else:
            code = openai_sdk_generate_code()

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
    