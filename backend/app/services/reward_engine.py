from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.models.reward import Reward
from app.models.reward_config import RewardConfig
from app.models.user import User


class RewardEngine:
    def get_active_config(self, db: Session) -> RewardConfig:
        result = db.execute(select(RewardConfig).order_by(RewardConfig.id.desc()).limit(1))
        config = result.scalar_one_or_none()
        if config:
            return config
        config = RewardConfig()
        db.add(config)
        db.flush()
        return config

    def distribute_rewards(
        self,
        db: Session,
        referral_id: str,
        new_user_id: str,
        config: RewardConfig,
    ) -> list[dict]:
        edge_result = db.execute(
            select(Referral).where(
                Referral.new_user_id == new_user_id,
                Referral.status == "valid",
                Referral.edge_type == "primary",
            )
        )
        direct_edge = edge_result.scalar_one_or_none()
        if not direct_edge:
            return []

        value_map = {
            1: config.level_1_value,
            2: config.level_2_value,
            3: config.level_3_value,
        }
        distributions: list[dict] = []
        current_referrer_id = direct_edge.referrer_id
        depth = 1

        while current_referrer_id and depth <= config.max_depth:
            beneficiary = db.get(User, current_referrer_id)
            if not beneficiary:
                break

            amount = value_map.get(depth, value_map.get(config.max_depth, 0.0))
            reward = Reward(
                referral_id=referral_id,
                beneficiary_id=beneficiary.id,
                amount=amount,
                depth_level=depth,
                reward_type=config.reward_type,
                created_at=datetime.utcnow(),
            )
            beneficiary.reward_balance += amount
            db.add(reward)
            distributions.append(
                {
                    "user_id": beneficiary.id,
                    "amount": amount,
                    "depth": depth,
                }
            )

            next_edge_result = db.execute(
                select(Referral).where(
                    Referral.new_user_id == current_referrer_id,
                    Referral.status == "valid",
                    Referral.edge_type == "primary",
                )
            )
            next_edge = next_edge_result.scalar_one_or_none()
            current_referrer_id = next_edge.referrer_id if next_edge else None
            depth += 1

        return distributions


reward_engine = RewardEngine()
