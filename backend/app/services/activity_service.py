from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.events import broadcaster
from app.models.activity_event import ActivityEvent


class ActivityService:
    async def publish_live(self, event_type: str, payload: dict) -> None:
        await broadcaster.publish(event_type, payload)

    def record(self, db: Session, event_type: str, payload: dict) -> ActivityEvent:
        event = ActivityEvent(event_type=event_type, payload=payload, created_at=datetime.utcnow())
        db.add(event)
        db.flush()
        return event

    def recent(self, db: Session, limit: int = 25) -> list[ActivityEvent]:
        result = db.execute(
            select(ActivityEvent).order_by(ActivityEvent.created_at.desc()).limit(limit)
        )
        return list(reversed(result.scalars().all()))


activity_service = ActivityService()
