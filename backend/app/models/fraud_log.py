import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FraudLog(Base):
    __tablename__ = "fraud_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    new_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    attempted_referrer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    fraud_type: Mapped[str] = mapped_column(String(50), nullable=False)
    cycle_path: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
