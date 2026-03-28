import time
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.referral import Referral
from app.models.user import User


class DAGEngine:
    """
    Advanced DAG engine using Recursive CTEs for high-performance graph traversal.
    Ensures O(depth) performance for cycle detection and subtree fetching.
    """

    def can_add_edge(
        self,
        db: Session,
        new_user_id: str,
        referrer_id: str,
    ) -> tuple[bool, str | None, list[str], float]:
        """
        Check if adding edge (new_user -> referrer) creates a cycle using Recursive CTE.
        """
        started = time.perf_counter()

        if new_user_id == referrer_id:
            elapsed = (time.perf_counter() - started) * 1000
            return False, "self_referral", [new_user_id], elapsed

        # Recursive CTE: find if referrer is already a descendant of new_user
        # (i.e., is there a path from referrer -> new_user?)
        query = text("""
            WITH RECURSIVE ancestors AS (
                SELECT referrer_id, CAST(new_user_id || '->' || referrer_id AS TEXT) as path
                FROM referrals
                WHERE new_user_id = :referrer_id AND status = 'valid' AND edge_type = 'primary'
                
                UNION ALL
                
                SELECT r.referrer_id, a.path || '->' || r.referrer_id
                FROM referrals r
                JOIN ancestors a ON r.new_user_id = a.referrer_id
                WHERE r.status = 'valid' AND r.edge_type = 'primary'
            )
            SELECT path FROM ancestors WHERE referrer_id = :new_user_id LIMIT 1
        """)

        result = db.execute(query, {"referrer_id": referrer_id, "new_user_id": new_user_id}).fetchone()

        if result:
            cycle_path = result[0].split("->") + [new_user_id]
            elapsed = (time.perf_counter() - started) * 1000
            return False, "cycle", cycle_path, elapsed

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
        max_depth: int = 5,
    ) -> dict:
        """
        Fetch the full referral subtree rooted at user_id using Recursive CTE.
        Returns a rich graph structure including ancestor paths for smart highlighting.
        """
        query = text("""
            WITH RECURSIVE descendants AS (
                -- Base case: the root node
                SELECT 
                    id as user_id, 
                    CAST(NULL AS TEXT) as parent_id, 
                    CAST(NULL AS TEXT) as edge_id,
                    0 as depth,
                    CAST(id AS TEXT) as full_path
                FROM users 
                WHERE id = :user_id
                
                UNION ALL
                
                -- Recursive step: find children
                SELECT 
                    r.new_user_id, 
                    r.referrer_id, 
                    r.id,
                    d.depth + 1,
                    d.full_path || ',' || r.new_user_id
                FROM referrals r
                JOIN descendants d ON r.referrer_id = d.user_id
                WHERE r.status = 'valid' AND r.edge_type = 'primary' AND d.depth < :max_depth
            )
            SELECT 
                d.*, 
                u.name, 
                u.reward_balance, 
                u.status as user_status
            FROM descendants d
            JOIN users u ON d.user_id = u.id
        """)

        rows = db.execute(query, {"user_id": user_id, "max_depth": max_depth}).fetchall()
        
        if not rows:
            # Root user might not have referrals, but we still want to show the root
            root = db.get(User, user_id)
            if not root: return {"nodes": [], "edges": []}
            return {
                "root": {"id": root.id, "name": root.name, "reward_balance": root.reward_balance},
                "nodes": [{"id": root.id, "data": {"label": root.name, "depth": 0, "reward_balance": root.reward_balance, "ancestry": [root.id]}}],
                "edges": [],
                "total_depth": 0,
                "total_descendants": 0
            }

        nodes = []
        edges = []
        total_depth = 0
        
        for row in rows:
            ancestry = row.full_path.split(",")
            nodes.append({
                "id": row.user_id,
                "data": {
                    "label": row.name,
                    "depth": row.depth,
                    "reward_balance": row.reward_balance,
                    "status": row.user_status,
                    "ancestry": ancestry # Smart Highlighting data
                }
            })
            if row.parent_id:
                edges.append({
                    "id": row.edge_id,
                    "source": row.parent_id,
                    "target": row.user_id,
                    "type": "primary"
                })
            total_depth = max(total_depth, row.depth)

        root_row = next(r for r in rows if r.depth == 0)

        return {
            "root": {
                "id": root_row.user_id,
                "name": root_row.name,
                "reward_balance": root_row.reward_balance,
                "status": root_row.user_status,
            },
            "nodes": nodes,
            "edges": edges,
            "total_depth": total_depth,
            "total_descendants": len(nodes) - 1,
        }


dag_engine = DAGEngine()


dag_engine = DAGEngine()
