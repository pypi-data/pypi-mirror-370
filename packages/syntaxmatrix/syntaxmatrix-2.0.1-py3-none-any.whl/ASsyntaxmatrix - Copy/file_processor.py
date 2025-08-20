# syntaxmatrix/file_processor.py
import os
import glob
import time
from PyPDF2 import PdfReader
from .vectorizer import embed_text 

from .vector_db import insert_embedding, delete_embeddings_for_file, add_pdf_chunk, delete_pdf_chunks

def extract_pdf_text(pdf_path: str) -> str:
    """
    Extracts text from a PDF file using PyPDF2.
    """
    text = []
    with open(pdf_path, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
    return "\n".join(text)


def recursive_text_split(text: str,
                         max_length: int = 2500,
                         min_length: int = 300,
                         separators: list = [". ", "\n", " ", ""]) -> list:
    """
    Recursively splits text into chunks <= max_length using preferred separators.
    """
    text = text.strip()
    if len(text) <= max_length:
        return [text]

    split_index = -1
    for sep in separators:
        idx = text.rfind(sep, 0, max_length)
        if idx >= min_length:
            split_index = idx + len(sep)
            break

    if split_index == -1:
        split_index = max_length

    head = text[:split_index].strip()
    tail = text[split_index:].strip()
    return [head] + recursive_text_split(tail, max_length, min_length, separators)


def process_admin_pdf_files(
    directory: str,
    clear_existing: bool = True,
    max_chunk_size: int = 2500,
    min_chunk_size: int = 300
) -> dict:
    result = {}
    pattern = os.path.join(directory, "*.pdf")
    pdf_paths = glob.glob(pattern)

    for pdf_path in pdf_paths:
        file_name = os.path.basename(pdf_path)
        if clear_existing:
            delete_pdf_chunks(file_name)
            delete_embeddings_for_file(file_name)

        text = extract_pdf_text(pdf_path)
        cleaned_text = " ".join(text.split())
        chunks = recursive_text_split(
            cleaned_text, max_length=max_chunk_size, min_length=min_chunk_size
        )
        
        for idx, chunk in enumerate(chunks):
            add_pdf_chunk(file_name, idx, chunk)

            # generate & store its embedding
            emb = embed_text(chunk)
            insert_embedding(
                 metadata={"file_name":file_name, "chunk_index":idx},
                vector=emb
            )
        # Store the chunks in the result dictionary
        result[file_name] = chunks
    return result

def remove_admin_pdf_file(directory: str, file_name: str):
    """
    Delete a system PDF and its stored chunks.
    """
    path = os.path.join(directory, file_name)
    if os.path.exists(path):
        os.remove(path)
    delete_pdf_chunks(file_name)
    delete_embeddings_for_file(file_name)
