from app.utils.logger import logger

from app.config import MODEL_NAME
from app.llm.openrouter import client
from app.exceptions import LLMServiceError
import time
from app.schemas.llm import LLMResponse
def generate(system_prompt: str, user_prompt: str) -> str:
    """
    Generate a response from the configured LLM.
    """
    start = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        latency = time.perf_counter() - start
        return LLMResponse(
    content=response.choices[0].message.content,
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
    
    