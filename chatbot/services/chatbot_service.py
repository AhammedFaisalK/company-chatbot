from .rag_service import get_context_for_question, RetrievalError
from .prompt_service import build_system_prompt
from .llm_service import generate_response, LLMServiceError
from .history_service import get_recent_history


def get_bot_response(user_question: str, conversation=None) -> str:
    context_chunks = get_context_for_question(user_question)  # may raise RetrievalError
    system_prompt = build_system_prompt(context_chunks)

    messages = [{"role": "system", "content": system_prompt}]

    if conversation is not None:
        history = get_recent_history(conversation)
        messages.extend(history)

    messages.append({"role": "user", "content": user_question})

    answer = generate_response(messages)  # may raise LLMServiceError
    return answer