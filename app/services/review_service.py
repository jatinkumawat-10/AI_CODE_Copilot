from app.prompts.review_prompt import build_review_prompt
from app.schemas.review import ReviewResult
from app.services.llm_service import generate
from app.utils.logger import logger


def review_code(code: str, language: str) -> ReviewResult:
    """
    Review source code using the configured LLM.
    """

    logger.info(f"Building review prompt for language: {language}")

    system_prompt, user_prompt = build_review_prompt(
        code=code,
        language=language,
    )

    logger.info("Sending review request to LLM")

    llm_response = generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    logger.info(f"""
Review generated successfully.

Model: {llm_response.model}
Latency: {llm_response.latency:.2f}s
Prompt Tokens: {llm_response.prompt_tokens}
Completion Tokens: {llm_response.completion_tokens}
Total Tokens: {llm_response.total_tokens}
""")

    return llm_response.content
