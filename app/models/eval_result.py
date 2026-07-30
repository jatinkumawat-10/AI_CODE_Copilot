import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class EvalResult(Base):
    """
    One case's result from one run of eval/run_eval.py. Shaped directly by
    score_case()'s real output fields — including n_errors, which exists
    because of the rate-limit failures observed in Stage 2 (see
    eval/EVAL_REPORT.md, Run 2). Multiple rows share an eval_run_id so
    results from the same execution of run_eval.py can be grouped and
    compared against earlier runs over time.
    """

    __tablename__ = "eval_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    eval_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    case_id: Mapped[str] = mapped_column(String, nullable=False)
    expected_to_flag: Mapped[bool] = mapped_column(Boolean, nullable=False)

    hits: Mapped[int] = mapped_column(Integer, nullable=False)
    n_valid_trials: Mapped[int] = mapped_column(Integer, nullable=False)
    n_errors: Mapped[int] = mapped_column(Integer, nullable=False)
    hit_rate: Mapped[float] = mapped_column(Float, nullable=True)

    # Full per-trial detail (method used, raw issues, error text) kept as
    # JSON rather than further normalized tables — this is diagnostic detail
    # you'd read occasionally while debugging a surprising score, not data
    # you'd query/filter across runs the way you would case_id or hit_rate.
    trials: Mapped[list] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
