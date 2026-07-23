from pydantic import BaseModel


class ReviewResult(BaseModel):
    summary: str
    strengths: list[str]
    issues: list[str]
    suggestions: list[str]
    verdict: str
