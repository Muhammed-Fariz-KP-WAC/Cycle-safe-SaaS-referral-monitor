from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.referral import Referral
from app.models.reward import Reward
from app.models.user import User
from app.schemas.user import (
    GraphResponse,
    RewardResponse,
    UserCreateRequest,
    UserItem,
    UserListResponse,
)
from app.services.dag_engine import dag_engine

router = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=UserListResponse)
async def list_users(db: Session = Depends(get_db)):
    rows = db.execute(select(User).order_by(User.created_at.desc()))
    users = rows.scalars().all()
    return {"total": len(users), "users": users}


@router.post("", response_model=UserItem, status_code=201)
async def create_user(payload: UserCreateRequest, db: Session = Depends(get_db)):
    user = User(
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        referral_code=payload.referral_code.strip().upper(),
        status=payload.status,
        is_root=payload.is_root,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or referral code already exists") from exc
    db.refresh(user)
    return user


@router.get("/{user_id}/graph", response_model=GraphResponse)
async def get_user_graph(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dag_engine.get_user_subtree(db, user_id)


@router.get("/{user_id}/rewards", response_model=RewardResponse)
async def get_user_rewards(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reward_rows = db.execute(
        select(Reward, Referral.new_user_id, User.name)
        .join(Referral, Referral.id == Reward.referral_id)
        .join(User, User.id == Referral.new_user_id)
        .where(Reward.beneficiary_id == user_id)
        .order_by(Reward.created_at.desc())
    )
    transactions = [
        {
            "referral_id": reward.referral_id,
            "amount": reward.amount,
            "depth_level": reward.depth_level,
            "from_user": from_name,
            "created_at": reward.created_at,
        }
        for reward, _from_user_id, from_name in reward_rows.all()
    ]
    total_earned = sum(item["amount"] for item in transactions)
    return {
        "user_id": user.id,
        "total_earned": total_earned,
        "current_balance": user.reward_balance,
        "transactions": transactions,
    }
