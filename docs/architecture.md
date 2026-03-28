# Architecture Note

## DAG Invariant

The system models referrals as a directed graph where each primary edge points from `new_user -> referrer`. Before any primary edge is inserted, the backend walks the referrer lineage upward and rejects the claim if the candidate child already appears in that ancestry chain. That preserves a directed acyclic graph for all reward-bearing edges.

## Why This Design

FastAPI gives a clean API layer with Swagger out of the box, and SQLAlchemy keeps the PostgreSQL integration straightforward for transactional graph operations. The service layer keeps the critical responsibilities separated:

- `dag_engine.py` enforces acyclic structure.
- `fraud_service.py` handles self-referral, duplicate, velocity, and suspicious fresh-account checks.
- `reward_engine.py` propagates rewards upward only on valid, committed edges.
- `activity_service.py` records recent events and pushes SSE updates to the dashboard.

## Transaction Safety

Referral acceptance is handled as one transactional flow: validate, commit the edge, distribute rewards, publish activity, then commit. Rejections log fraud and convert the attempted child to a root account so the system state stays valid without silently losing the user.

## Dashboard Data Flow

The dashboard reads metrics, graph data, fraud flags, and recent activity from API endpoints. It also listens to `/api/dashboard/stream` for live event updates so evaluators can see fraud blocks and accepted referrals as they happen.
