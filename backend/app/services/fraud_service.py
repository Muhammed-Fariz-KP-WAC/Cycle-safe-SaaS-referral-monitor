from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.fraud_log import FraudLog
from app.models.referral import Referral
from app.models.user import User


class FraudService:
    def check_duplicate(self, db: Session, new_user_id: str, referrer_id: str, edge_type: str) -> bool:
        result = db.execute(
            select(Referral.id).where(
                Referral.new_user_id == new_user_id,
                Referral.referrer_id == referrer_id,
                Referral.edge_type == edge_type,
            )
        )
        return result.scalar_one_or_none() is not None

    def check_velocity(self, db: Session, referrer_id: str, limit: int) -> bool:
        window_start = datetime.utcnow() - timedelta(minutes=1)
        result = db.execute(
            select(func.count(Referral.id)).where(
                Referral.referrer_id == referrer_id,
                Referral.status == "valid",
                Referral.created_at >= window_start,
            )
        )
        return (result.scalar() or 0) >= limit

    def check_account_age(self, db: Session, new_user_id: str) -> bool:
        user = db.get(User, new_user_id)
        if not user:
            return False
        return user.created_at >= datetime.utcnow() - timedelta(minutes=5)

    def log_fraud(
        self,
        db: Session,
        fraud_type: str,
        new_user_id: str | None,
        attempted_referrer_id: str | None,
        cycle_path: list[str] | None = None,
        metadata: dict | None = None,
    ) -> FraudLog:
        log = FraudLog(
            fraud_type=fraud_type,
            new_user_id=new_user_id,
            attempted_referrer_id=attempted_referrer_id,
            cycle_path=cycle_path,
            metadata_json=metadata or {},
        )
        db.add(log)
        return log


fraud_service = FraudService()
