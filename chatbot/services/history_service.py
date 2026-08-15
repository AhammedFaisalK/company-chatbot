from ..models import Conversation, Message

MAX_HISTORY_MESSAGES = 6  # last 3 user/assistant pairs


def get_recent_history(conversation: Conversation, limit: int = MAX_HISTORY_MESSAGES) -> list[dict]:
    """
    Returns the most recent messages in a conversation, formatted as
    {"role": ..., "content": ...} dicts ready to hand to the LLM.
    Ordered oldest-to-newest (the order the LLM expects).
    """
    recent = (
        conversation.messages
        .order_by("-created_at")[:limit]
    )
    # recent is newest-first; reverse it so the LLM sees oldest-first
    ordered = list(reversed(recent))

    return [{"role": m.role, "content": m.content} for m in ordered]