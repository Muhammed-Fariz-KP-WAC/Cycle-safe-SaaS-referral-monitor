from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.referral import Referral
from app.models.user import User
from app.schemas.referral import ReferralClaimRequest, ReferralClaimResponse
from app.services.activity_service import activity_service
from app.services.dag_engine import dag_engine
from app.services.fraud_service import fraud_service
from app.services.reward_engine import reward_engine

router = APIRouter(prefix="/referral", tags=["referral"])


def assign_root_if_orphan(db: Session, user: User) -> None:
    existing_primary = db.execute(
        select(Referral.id).where(
            Referral.new_user_id == user.id,
            Referral.edge_type == "primary",
            Referral.status == "valid",
        )
    )
    if existing_primary.scalar_one_or_none() is None:
        user.is_root = True
        user.status = "root"


@router.post("/claim", response_model=ReferralClaimResponse, status_code=status.HTTP_201_CREATED)
async def claim_referral(payload: ReferralClaimRequest, db: Session = Depends(get_db)):
    new_user = db.get(User, payload.new_user_id)
    if not new_user:
        raise HTTPException(status_code=404, detail="New user not found")

    referrer_result = db.execute(
        select(User).where(User.referral_code == payload.referrer_code)
    )
    referrer = referrer_result.scalar_one_or_none()
    if not referrer:
        raise HTTPException(status_code=404, detail="Referrer code not found")

    config = reward_engine.get_active_config(db)

    duplicate = fraud_service.check_duplicate(
        db, new_user.id, referrer.id, payload.edge_type
    )
    if duplicate:
        fraud_service.log_fraud(
            db,
            "duplicate",
            new_user.id,
            referrer.id,
            metadata={"edge_type": payload.edge_type},
        )
        assign_root_if_orphan(db, new_user)
        activity_service.record(
            db,
            "fraud_alert",
            {"type": "duplicate", "new_user_id": new_user.id, "referrer_id": referrer.id},
        )
        db.commit()
        await activity_service.publish_live(
            "fraud_alert",
            {"type": "duplicate", "new_user_id": new_user.id, "referrer_id": referrer.id},
        )
        return ReferralClaimResponse(
            status="rejected",
            reason="duplicate",
            message="Duplicate referral claim rejected.",
            cycle_check_ms=0.0,
        )

    velocity_exceeded = fraud_service.check_velocity(db, referrer.id, config.velocity_limit)
    if velocity_exceeded:
        fraud_service.log_fraud(
            db,
            "velocity",
            new_user.id,
            referrer.id,
            metadata={"limit": config.velocity_limit},
        )
        assign_root_if_orphan(db, new_user)
        activity_service.record(
            db,
            "fraud_alert",
            {"type": "velocity", "new_user_id": new_user.id, "referrer_id": referrer.id},
        )
        db.commit()
        await activity_service.publish_live(
            "fraud_alert",
            {"type": "velocity", "new_user_id": new_user.id, "referrer_id": referrer.id},
        )
        return ReferralClaimResponse(
            status="rejected",
            reason="velocity",
            message="Velocity limit exceeded for this referrer.",
            cycle_check_ms=0.0,
        )

    is_fresh_account = fraud_service.check_account_age(db, new_user.id)
    if is_fresh_account:
        fraud_service.log_fraud(
            db,
            "new_account_velocity",
            new_user.id,
            referrer.id,
            metadata={"message": "Account created in the last five minutes"},
        )
        activity_service.record(
            db,
            "fraud_alert",
            {"type": "new_account_velocity", "new_user_id": new_user.id, "referrer_id": referrer.id},
        )

    can_add, reason, cycle_path, cycle_ms = dag_engine.can_add_edge(
        db,
        new_user.id,
        referrer.id,
    )
    if not can_add:
        fraud_service.log_fraud(
            db,
            reason or "cycle",
            new_user.id,
            referrer.id,
            cycle_path=cycle_path,
        )
        assign_root_if_orphan(db, new_user)
        activity_service.record(
            db,
            "fraud_alert",
            {
                "type": reason,
                "new_user_id": new_user.id,
                "referrer_id": referrer.id,
                "cycle_path": cycle_path,
            },
        )
        db.commit()
        await activity_service.publish_live(
            "fraud_alert",
            {
                "type": reason,
                "new_user_id": new_user.id,
                "referrer_id": referrer.id,
                "cycle_path": cycle_path,
            },
        )
        return ReferralClaimResponse(
            status="rejected",
            reason=reason,
            cycle_path=cycle_path,
            message="Referral rejected because it violates the DAG invariant.",
            cycle_check_ms=round(cycle_ms, 2),
        )

    expires_at = datetime.utcnow() + timedelta(days=config.referral_expiry_days)
    try:
        referral = dag_engine.commit_edge(
            db,
            new_user.id,
            referrer.id,
            payload.edge_type,
            expires_at=expires_at,
        )
        new_user.is_root = False
        new_user.status = "active"
        db.flush()
        rewards = reward_engine.distribute_rewards(db, referral.id, new_user.id, config)
        activity_service.record(
            db,
            "referral_activity",
            {
                "type": "accepted",
                "new_user_id": new_user.id,
                "new_user_name": new_user.name,
                "referrer_id": referrer.id,
                "referrer_name": referrer.name,
                "rewards": rewards,
                "cycle_check_ms": round(cycle_ms, 2),
            },
        )
        db.commit()
        await activity_service.publish_live(
            "referral_activity",
            {
                "type": "accepted",
                "new_user_id": new_user.id,
                "new_user_name": new_user.name,
                "referrer_id": referrer.id,
                "referrer_name": referrer.name,
                "rewards": rewards,
                "cycle_check_ms": round(cycle_ms, 2),
            },
        )
        return ReferralClaimResponse(
            status="accepted",
            referral_id=referral.id,
            message="Referral accepted and rewards distributed.",
            rewards_distributed=rewards,
            cycle_check_ms=round(cycle_ms, 2),
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Referral edge already exists") from exc
