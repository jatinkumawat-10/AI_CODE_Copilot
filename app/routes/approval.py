import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.review import ReviewItem
from app.schemas.approval import ApprovalStatusUpdate
from app.services.approval_service import InvalidTransitionError, validate_transition
from app.utils.logger import logger

router = APIRouter()


@router.patch("/review-items/{item_id}/status")
def update_approval_status(
    item_id: uuid.UUID,
    update: ApprovalStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    Transition a review item's approval_status (proposed -> approved ->
    applied, or proposed -> rejected). Validates the transition before
    writing anything -- an invalid transition (e.g. proposed -> applied
    directly) returns 409, not a silently-accepted bad state.
    """
    item = db.query(ReviewItem).filter_by(id=item_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Review item not found")

    try:
        validate_transition(item.approval_status, update.status)
    except InvalidTransitionError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    item.approval_status = update.status
    db.commit()
    db.refresh(item)

    logger.info(f"Review item {item_id} transitioned to '{update.status}'")

    return {
        "id": str(item.id),
        "kind": item.kind,
        "content": item.content,
        "approval_status": item.approval_status,
    }
