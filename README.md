# Cycle-Safe Referral Engine

A robust, backend-heavy referral system designed with **DAG-safe claims**, real-time **fraud detection**, and automated **reward propagation**. This project features a high-performance FastAPI backend, PostgreSQL storage, and a sleek React-based administrative dashboard.

---

## 🏗️ System Architecture

The engine is built around a **Directed Acyclic Graph (DAG)** model to ensure referral integrity and prevent circular reward exploitation.

### Core Architectural Principles

*   **DAG Invariant:** Referrals are modeled as directed edges (`new_user -> referrer`). Before any referral is accepted, the system performs a lineage walk to ensure the new user doesn't already exist in the referrer's ancestry, preserving a cycle-free graph.
*   **Service-Oriented Design:**
    *   `dag_engine.py`: Enforces the acyclic structure during referral claims.
    *   `fraud_service.py`: Implements multi-layered checks (self-referral, duplicates, velocity, and fresh-account flags).
    *   `reward_engine.py`: Handles complex, multi-level reward propagation along valid edges.
    *   `activity_service.py`: Manages the event log and pushes real-time updates via **Server-Sent Events (SSE)**.
*   **Transaction Integrity:** All referral operations (validation, edge creation, reward distribution) are wrapped in atomic database transactions. Rejections are logged as fraud events, ensuring the system remains consistent and auditable.
*   **Real-time Visibility:** The frontend maintains a live connection to the backend via SSE, providing instant feedback on fraud blocks and successful referrals.

---

## 🚀 Features

-   **Graph-Based Referrals:** Visualizes and manages complex referral networks.
-   **Multi-Level Rewards:** Configurable reward structures that propagate up the referral chain.
-   **Advanced Fraud Detection:** Built-in protection against common referral exploits.
-   **Live Monitoring:** Real-time activity feed and metrics dashboard.
-   **Network Visualization:** Interactive graph view of user referral relationships.
-   **Simulation Tools:** Test reward configurations and referral scenarios before deployment.

---

## 🛠️ Tech Stack

-   **Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.0 (Async), PostgreSQL (psycopg3).
-   **Frontend:** React (Vite), Tailwind-inspired Vanilla CSS, React Flow (for graph visualization).
-   **Infrastructure:** Docker, Docker Compose.
-   **Real-time:** Server-Sent Events (SSE) for live dashboard updates.

---

## 📂 Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration and events
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── routers/        # API endpoints (User, Referral, Fraud, Admin)
│   │   ├── schemas/        # Pydantic models for validation
│   │   └── services/       # Core business logic (DAG, Reward, Fraud engines)
│   └── seed.py             # Database initialization and seeding script
├── frontend/
│   ├── src/
│   │   ├── api/            # API client and SSE integration
│   │   ├── components/     # Reusable UI components (Graph, Feed, Panels)
│   │   └── pages/          # Dashboard layout and tab management
└── docs/                   # Detailed architectural documentation
```

---

## 🚦 Getting Started

### 1. Run with Docker (Recommended)

This sets up the entire stack, including the PostgreSQL database.

```bash
docker-compose up --build
```

### 2. Seed the Database

In a separate terminal, initialize the database with sample data:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Ensure DATABASE_URL matches your environment
export DATABASE_URL=postgresql+psycopg://referral:referral@localhost:5432/referral_engine
python seed.py
```

### 3. Local Development

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```
API: `http://localhost:8000` | Swagger: `http://localhost:8000/docs`

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Dashboard: `http://localhost:5173`

---

## 🔗 Key API Endpoints

| Endpoint | Description |
| :--- | :--- |
| `POST /api/referral/claim` | Process a new referral claim with DAG & Fraud checks. |
| `GET /api/user/{id}/graph` | Retrieve the referral graph for a specific user. |
| `GET /api/fraud/flags` | List all detected fraud attempts and violations. |
| `GET /api/dashboard/metrics` | Summary statistics for the admin dashboard. |
| `GET /api/dashboard/stream` | SSE endpoint for real-time activity updates. |
| `POST /api/dashboard/simulate` | Simulate reward distribution for testing. |
| `PATCH /api/admin/reward-config` | Update global reward rules (depth, amounts, etc). |
