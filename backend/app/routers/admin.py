from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reward_config import RewardConfig

router = APIRouter(prefix="/admin", tags=["admin"])


class RewardConfigResponse(BaseModel):
    id: int
    max_depth: int
    reward_type: str
    level_1_value: float
    level_2_value: float
    level_3_value: float
    velocity_limit: int
    referral_expiry_days: int
    updated_at: datetime


class RewardConfigUpdateRequest(BaseModel):
    max_depth: int | None = Field(default=None, ge=1, le=10)
    reward_type: str | None = None
    level_1_value: float | None = Field(default=None, ge=0)
    level_2_value: float | None = Field(default=None, ge=0)
    level_3_value: float | None = Field(default=None, ge=0)
    velocity_limit: int | None = Field(default=None, ge=1)
    referral_expiry_days: int | None = Field(default=None, ge=1)


def get_or_create_config(db: Session) -> RewardConfig:
    config = db.query(RewardConfig).order_by(RewardConfig.id.desc()).first()
    if config:
        return config
    config = RewardConfig()
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("/reward-config", response_model=RewardConfigResponse)
async def get_reward_config(db: Session = Depends(get_db)):
    return get_or_create_config(db)


@router.patch("/reward-config", response_model=RewardConfigResponse)
async def patch_reward_config(payload: RewardConfigUpdateRequest, db: Session = Depends(get_db)):
    config = get_or_create_config(db)
    updates = payload.model_dump(exclude_none=True)
    if "reward_type" in updates and updates["reward_type"] not in {"fixed", "percentage"}:
        raise HTTPException(status_code=400, detail="reward_type must be fixed or percentage")

    for field_name, value in updates.items():
        setattr(config, field_name, value)
    config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(config)
    return config
