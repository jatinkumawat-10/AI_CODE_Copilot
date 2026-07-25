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
