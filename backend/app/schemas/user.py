from datetime import datetime

from pydantic import BaseModel, Field


class GraphNodeData(BaseModel):
    label: str
    depth: int
    reward_balance: float
    status: str


class GraphNode(BaseModel):
    id: str
    data: GraphNodeData


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str


class GraphResponse(BaseModel):
    root: dict
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    total_depth: int
    total_descendants: int


class RewardTransactionItem(BaseModel):
    referral_id: str
    amount: float
    depth_level: int
    from_user: str | None = None
    created_at: datetime


class RewardResponse(BaseModel):
    user_id: str
    total_earned: float
    current_balance: float
    transactions: list[RewardTransactionItem] = Field(default_factory=list)


class UserCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    referral_code: str = Field(min_length=3, max_length=32)
    status: str = "active"
    is_root: bool = False


class UserItem(BaseModel):
    id: str
    name: str
    email: str
    referral_code: str
    reward_balance: float
    status: str
    is_root: bool
    created_at: datetime


class UserListResponse(BaseModel):
    total: int
    users: list[UserItem] = Field(default_factory=list)
