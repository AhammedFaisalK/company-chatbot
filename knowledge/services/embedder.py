from fastembed import TextEmbedding

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"  # 384-dim, ONNX-based, no PyTorch

_model = None


def get_model() -> TextEmbedding:
    """
    Lazily loads the ONNX-based embedding model once and reuses it.
    fastembed uses ONNX Runtime instead of PyTorch — much lighter
    memory footprint, well-suited to memory-constrained environments
    like free-tier hosting.
    """
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embeds a batch of texts locally via ONNX Runtime, no API call,
    no cost, no PyTorch. Returns one vector (list of floats) per
    input text, in order.
    """
    if not texts:
        return []

    model = get_model()
    # fastembed's .embed() returns a generator of numpy arrays
    vectors = list(model.embed(texts))
    return [vector.tolist() for vector in vectors]


def embed_text(text: str) -> list[float]:
    """Convenience wrapper for embedding a single string (e.g. a user question)."""
    return embed_texts([text])[0]