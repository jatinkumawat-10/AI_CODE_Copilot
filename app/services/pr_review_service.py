from pathlib import Path

from app.db import SessionLocal
from app.services.github_service import get_pr_files, post_pr_comment
from app.services.persistence_service import save_review_run
from app.services.review_service import generate_review
from app.utils.file_handler import EXTENSION_LANGUAGE_MAP
from app.utils.logger import logger


def _detect_language_or_none(filename: str) -> str | None:
    """
    Like file_handler.detect_language(), but returns None for unsupported
    extensions instead of raising -- there's no HTTP request to respond to
    inside a background task, so we skip unsupported files silently rather
    than crash the whole PR review over one unrelated file (e.g. a .md or
    .json file changed in the same PR).
    """
    extension = Path(filename).suffix.lower()
    return EXTENSION_LANGUAGE_MAP.get(extension)


def review_pull_request(owner: str, repo: str, pr_number: int) -> None:
    """
    Public entry point, called from the background task. Wraps the real
    logic in a top-level try/except -- without this, a failure in
    get_pr_files() or post_pr_comment() (outside the per-file loop's own
    try/except) would crash the background task with zero log output,
    indistinguishable from "everything worked, there was just nothing to
    review." FastAPI's BackgroundTasks does not surface exceptions
    anywhere visible by default, so this guarantee has to be explicit.
    """
    try:
        _review_pull_request_impl(owner=owner, repo=repo, pr_number=pr_number)
    except Exception:
        logger.exception(
            f"PR review task failed entirely for {owner}/{repo} PR #{pr_number}"
        )


def _review_pull_request_impl(owner: str, repo: str, pr_number: int) -> None:
    """
    Fetch a PR's changed files, review each supported file's diff patch
    (not the full file -- this mirrors what a human reviewer actually
    looks at on a PR page), and post one combined comment back to the PR.

    Deliberately reviews the diff patch, not the full file content: this
    is a considered choice, not a shortcut -- a PR review should focus on
    what changed, the same way a human reviewer's attention does.
    """
    files = get_pr_files(owner=owner, repo=repo, pr_number=pr_number)
    logger.info(
        f"PR review task started for {owner}/{repo} PR #{pr_number}: "
        f"{len(files)} changed file(s) fetched"
    )

    review_sections = []

    for file in files:
        filename = file["filename"]

        if file.get("status") == "removed":
            continue  # nothing to review in a deleted file

        language = _detect_language_or_none(filename)
        if language is None:
            logger.info(f"Skipping unsupported file type: {filename}")
            continue

        patch = file.get("patch")
        if not patch:
            # GitHub omits "patch" for very large diffs -- nothing to review
            logger.info(f"Skipping {filename}: no patch available (diff too large)")
            continue

        try:
            llm_response = generate_review(code=patch, language=language)
        except Exception:
            logger.exception(f"Review failed for {filename} in PR #{pr_number}")
            continue

        db = SessionLocal()
        try:
            save_review_run(
                db=db,
                code=patch,
                language=language,
                llm_response=llm_response,
                filename=filename,
                pr_owner=owner,
                pr_repo=repo,
                pr_number=pr_number,
            )
        except Exception:
            logger.exception(
                f"Failed to persist review for {filename} in PR #{pr_number}"
            )
        finally:
            db.close()

        review = llm_response.content
        review_sections.append(
            f"### `{filename}`\n\n"
            f"**Summary:** {review.summary}\n\n"
            f"**Issues:**\n"
            + (
                "\n".join(f"- {issue}" for issue in review.issues)
                if review.issues
                else "- None found"
            )
            + f"\n\n**Verdict:** {review.verdict}"
        )

    if not review_sections:
        logger.info(f"No reviewable files in PR #{pr_number}, skipping comment")
        return

    comment_body = "## 🤖 AI Code Review\n\n" + "\n\n---\n\n".join(review_sections)

    post_pr_comment(owner=owner, repo=repo, pr_number=pr_number, body=comment_body)
    logger.info(f"Posted review comment on {owner}/{repo} PR #{pr_number}")
