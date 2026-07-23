from pydantic import BaseModel

from app.schemas.review import ReviewResult


class LLMResponse(BaseModel):
    content: ReviewResult
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency: float
