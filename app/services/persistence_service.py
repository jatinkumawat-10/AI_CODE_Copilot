from sqlalchemy.orm import Session

from app.models.review import ReviewItem, ReviewRun
from app.schemas.llm import LLMResponse


def save_review_run(
    db: Session,
    code: str,
    language: str,
    llm_response: LLMResponse,
    filename: str | None = None,
    pr_owner: str | None = None,
    pr_repo: str | None = None,
    pr_number: int | None = None,
) -> ReviewRun:
    """
    Persist one review run and its strengths/issues/suggestions as
    ReviewItem rows. Takes the full LLMResponse (not just ReviewResult) so
    model/token/latency observability data — already computed in
    llm_service.py, previously only logged — gets stored.

    pr_owner/pr_repo/pr_number are only passed by the webhook-triggered
    path (pr_review_service.py); manual /review calls leave them None.
    """
    review = llm_response.content

    review_run = ReviewRun(
        filename=filename,
        language=language,
        code=code,
        summary=review.summary,
        verdict=review.verdict,
        model=llm_response.model,
        prompt_tokens=llm_response.prompt_tokens,
        completion_tokens=llm_response.completion_tokens,
        total_tokens=llm_response.total_tokens,
        latency_seconds=llm_response.latency,
        pr_owner=pr_owner,
        pr_repo=pr_repo,
        pr_number=pr_number,
    )

    for strength in review.strengths:
        review_run.items.append(ReviewItem(kind="strength", content=strength))
    for issue in review.issues:
        review_run.items.append(ReviewItem(kind="issue", content=issue))
    for suggestion in review.suggestions:
        review_run.items.append(ReviewItem(kind="suggestion", content=suggestion))

    db.add(review_run)
    db.commit()
    db.refresh(review_run)

    return review_run
