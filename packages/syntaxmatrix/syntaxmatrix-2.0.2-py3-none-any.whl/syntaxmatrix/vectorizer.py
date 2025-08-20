import os
import openai
from openai import OpenAI
from . import llm_store as _llms
from . import profiles as _prof
from typing import List
import itertools
from syntaxmatrix import llm_store as _llms
from dotenv import load_dotenv


def embed_text(text: str):

    embed = _llms.load_embed_model()
    model = embed["model"]
    api_key = embed["api_key"]
    embed_client = OpenAI(api_key=api_key)

    try:
        resp = embed_client.embeddings.create(
            model=model,
            input=text
        )
        return resp.data[0].embedding
    except Exception as e:
        print(f"[vectorizer] embed_text failed: {e}")
        # return None so callers can check and bail out
        return "Vector error!"
    
    
def get_embeddings_in_batches(texts:List[str], batch_size=100) -> List[List[float]]: 

    embed = _llms.load_embed_model()
    model = embed["model"]
    api_key = embed["api_key"]
    embed_client = OpenAI(api_key=api_key)

    embed_client = OpenAI(api_key=api_key)
    results = []
    for batch in itertools.zip_longest(*(iter(texts),) * batch_size):
        batch = [t for t in batch if t is not None]
        resp = embed_client.embeddings.create(
            model=model, 
            input=batch
        )
        results.extend([r.embedding for r in resp.data])
    return results