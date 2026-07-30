from pydantic import BaseModel


class ReviewResult(BaseModel):
    summary: str
    strengths: list[str]
    issues: list[str]
    suggestions: list[str]
    verdict: str


class ReviewResultResponse(ReviewResult):
    """
    Same shape as ReviewResult, plus review_run_id -- lets the frontend
    make a follow-up call to GET /review-runs/{review_run_id}/items to
    fetch individual item IDs for the approve/reject UI, without
    restructuring ReviewResult itself (which would ripple into every
    existing test and the current frontend rendering).
    """

    review_run_id: str
