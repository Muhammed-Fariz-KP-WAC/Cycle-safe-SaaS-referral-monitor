from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.events import broadcaster
from app.database import get_db
from app.models.activity_event import ActivityEvent
from app.models.fraud_log import FraudLog
from app.models.referral import Referral
from app.models.reward import Reward
from app.models.user import User
from app.schemas.dashboard import DashboardMetrics, SimulationRequest, SimulationResponse
from app.services.activity_service import activity_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics(db: Session = Depends(get_db)):
    total_users = (db.execute(select(func.count(User.id)))).scalar() or 0
    valid_referrals = (
        db.execute(select(func.count(Referral.id)).where(Referral.status == "valid"))
    ).scalar() or 0
    fraud_attempts = (db.execute(select(func.count(FraudLog.id)))).scalar() or 0
    total_referrals = valid_referrals + fraud_attempts
    rejected_referrals = fraud_attempts
    total_rewards = (db.execute(select(func.sum(Reward.amount)))).scalar() or 0.0
    window_start = datetime.utcnow() - timedelta(days=1)
    last_day_referrals = (
        db.execute(
            select(func.count(Referral.id)).where(
                Referral.created_at >= window_start
            )
        )
    ).scalar() or 0
    breakdown_rows = (
        db.execute(select(FraudLog.fraud_type, func.count(FraudLog.id)).group_by(FraudLog.fraud_type))
    ).all()
    referral_rows = db.execute(select(ActivityEvent).where(ActivityEvent.event_type == "referral_activity"))
    cycle_samples = []
    for event in referral_rows.scalars().all():
        rewards = event.payload.get("rewards", [])
        if not rewards:
            cycle_samples.append(0.0)
        cycle_samples.append(float(event.payload.get("cycle_check_ms", 0.0)))
    avg_cycle_check_ms = round(sum(cycle_samples) / len(cycle_samples), 2) if cycle_samples else 0.0
    return {
        "total_users": total_users,
        "total_referrals": total_referrals,
        "valid_referrals": valid_referrals,
        "rejected_referrals": rejected_referrals,
        "fraud_attempts": fraud_attempts,
        "fraud_breakdown": {fraud_type: count for fraud_type, count in breakdown_rows},
        "total_rewards_distributed": round(float(total_rewards), 2),
        "referrals_last_24h": last_day_referrals,
        "avg_cycle_check_ms": avg_cycle_check_ms,
    }


@router.get("/activities")
async def get_activities(db: Session = Depends(get_db)):
    events = activity_service.recent(db, settings.recent_activity_limit)
    return [
        {
            "id": event.id,
            "event_type": event.event_type,
            "payload": event.payload,
            "created_at": event.created_at,
        }
        for event in events
    ]


@router.get("/stream")
async def stream_events():
    return StreamingResponse(broadcaster.subscribe(), media_type="text/event-stream")


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_rewards(payload: SimulationRequest):
    active_levels = payload.values[: payload.depth]
    breakdown = []
    projected_total = 0.0
    for level, value in enumerate(active_levels, start=1):
        beneficiaries = max(int(payload.expected_users * (payload.avg_referrals_per_user ** (level - 1))), 1)
        total = round(beneficiaries * value, 2)
        projected_total += total
        breakdown.append(
            {
                "level": level,
                "beneficiaries": beneficiaries,
                "unit_value": value,
                "total": total,
            }
        )

    return {
        "projected_total_payout": round(projected_total, 2),
        "cost_per_acquisition": round(projected_total / max(payload.expected_users, 1), 2),
        "breakdown": breakdown,
    }
