from .embedder import embed_text
from .vector_store import search


class RetrievalError(Exception):
    """Raised when the knowledge base can't be searched (missing index, corrupted data, etc.)."""


def retrieve_relevant_chunks(question: str, top_k: int = 4) -> list[dict]:
    """
    Given a user's question, embeds it and returns the top_k most
    relevant knowledge-base chunks. Raises RetrievalError if the
    vector index is missing or search otherwise fails.
    """
    try:
        query_embedding = embed_text(question)
        return search(query_embedding, top_k=top_k)
    except FileNotFoundError as e:
        raise RetrievalError(
            "Knowledge base index not found. Run 'python manage.py ingest_knowledge' first."
        ) from e
    except Exception as e:
        raise RetrievalError(f"Vector search failed: {e}") from e