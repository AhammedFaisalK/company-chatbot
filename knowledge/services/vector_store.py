import json
import pickle
from pathlib import Path

import faiss
import numpy as np
from django.conf import settings

INDEX_PATH = settings.BASE_DIR / "knowledge_files" / "vector_index.faiss"
METADATA_PATH = settings.BASE_DIR / "knowledge_files" / "vector_metadata.pkl"


def build_index(embedded_chunks: list[dict]) -> None:
    """
    Builds a FAISS index from embedded chunks and saves it to disk,
    along with a metadata file mapping each vector's position back
    to its original heading/content text.
    """
    if not embedded_chunks:
        raise ValueError("No embedded chunks provided to build_index().")

    dimension = len(embedded_chunks[0]["embedding"])
    index = faiss.IndexFlatL2(dimension)

    vectors = np.array(
        [chunk["embedding"] for chunk in embedded_chunks],
        dtype="float32",
    )
    index.add(vectors)

    faiss.write_index(index, str(INDEX_PATH))

    # Store the human-readable text for each vector, in the same order
    # they were added to the index (FAISS only stores numbers, not text).
    metadata = [
        {"heading": chunk["heading"], "content": chunk["content"], "text": chunk["text"]}
        for chunk in embedded_chunks
    ]
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)


def load_index():
    """Loads the FAISS index and metadata from disk."""
    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Vector index not found. Run the ingestion pipeline first."
        )

    index = faiss.read_index(str(INDEX_PATH))
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata


def search(query_embedding: list[float], top_k: int = 4) -> list[dict]:
    """
    Given a question's embedding, returns the top_k most similar
    chunks (as metadata dicts), ordered from most to least relevant.
    """
    index, metadata = load_index()

    query_vector = np.array([query_embedding], dtype="float32")
    distances, indices = index.search(query_vector, top_k)

    results = []
    for rank, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        chunk_meta = metadata[idx]
        results.append({
            **chunk_meta,
            "distance": float(distances[0][rank]),
        })
    return results