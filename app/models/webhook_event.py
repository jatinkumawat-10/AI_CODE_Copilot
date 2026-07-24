import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ProcessedWebhookEvent(Base):
    """
    Tracks (owner, repo, pr_number, head_sha) combinations already
    attempted, so a duplicate webhook delivery for the same commit
    (a genuine GitHub retry, or manually clicking Redeliver) doesn't
    trigger a second review attempt. Recorded at attempt time, not only
    on success -- a failed attempt (e.g. rate limit) is not automatically
    retried by a duplicate delivery for the same commit; only a new
    commit (new head_sha) triggers a fresh attempt. This is a deliberate
    tradeoff: it protects against wasted LLM calls on true duplicates,
    at the cost of not auto-retrying failed attempts.
    """
    __tablename__ = "processed_webhook_events"
    __table_args__ = (
        UniqueConstraint(
            "owner", "repo", "pr_number", "head_sha", name="uq_webhook_event"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner: Mapped[str] = mapped_column(String, nullable=False)
    repo: Mapped[str] = mapped_column(String, nullable=False)
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    head_sha: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )