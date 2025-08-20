# syntaxmatrix/bootstrap.py

from syntaxmatrix.llm_store import list_models, add_model

def seed_default_models():
    """
    If the catalog is empty, populate it with
    large/medium/small variants
    (and only OpenAI for embeddings).
    """
    if list_models():
        return  

    defaults = [
        ("openai", "gpt-4o", "large"),
        ("openai", "gpt-4o-mini", "medium"),
        ("openai", "gpt-4.1-nano", "small"),
        ("google", "gemini-2.5-pro", "large"),
        ("google", "gemini-2.5-chat", "medium"),
        ("google", "gemma-gemma-3n-e4b-it", "small"),
    ]

    # Only OpenAI embeddings
    embedding = [("openai", "text-embedding-3-small", "embedding")]

    for provider, model, purpose in defaults + embedding:
        add_model(provider, model, purpose)
