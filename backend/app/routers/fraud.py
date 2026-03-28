from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fraud_log import FraudLog
from app.models.user import User
from app.schemas.referral import FraudFlagsResponse

router = APIRouter(prefix="/fraud", tags=["fraud"])


@router.get("/flags", response_model=FraudFlagsResponse)
async def get_fraud_flags(db: Session = Depends(get_db)):
    result = db.execute(
        select(FraudLog, User.name)
        .join(User, User.id == FraudLog.new_user_id, isouter=True)
        .order_by(FraudLog.created_at.desc())
    )
    flags = []
    for log, attempted_by in result.all():
        attempted_referrer = None
        if log.attempted_referrer_id:
            referrer = db.get(User, log.attempted_referrer_id)
            attempted_referrer = referrer.name if referrer else None
        flags.append(
            {
                "id": log.id,
                "fraud_type": log.fraud_type,
                "attempted_by": attempted_by,
                "attempted_referrer": attempted_referrer,
                "cycle_path": log.cycle_path or [],
                "metadata": log.metadata_json,
                "created_at": log.created_at,
            }
        )
    return {"total": len(flags), "flags": flags}
