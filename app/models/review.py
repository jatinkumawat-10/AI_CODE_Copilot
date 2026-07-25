import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ReviewRun(Base):
    """
    One call to the review service. Stores what was reviewed, the model's
    holistic verdict/summary, and observability data (latency, tokens)
    that llm_service.py was already computing but only logging, not
    persisting.
    """

    __tablename__ = "review_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    filename: Mapped[str] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    verdict: Mapped[str] = mapped_column(Text, nullable=False)

    model: Mapped[str] = mapped_column(String, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_seconds: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    items: Mapped[list["ReviewItem"]] = relationship(
        back_populates="review_run", cascade="all, delete-orphan"
    )


class ReviewItem(Base):
    """
    One entry from a review's strengths, issues, or suggestions list.
    Normalized into one table with a `kind` column rather than three
    separate tables — future approval workflow work only needs to filter
    kind='issue', and adding a column later (severity, approval_status)
    only touches one table, not three.
    """

    __tablename__ = "review_items"
    __table_args__ = (
        CheckConstraint(
            "approval_status IN ('proposed', 'approved', 'rejected', 'applied')",
            name="ck_review_item_approval_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    review_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("review_runs.id"), nullable=False
    )
    kind: Mapped[str] = mapped_column(
        String, nullable=False
    )  # strength|issue|suggestion
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Only meaningful for kind='issue' -- strengths/suggestions don't go
    # through triage, but living in the same table avoids a fourth model
    # just for one extra column on a subset of rows.
    approval_status: Mapped[str] = mapped_column(
        String, nullable=False, default="proposed"
    )

    review_run: Mapped["ReviewRun"] = relationship(back_populates="items")
