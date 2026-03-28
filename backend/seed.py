import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models.reward_config import RewardConfig
from app.models.user import User
from app.schemas.referral import ReferralClaimRequest
from app.routers.referral import claim_referral


USERS = [
    ("Root User", "root@example.com", "ROOT-001", True, datetime.utcnow() - timedelta(days=30)),
    ("Alice", "alice@example.com", "ALICE-001", False, datetime.utcnow() - timedelta(days=20)),
    ("Bob", "bob@example.com", "BOB-001", False, datetime.utcnow() - timedelta(days=10)),
    ("Charlie", "charlie@example.com", "CHARLIE-001", False, datetime.utcnow() - timedelta(days=10)),
    ("Diana", "diana@example.com", "DIANA-001", False, datetime.utcnow() - timedelta(days=9)),
    ("Eve", "eve@example.com", "EVE-001", False, datetime.utcnow() - timedelta(days=8)),
    ("Frank", "frank@example.com", "FRANK-001", False, datetime.utcnow() - timedelta(days=7)),
    ("Rapid User", "rapid@example.com", "RAPID-001", False, datetime.utcnow() - timedelta(days=7)),
    ("Duplicate User", "duplicate@example.com", "DUP-001", False, datetime.utcnow() - timedelta(days=7)),
]


async def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        users = []
        for name, email, code, is_root, created_at in USERS:
            user = User(
                name=name,
                email=email,
                referral_code=code,
                is_root=is_root,
                status="root" if is_root else "active",
                created_at=created_at,
            )
            db.add(user)
            users.append(user)
        db.add(
            RewardConfig(
                max_depth=3,
                reward_type="fixed",
                level_1_value=100.0,
                level_2_value=50.0,
                level_3_value=25.0,
                velocity_limit=5,
                referral_expiry_days=365,
            )
        )
        db.commit()

        result = db.execute(select(User))
        by_name = {user.name: user for user in result.scalars().all()}

        valid_claims = [
            ("Alice", "ROOT-001"),
            ("Bob", "ALICE-001"),
            ("Charlie", "BOB-001"),
            ("Diana", "ALICE-001"),
            ("Eve", "ROOT-001"),
            ("Frank", "EVE-001"),
        ]
        for child_name, code in valid_claims:
            await claim_referral(
                ReferralClaimRequest(new_user_id=by_name[child_name].id, referrer_code=code),
                db,
            )

        await claim_referral(
            ReferralClaimRequest(new_user_id=by_name["Alice"].id, referrer_code="CHARLIE-001"),
            db,
        )
        await claim_referral(
            ReferralClaimRequest(new_user_id=by_name["Bob"].id, referrer_code="BOB-001"),
            db,
        )
        await claim_referral(
            ReferralClaimRequest(new_user_id=by_name["Duplicate User"].id, referrer_code="ALICE-001"),
            db,
        )
        await claim_referral(
            ReferralClaimRequest(new_user_id=by_name["Duplicate User"].id, referrer_code="ALICE-001"),
            db,
        )
        for index in range(6):
            temp_user = User(
                name=f"Velocity Child {index + 1}",
                email=f"velocity{index + 1}@example.com",
                referral_code=f"VEL-{index + 1:03d}",
                status="active",
                created_at=datetime.utcnow() - timedelta(days=10),
            )
            db.add(temp_user)
            db.commit()
            await claim_referral(
                ReferralClaimRequest(new_user_id=temp_user.id, referrer_code="RAPID-001"),
                db,
            )

        print("Seeded referral engine data.")


if __name__ == "__main__":
    asyncio.run(seed())
