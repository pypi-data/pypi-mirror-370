
# SyntaxMatrix: Full-Stack Plug-and-Play AI Assistant Micro-Framework

<!-- LOGO PLACEHOLDER -->
<p align="center">
  <img src="logo.png" alt="SyntaxMatrix Logo" width="150"/><br>
  <em>Add your project logo above. Recommended size: 150x150px.</em>
</p>

---

## Introduction

**SyntaxMatrix** is a full-stack, plug-and-play micro-framework that enables AI developers, educators, researchers, and enterprise teams to build, deploy, and manage advanced AI assistant applications with minimal friction.

Designed to abstract away heavy infrastructure and data engineering, SyntaxMatrix allows you to focus on your project logic—while providing powerful out-of-the-box features like persistent page/content management, built-in Retrieval-Augmented Generation (RAG) capabilities, vector search, analytics dashboard, and more.

SyntaxMatrix is:
- **Modular and extensible**: Use it as a drop-in UI and logic layer in any Python-based AI app.
- **Enterprise-ready**: Supports multi-user admin panel, dataset upload, in-memory and persistent vector search, and fine-grained CRUD controls.
- **DevOps-friendly**: Easily deploy on **GCP, Docker, Gunicorn**, or your own local server.
- **Zero-boilerplate for analysts**: Upload your data and immediately ask questions or request ML analytics—no code changes required.
- **Open to rapid prototyping**: Perfect for demo projects, classroom tools, and production-grade LLM-powered assistants.

**Core Use Cases:**
- Build custom AI chat assistants with advanced RAG capabilities
- Deploy internal knowledge tools for your company, with domain PDF/document search out of the box
- Enable analysts to upload datasets and perform instant ML and data analytics
- Teach students or teams how to leverage LLMs, vector databases, and prompt engineering
- Prototype or productionize multi-agent chat, classroom kits, or custom analytics dashboards

**Audience:**  
AI developers, educators, ML/DS researchers, enterprise engineering teams, and anyone who needs a powerful, extensible, and easy-to-integrate AI assistant platform.

---

### At a Glance

- **Plug-and-play installation:**  
  ```bash
  pip install syntaxmatrix
  # For analytics, ML, and advanced dashboard features:
  pip install "syntaxmatrix[analysis]"
  ```
- **Full-stack:**  
  Built-in UI, backend, vector storage, admin panel, and analytics dashboard
- **Seamless document & data ingestion:**  
  Persist company/domain PDFs, upload user files for per-session RAG, manage and search both
- **Ready-to-use admin & dashboard:**  
  No setup required for CRUD, uploads, analytics, or page management
- **Developer friendly:**  
  Extend with your own widgets, handlers, and ML logic as needed
- **Deploy anywhere:**  
  GCP, Docker, Gunicorn, or local
- **Future-ready:**  
  Multi-agent chat, classroom-ready kits, and streaming responses on the roadmap

---

## 2. SyntaxMatrix UI Overview

Below are the primary interfaces included out-of-the-box with SyntaxMatrix.  
**Replace the image files with your own in the README repo once available.**

### Main Chat Page

![Main Page Screenshot](main_page.png)  
*Hint: This screenshot should showcase the default landing/chat interface: user input box, chat history, and file uploader (PDF). Show a few example queries, a PDF upload, and both bot/user chat bubbles.*

### Admin Panel

![Admin Panel Screenshot](admin_panel.png)  
*Hint: Show the admin interface with options for creating/editing pages, uploading company/domain documents, and performing CRUD operations. Demonstrate file upload for company vectors (PDFs), editing page titles/content, and managing company data.*

### Analytics Dashboard

![Dashboard Screenshot](dashboard.png)  
*Hint: Capture the dashboard after uploading a dataset and running a sample ML/analytics task. Show an analytics summary, generated plots, and a chat interaction where smxAI responds with insights about the data.*

---

## 3. Installation & Setup

**SyntaxMatrix** is distributed via PyPI and can be added to any Python project in seconds.

```bash
pip install syntaxmatrix
# For analytics, ML, and advanced dashboard features:
pip install "syntaxmatrix[analysis]"
```

> **Copy button available in the top right of every code block on GitHub for one-click copy.

### Python & System Requirements

- **Python 3.8+**
- pip (latest recommended)

All dependencies are installed automatically, including Flask, pandas, scikit-learn, numpy, openai, matplotlib, plotly, PyPDF2, and more.

---

## 4. Getting Started: Add SyntaxMatrix to Your Project

SyntaxMatrix is designed to be **plug-and-play**.
**You do not need to copy any demo files.**
Instead, follow these steps to add a full chat UI, RAG, and dashboard to your app:

### A. Minimal Chat Assistant Integration

Below is a minimal example for developers.  
This creates a chat interface that supports:

- User queries and chat history
- Company or domain PDF ingestion/search (auto-managed)
- Per-session document (user) upload and retrieval via in-memory vectorstore (SMIV)
- Streamed LLM responses
- CRUD for pages and admin management—all via built-in UI

```python
import syntaxmatrix as smx
from syntaxmatrix.smiv import SMIV
from syntaxmatrix.vectorizer import embed_text

def get_or_build_smiv_index(sid):
    # User session in-memory vector index (SMIV) for uploaded PDFs
    chunks = smx.get_user_chunks(sid) or []
    count = len(chunks)
    if (sid not in smx._user_indices or smx._user_index_counts.get(sid, -1) != count):
        vecs = [embed_text(txt) for txt in chunks]
        idx = SMIV(len(vecs[0]) if vecs else 1536)
        for i, (txt, vec) in enumerate(zip(chunks, vecs)):
            idx.add(vector=vec, metadata={"chunk_text": txt, "chunk_index": i, "session_id": sid})
        smx._user_indices[sid] = idx
        smx._user_index_counts[sid] = count
    return smx._user_indices[sid]

def create_conversation(stream=False):
    chat_history = smx.get_chat_history()
    sid = smx.get_session_id()
    sources = []

    # Ensure session indices exist
    if not hasattr(smx, "_user_indices"):
        smx._user_indices = {}
        smx._user_index_counts = {}

    smiv_index = get_or_build_smiv_index(sid)
    query, intent = smx.get_text_input_value("user_query")
    query = query.strip()
    if not query:
        return

    if intent == "none":
        context = ""
    else:
        lines = []
        q_vec = embed_text(query)
        if intent in ("user_docs", "both"):
            user_hits = smiv_index.search(q_vec, top_k=3)
            lines.append("\n### Personal Context (user uploads)\n")
            for hit in user_hits:
                text = hit["metadata"]["chunk_text"].strip().replace("\n", " ")
                lines.append(f"- {text}\n")
            sources.append("User uploads")
        if intent in ("system_docs", "both"):
            sys_hits = smx.smpv_search(q_vec, top_k=5)
            lines.append("### System Context (company docs)\n")
            for hit in sys_hits:
                text = hit["chunk_text"].strip().replace("\n", " ")
                lines.append(f"- {text}\n")
            sources.append("Company/domain docs")
        context = "".join(lines)

    conversations = "\n".join([f"{role}: {msg}" for role, msg in chat_history])
    # [Replace with your actual LLM call here]
    answer = smx.process_query(query, conversations, context, stream=stream).strip()

    if sources:
        answer += "<ul style='margin-top:5px;'><strong style='color:blue;font-size:0.7rem;'>Sources: "
        for s in sources:
            answer += f"<li>{s}</li>"
        answer += "</strong></ul>"

    chat_history.append(("User", query))
    chat_history.append(("Bot", answer))
    smx.set_chat_history(chat_history)
    smx.clear_text_input_value("user_query")

# --- Register widgets for chat UI
smx.text_input("user_query", "Enter query:", placeholder="Ask smxAI anything...")
smx.button("submit_query", "Submit", callback=lambda: create_conversation(stream=True))
smx.file_uploader("user_files", "Upload PDF files:", accept_multiple_files=True)

# Optional: Clear chat
def clear_chat():
    smx.clear_chat_history()
smx.button("clear", "Clear", clear_chat)

if __name__ == "__main__":
    smx.run()
```

