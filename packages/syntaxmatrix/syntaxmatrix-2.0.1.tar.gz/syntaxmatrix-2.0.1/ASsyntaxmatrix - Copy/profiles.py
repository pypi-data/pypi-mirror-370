# syntaxmatrix/profiles.py
from openai import OpenAI
from google import genai

from syntaxmatrix.llm_store import list_profiles, load_profile

# Preload once at import-time
_profiles: dict[str, dict] = {}
for entry in list_profiles():
    prof = load_profile(entry["name"])
    if prof:
        _profiles[entry["purpose"]] = prof


def get_profile(purpose: str) -> dict:
    """
    Return the full profile dict {'provider'=val, 'api_key'=val, 'model'=val} for that purpose (e.g. "chat", "code").
    Returns None if no such profile exists.
    """
    prof = _profiles.get(purpose, None)
    return prof


def get_client(profile):
    provider = profile["provider"].lower()
    api_key = profile["api_key"]

    if provider == "openai":
        return OpenAI(api_key=api_key)
    elif provider == "google":
        # return OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        return  genai.Client(api_key=api_key)
    elif provider == "xai":
        return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    elif provider == "deepseek":
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    elif provider == "moonshotai":
        return OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1")
    