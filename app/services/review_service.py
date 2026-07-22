from app.prompts.review_prompt import build_review_prompt
from app.services.llm_service import generate


def review_code(code: str, language: str) -> str:

    system_prompt, user_prompt = build_review_prompt(
        code,
        language
    )

    return generate(
        system_prompt,
        user_prompt
    )