> **How it works:**  
> - All uploaded PDFs (company/domain) via the Admin Panel are indexed and available to smxAI for search and retrieval—*automatically*.
> - User-uploaded PDFs are indexed *per session* in SMIV; these are ephemeral and cleared on session end.
> - The Admin Panel and page CRUD are built-in and accessible on startup.

---

### B. Enabling the Analytics Dashboard (Automated Data Analysis & ML)

The **Dashboard** is included out-of-the-box.  
Once you run your SyntaxMatrix app, any admin or analyst can upload a CSV dataset via the dashboard and request instant analysis or ML jobs via natural language:

- **No extra code required for dashboard or ML.**
- All plots, distributions, and ML model training are performed *automatically* via the dashboard UI.

**Typical Workflow:**
1. Start your SyntaxMatrix-powered app.
2. Open the dashboard (via UI link).
3. Upload a CSV (e.g., `diabetes_dataset.csv`).
4. Use the chat box or dashboard buttons to request:
    - Data summaries and descriptions
    - Missing value detection/visualization
    - Numeric/categorical feature analysis
    - Correlation, heatmaps, boxplots, outlier detection
    - Target distribution plots
    - Feature-target comparison
    - Automated ML: model training, evaluation, and result plotting
    - Advanced: Clustering, UMAP visualizations, survival analysis (Kaplan-Meier, Cox model), and more

All outputs are returned as formatted tables, markdown, or interactive plots in the dashboard—**no code or Python needed**.

---

### C. (Optional) Custom Analytics / Extending Dashboard

You can extend the dashboard by adding your own widgets and ML jobs using `syntaxmatrix.plottings`.

**Example: Automated Model Training and Confusion Matrix (from analysis.py)**

```python
import syntaxmatrix as smx
import pandas as pd
from syntaxmatrix.plottings import figure
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

def train_and_evaluate_model():
    df = smx.get_uploaded_dataset()
    X = df.drop("target_col", axis=1)
    y = df["target_col"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    fig = figure(figsize=(4, 4))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(ax=fig.gca())
    smx.set_plottings(fig, note=f"Accuracy: {acc:.3f}")

smx.button("train_model", "Train Model", callback=train_and_evaluate_model)
```

> **More advanced examples (pairplots, UMAP, survival analysis) can be found in the main documentation and your analysis.py.**

---

## 5. Core Features & Workflows

### A. Chat Interface & RAG (Retrieval-Augmented Generation) Flow

- **User queries** (chat box)
- **Intent detection** (which sources to use)
- **Semantic search** (company/domain + user PDFs)
- **LLM generation** (with optional source citation)
- **Built-in chat history**

See previous integration code for a full implementation.

---

### B. Admin Panel & Content Management

- **CRUD** for pages (About, Help, etc.)
- **Upload/manage PDFs** (domain knowledge)
- **Branding and theme** options
- **No extra code needed**—start app and access admin panel

---

### C. Vector Storage: Company/Domain vs. User Data

- **Company/domain vectors**: Persistent, in SQLite, available for RAG at all times
- **User (SMIV) vectors**: Ephemeral, per session, in-memory
- **Both managed automatically by SyntaxMatrix**

---

### D. Analytics Dashboard & Automated ML Jobs

- **Upload CSV** via dashboard
- **Auto analysis** (summary, missing values, distributions, correlations, boxplots, etc.)
- **Auto ML** (train/test split, logistic regression, confusion matrix, model accuracy)
- **Advanced analytics** (clustering, survival analysis, UMAP, plotly)

No Python required—just use the dashboard UI!

---

### E. SMIV (In-Memory Vectorstore) for User Docs

