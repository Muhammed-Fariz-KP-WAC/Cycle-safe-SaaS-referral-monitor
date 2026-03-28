from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RewardConfig(Base):
    __tablename__ = "reward_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    max_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    reward_type: Mapped[str] = mapped_column(String(20), nullable=False, default="fixed")
    level_1_value: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    level_2_value: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    level_3_value: Mapped[float] = mapped_column(Float, nullable=False, default=25.0)
    velocity_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    referral_expiry_days: Mapped[int] = mapped_column(Integer, nullable=False, default=365)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
