class InvalidTransitionError(Exception):
    """Raised when an approval_status transition isn't allowed."""

    pass


# Explicit allow-list of valid transitions. Anything not listed here is
# rejected -- e.g. proposed -> applied directly, or rejected -> approved,
# are both disallowed even though nothing stops you from constructing
# those strings by accident.
VALID_TRANSITIONS: dict[str, set[str]] = {
    "proposed": {"approved", "rejected"},
    "approved": {"applied"},
    "rejected": set(),  # terminal state, no transitions out
    "applied": set(),  # terminal state, no transitions out
}


def validate_transition(current_status: str, new_status: str) -> None:
    """
    Raises InvalidTransitionError if the transition isn't allowed.
    Does nothing (returns None) if it's valid -- callers proceed with the
    actual database update themselves.
    """
    allowed = VALID_TRANSITIONS.get(current_status, set())

    if new_status not in allowed:
        raise InvalidTransitionError(
            f"Cannot transition from '{current_status}' to '{new_status}'. "
            f"Valid transitions from '{current_status}': "
            f"{sorted(allowed) or 'none (terminal state)'}"
        )


def approve_merged_pr_items(db, owner: str, repo: str, pr_number: int) -> int:
    """
    Bulk-transitions all still-'proposed' issue items belonging to a
    merged PR to 'approved'.

    This is a heuristic, not a guarantee: a merged PR means the team
    accepted the code as mergeable, which implicitly accepts whatever
    issues remained flagged -- it does NOT mean each individual issue was
    reviewed or confirmed fixed. A PR can merge with some flagged issues
    fixed, others dismissed, others never looked at at all. Callers
    (and anyone reading approval_status='approved' later) should treat
    this as "the team shipped it anyway," not "this specific issue was
    verified resolved."

    Returns the number of items transitioned, for logging.
    """
    from app.models.review import ReviewItem, ReviewRun

    review_run_ids = (
        db.query(ReviewRun.id)
        .filter_by(pr_owner=owner, pr_repo=repo, pr_number=pr_number)
        .subquery()
    )

    proposed_items = (
        db.query(ReviewItem)
        .filter(
            ReviewItem.review_run_id.in_(review_run_ids),
            ReviewItem.kind == "issue",
            ReviewItem.approval_status == "proposed",
        )
        .all()
    )

    for item in proposed_items:
        item.approval_status = "approved"

    db.commit()

    return len(proposed_items)