- **Session-based RAG** for user-uploaded PDFs
- **Auto chunking, embedding, search**
- **Cleared on session end**

---

### F. Branding, UI Customization, and Theming

```python
smx.set_site_logo("logo.png")
smx.set_site_title("My Company Assistant")
smx.set_user_icon("👤")
smx.set_bot_icon("🤖")
smx.enable_theme_toggle()
smx.set_ui_mode("smx")
```

---

### G. Roadmap & Future Directions

- Multi-agent chat UI (collaborative AI/roles/agents)
- Classroom-ready education kits
- Real-time streaming LLM responses
- Expanded analytics and ML modules
- Integrations with more vector DBs and cloud storage
- Automated scheduled data/ML jobs

---

## 6. Deployment Instructions

### A. Local Development / Testing

```bash
pip install "syntaxmatrix[analysis]"
python your_script.py
```

App at `http://localhost:5000/`.

---

### B. Production Deployment (Gunicorn + Nginx or Reverse Proxy)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 your_script:app
```
*(Export a Flask app with `app = smx.get_flask_app()`)*

---

### C. Docker Deployment

**Dockerfile example:**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && \
    pip install "syntaxmatrix[analysis]"
EXPOSE 5000
CMD ["python", "your_script.py"]
```

**Build & run:**

```bash
docker build -t syntaxmatrix-app .
docker run -d -p 5000:5000 --name smx syntaxmatrix-app
```

---

### D. GCP Deployment (with Docker)

1. **Push your Docker image to GCP Artifact/Container Registry:**

    ```bash
    docker tag syntaxmatrix-app gcr.io/your-gcp-project/syntaxmatrix-app:latest
    docker push gcr.io/your-gcp-project/syntaxmatrix-app:latest
    ```

2. **Deploy to Google Cloud Run (recommended).**

---

### E. Environment Variables & Configuration Tips

- **PORT**: `smx.run(port=XXXX)`
- **Persistence**: Mount volume or use cloud storage for `/uploads` and SQLite DBs
- **Security**: Set env vars for sensitive keys
- **Scaling**: Use Cloud Run autoscaling or Gunicorn workers

---

### F. Troubleshooting

- **Port in use:** Change port in your script or Dockerfile
- **Missing deps:** Use `analysis` extra
- **File upload:** Ensure `/uploads` is writable

---

## 7. Extending & Customizing SyntaxMatrix

- **Register custom widgets** (input, button, dropdown, uploader)
- **Custom analytics/ML routines** with `syntaxmatrix.plottings`
- **Custom page CRUD via admin panel**
- **Branding and UI theming**

See earlier code examples.

---

## 8. Contributing

SyntaxMatrix welcomes contributions! Fork, branch, and submit PRs for features, bugfixes, docs, or analytics/ML routines.

- [GitHub Issues](https://github.com/bobganti/SyntaxMatrix/issues)
- [GitHub Discussions](https://github.com/bobganti/SyntaxMatrix/discussions)

---

## 9. Support & Contact

- **Email:** your-email@example.com *(change as needed)*
- **GitHub Issues/Discussions:** for all public bug reports and feature requests
- **Enterprise support:** contact via email or GitHub

---

## 10. License

MIT License

```text
MIT License
Copyright (c) 2025 Bob Nti
Permission is hereby granted, free of charge, to any person obtaining a copy...
[Full MIT license text here]
```

---

## 11. Project Links

- [PyPI: syntaxmatrix](https://pypi.org/project/syntaxmatrix)
- [GitHub](https://github.com/bobganti/SyntaxMatrix)
- [Docs (Coming soon)](https://syntaxmatrix.ai)

---

## 12. Logo and Screenshots

- **Logo:** Replace the top placeholder with your logo (e.g., `logo.png`)
- **Screenshots:** Add real screenshots in each section

---

## 13. Roadmap & Acknowledgements

See roadmap above. Thanks to all contributors and users!

---
