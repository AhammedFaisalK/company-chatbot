from django.conf import settings
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, AuthenticationError

_client = None


def get_client() -> OpenAI:
    """
    Lazily creates a single shared client pointed at Grok's
    OpenAI-compatible endpoint.
    """
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_API_BASE_URL,
        )
    return _client


class LLMServiceError(Exception):
    """Raised when the LLM call fails in a way the caller should handle."""


def generate_response(messages: list[dict], temperature: float = 0.3) -> str:
    """
    Sends a list of chat messages (system/user/assistant turns) to Grok
    and returns the generated text.

    `messages` follows the standard format:
        [{"role": "system", "content": "..."},
         {"role": "user", "content": "..."}]

    Low temperature (0.3) keeps answers consistent and grounded rather
    than creative — appropriate for a support bot.
    """
    client = get_client()

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=500,
            timeout=20,
        )
    except AuthenticationError as e:
        raise LLMServiceError("Invalid or missing LLM API key.") from e
    except RateLimitError as e:
        raise LLMServiceError("LLM API rate limit or quota exceeded.") from e
    except APITimeoutError as e:
        raise LLMServiceError("LLM API request timed out.") from e
    except APIError as e:
        raise LLMServiceError(f"LLM API error: {e}") from e

    return response.choices[0].message.content