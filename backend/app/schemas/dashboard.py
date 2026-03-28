from datetime import datetime

from pydantic import BaseModel, Field


class DashboardMetrics(BaseModel):
    total_users: int
    total_referrals: int
    valid_referrals: int
    rejected_referrals: int
    fraud_attempts: int
    fraud_breakdown: dict[str, int] = Field(default_factory=dict)
    total_rewards_distributed: float
    referrals_last_24h: int
    avg_cycle_check_ms: float


class ActivityItem(BaseModel):
    id: str
    event_type: str
    payload: dict
    created_at: datetime


class SimulationRequest(BaseModel):
    depth: int = 3
    reward_type: str = "fixed"
    values: list[float] = Field(default_factory=lambda: [100.0, 50.0, 25.0])
    expected_users: int = 100
    avg_referrals_per_user: float = 1.5


class SimulationResponse(BaseModel):
    projected_total_payout: float
    cost_per_acquisition: float
    breakdown: list[dict]
