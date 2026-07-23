import json
import time

from app.config import MODEL_NAME
from app.exceptions import LLMServiceError
from app.llm.openrouter import client
from app.schemas.llm import LLMResponse
from app.schemas.review import ReviewResult
from app.utils.logger import logger


def generate(system_prompt: str, user_prompt: str) -> LLMResponse:
    """
    Generate a structured response from the configured LLM.
    """
    start = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        latency = time.perf_counter() - start

        # Raw JSON string returned by the LLM
        content = response.choices[0].message.content

        # Convert JSON string -> Python dict
        review_data = json.loads(content)

        # Validate against Pydantic schema
        review = ReviewResult.model_validate(review_data)

        logger.info(
            f"""
Review generated successfully.

Model: {response.model}
Latency: {latency:.2f}s
Prompt Tokens: {response.usage.prompt_tokens}
Completion Tokens: {response.usage.completion_tokens}
Total Tokens: {response.usage.total_tokens}
"""
        )

        return LLMResponse(
            content=review,
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            latency=latency,
        )

    except Exception as e:
        logger.exception("Failed to generate response from LLM.")

        raise LLMServiceError(
            "Failed to generate AI review."
        ) from e