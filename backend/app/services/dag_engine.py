import time
from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.models.user import User


class DAGEngine:
    def can_add_edge(
        self,
        db: Session,
        new_user_id: str,
        referrer_id: str,
    ) -> tuple[bool, str | None, list[str], float]:
        started = time.perf_counter()

        if new_user_id == referrer_id:
            elapsed = (time.perf_counter() - started) * 1000
            return False, "self_referral", [new_user_id], elapsed

        result = db.execute(
            select(Referral.new_user_id, Referral.referrer_id).where(
                Referral.status == "valid",
                Referral.edge_type == "primary",
            )
        )
        parent_by_child = {
            child: parent
            for child, parent in result.all()
        }

        path = [referrer_id]
        current = referrer_id
        seen = {referrer_id}
        while current in parent_by_child:
            current = parent_by_child[current]
            path.append(current)
            if current == new_user_id:
                cycle_path = [new_user_id, *reversed(path)]
                elapsed = (time.perf_counter() - started) * 1000
                return False, "cycle", cycle_path, elapsed
            if current in seen:
                elapsed = (time.perf_counter() - started) * 1000
                return False, "corrupt_graph", path, elapsed
            seen.add(current)

        elapsed = (time.perf_counter() - started) * 1000
        return True, None, [], elapsed

    def commit_edge(
        self,
        db: Session,
        new_user_id: str,
        referrer_id: str,
        edge_type: str = "primary",
        expires_at: datetime | None = None,
    ) -> Referral:
        referral = Referral(
            new_user_id=new_user_id,
            referrer_id=referrer_id,
            edge_type=edge_type,
            status="valid",
            expires_at=expires_at,
        )
        db.add(referral)
        return referral

    def get_user_subtree(
        self,
        db: Session,
        user_id: str,
        max_depth: int = 3,
    ) -> dict:
        users_result = db.execute(select(User))
        users = {user.id: user for user in users_result.scalars().all()}
        edges_result = db.execute(
            select(Referral).where(Referral.status == "valid", Referral.edge_type == "primary")
        )
        children_by_parent: dict[str, list[Referral]] = defaultdict(list)
        for edge in edges_result.scalars().all():
            children_by_parent[edge.referrer_id].append(edge)

        root = users[user_id]
        nodes = [
            {
                "id": root.id,
                "data": {
                    "label": root.name,
                    "depth": 0,
                    "reward_balance": root.reward_balance,
                    "status": root.status,
                },
            }
        ]
        graph_edges = []
        total_depth = 0
        total_descendants = 0
        queue = [(user_id, 0)]
        visited = {user_id}

        while queue:
            current_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            for referral in children_by_parent.get(current_id, []):
                child = users.get(referral.new_user_id)
                if not child or child.id in visited:
                    continue
                visited.add(child.id)
                child_depth = depth + 1
                total_depth = max(total_depth, child_depth)
                total_descendants += 1
                nodes.append(
                    {
                        "id": child.id,
                        "data": {
                            "label": child.name,
                            "depth": child_depth,
                            "reward_balance": child.reward_balance,
                            "status": child.status,
                        },
                    }
                )
                graph_edges.append(
                    {
                        "id": referral.id,
                        "source": current_id,
                        "target": child.id,
                        "type": referral.edge_type,
                    }
                )
                queue.append((child.id, child_depth))

        return {
            "root": {
                "id": root.id,
                "name": root.name,
                "reward_balance": root.reward_balance,
                "status": root.status,
            },
            "nodes": nodes,
            "edges": graph_edges,
            "total_depth": total_depth,
            "total_descendants": total_descendants,
        }


dag_engine = DAGEngine()
