from datetime import datetime

from pydantic import BaseModel, Field


class ReferralClaimRequest(BaseModel):
    new_user_id: str
    referrer_code: str = Field(min_length=3, max_length=32)
    edge_type: str = "primary"


class RewardDistribution(BaseModel):
    user_id: str
    amount: float
    depth: int


class ReferralClaimResponse(BaseModel):
    status: str
    referral_id: str | None = None
    reason: str | None = None
    cycle_path: list[str] = Field(default_factory=list)
    message: str
    rewards_distributed: list[RewardDistribution] = Field(default_factory=list)
    cycle_check_ms: float


class FraudFlagItem(BaseModel):
    id: str
    fraud_type: str
    attempted_by: str | None = None
    attempted_referrer: str | None = None
    cycle_path: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime


class FraudFlagsResponse(BaseModel):
    total: int
    flags: list[FraudFlagItem]
