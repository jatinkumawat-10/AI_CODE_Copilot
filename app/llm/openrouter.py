from openai import OpenAI

from app.config import (
    BASE_URL,
    OPENAI_API_KEY,
)
from app.exceptions import LLMServiceError


def get_client() -> OpenAI:
    """
    Return an initialized OpenRouter client.
    """

    if not OPENAI_API_KEY:
        raise LLMServiceError("OPENAI_API_KEY is not configured.")

    return OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=BASE_URL,
    )
#test