from knowledge.services.retriever import retrieve_relevant_chunks, RetrievalError

# Re-export so chatbot_service.py doesn't need to import from knowledge directly
__all__ = ["get_context_for_question", "RetrievalError"]


def get_context_for_question(question: str, top_k: int = 4) -> list[dict]:
    return retrieve_relevant_chunks(question, top_k=top_k)