from django.conf import settings
from .loader import load_markdown_file, clean_text
from .chunker import split_into_chunks
from .embedder import embed_texts
from .vector_store import build_index


def load_and_chunk_knowledge_base() -> list:
    file_path = settings.KNOWLEDGE_BASE_DIR / "company_knowledge.md"
    raw_text = load_markdown_file(file_path)
    cleaned = clean_text(raw_text)
    chunks = split_into_chunks(cleaned)
    return chunks


def embed_chunks(chunks: list) -> list[dict]:
    texts = [chunk.text for chunk in chunks]
    vectors = embed_texts(texts)

    embedded = []
    for chunk, vector in zip(chunks, vectors):
        embedded.append({
            "heading": chunk.heading,
            "content": chunk.content,
            "text": chunk.text,
            "embedding": vector,
        })
    return embedded


def run_full_ingestion() -> int:
    """
    Full pipeline: load → clean → chunk → embed → build FAISS index.
    Returns the number of chunks indexed. Run this whenever the
    knowledge base file changes.
    """
    chunks = load_and_chunk_knowledge_base()
    embedded = embed_chunks(chunks)
    build_index(embedded)
    return len(embedded)