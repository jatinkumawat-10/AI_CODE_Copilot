from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.webhook_event import ProcessedWebhookEvent
from app.services.approval_service import approve_merged_pr_items
from app.services.pr_review_service import review_pull_request
from app.utils.github_signature import verify_github_signature
from app.utils.logger import logger

router = APIRouter()


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    """
    Receives GitHub webhook events. Verifies the payload signature before
    trusting anything in it, then handles two kinds of pull_request
    events:

    - closed+merged=true: bulk-approves all still-'proposed' issue items
      belonging to that PR (see approve_merged_pr_items's docstring for
      why this is a heuristic, not a guarantee, of individual review).
    - opened/synchronize: triggers a review as a background task --
      GitHub expects a response within ~10s and our reviews have
      measured up to 79s, so the review must not block this response.

    Any other pull_request action is acknowledged and ignored.
    """
    raw_body = await request.body()

    if not verify_github_signature(raw_body, x_hub_signature_256):
        logger.warning("Rejected webhook: invalid signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    if x_github_event != "pull_request":
        logger.info(f"Ignoring non-pull_request event: {x_github_event}")
        return {"status": "ignored", "reason": "not a pull_request event"}

    payload = await request.json()
    action = payload.get("action")

    pr_number = payload["number"]
    repo_full_name = payload["repository"]["full_name"]
    owner, repo = repo_full_name.split("/")

    if action == "closed" and payload["pull_request"].get("merged") is True:
        approved_count = approve_merged_pr_items(
            db=db, owner=owner, repo=repo, pr_number=pr_number
        )
        logger.info(
            f"PR merged: {repo_full_name} PR #{pr_number} -- "
            f"auto-approved {approved_count} previously-proposed issue(s). "
            f"Note: this reflects the team accepting the code as mergeable, "
            f"not individual verification of each issue."
        )
        return {"status": "merged", "auto_approved_count": approved_count}

    if action not in ("opened", "synchronize"):
        logger.info(f"Ignoring pull_request action: {action}")
        return {"status": "ignored", "reason": f"action '{action}' not handled"}

    head_sha = payload["pull_request"]["head"]["sha"]

    already_processed = (
        db.query(ProcessedWebhookEvent)
        .filter_by(owner=owner, repo=repo, pr_number=pr_number, head_sha=head_sha)
        .first()
    )
    if already_processed is not None:
        logger.info(
            f"Skipping duplicate delivery: {repo_full_name} PR #{pr_number} "
            f"at commit {head_sha[:8]} already attempted"
        )
        return {"status": "skipped", "reason": "already processed this commit"}

    db.add(
        ProcessedWebhookEvent(
            owner=owner, repo=repo, pr_number=pr_number, head_sha=head_sha
        )
    )
    db.commit()

    logger.info(
        f"Accepted webhook: {repo_full_name} PR #{pr_number}, action={action}, "
        f"commit {head_sha[:8]}"
    )

    background_tasks.add_task(
        review_pull_request, owner=owner, repo=repo, pr_number=pr_number
    )

    return {"status": "accepted", "pr_number": pr_number}
