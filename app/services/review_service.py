from app.prompts.review_prompt import build_review_prompt
from app.schemas.llm import LLMResponse
from app.schemas.review import ReviewResult
from app.services.llm_service import generate
from app.utils.logger import logger


def generate_review(code: str, language: str) -> LLMResponse:
    """
    Review source code using the configured LLM, returning the full
    LLMResponse (model, token counts, latency, and the parsed ReviewResult).

    This is the real logic; review_code() below is a thin wrapper kept for
    backward compatibility with existing callers/tests that only need the
    ReviewResult content, not the observability metadata.
    """
    logger.info(f"Building review prompt for language: {language}")

    system_prompt, user_prompt = build_review_prompt(
        code=code,
        language=language,
    )

    logger.info("Sending review request to LLM")

    return generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


def review_code(code: str, language: str) -> ReviewResult:
    """
    Review source code using the configured LLM.
    Thin wrapper around generate_review() for callers that only need the
    parsed review content, not the full LLMResponse metadata.
    """
    return generate_review(code=code, language=language).content