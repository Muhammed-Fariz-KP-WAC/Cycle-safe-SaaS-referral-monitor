import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = (
        UniqueConstraint("new_user_id", "edge_type", name="uq_referral_primary_edge"),
        Index("ix_referrals_referrer_status", "referrer_id", "status"),
        Index("ix_referrals_new_user_status", "new_user_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    new_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    referrer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    edge_type: Mapped[str] = mapped_column(String(20), nullable=False, default="primary")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="valid")
    rejection_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
