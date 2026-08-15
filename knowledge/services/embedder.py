from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model() -> SentenceTransformer:
    """
    Lazily loads the embedding model once and reuses it.
    Loading is the slow part (~1-2 seconds); actual embedding calls
    after that are fast.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embeds a batch of texts locally, no API call, no cost.
    Returns one vector (list of floats) per input text, in order.
    """
    if not texts:
        return []

    model = get_model()
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [vector.tolist() for vector in vectors]


def embed_text(text: str) -> list[float]:
    """Convenience wrapper for embedding a single string (e.g. a user question)."""
    return embed_texts([text])[0]