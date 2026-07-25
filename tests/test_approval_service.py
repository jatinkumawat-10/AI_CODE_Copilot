import pytest

from app.services.approval_service import InvalidTransitionError, validate_transition


def test_proposed_to_approved_is_valid():
    validate_transition("proposed", "approved")  # should not raise


def test_proposed_to_rejected_is_valid():
    validate_transition("proposed", "rejected")  # should not raise


def test_approved_to_applied_is_valid():
    validate_transition("approved", "applied")  # should not raise


def test_proposed_to_applied_is_invalid():
    """Cannot skip straight to applied without going through approved."""
    with pytest.raises(InvalidTransitionError):
        validate_transition("proposed", "applied")


def test_rejected_to_approved_is_invalid():
    """Rejected is a terminal state -- cannot reverse the decision."""
    with pytest.raises(InvalidTransitionError):
        validate_transition("rejected", "approved")


def test_applied_to_anything_is_invalid():
    """Applied is a terminal state -- nothing transitions out of it."""
    with pytest.raises(InvalidTransitionError):
        validate_transition("applied", "proposed")


def test_approved_to_rejected_is_invalid():
    """Once approved, cannot go back to rejected -- only forward to applied."""
    with pytest.raises(InvalidTransitionError):
        validate_transition("approved", "rejected")
