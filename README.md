# Cycle-Safe Referral Engine

Backend-heavy referral engine with DAG-safe claims, fraud detection, reward propagation, PostgreSQL storage, seed data, Swagger docs, and a lightweight React dashboard.

## Run With Docker

This is the easiest PostgreSQL setup.

```bash
cd /home/wac/TASK
docker-compose up --build
```

In a second terminal, seed the database:

```bash
cd /home/wac/TASK/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DATABASE_URL=postgresql+psycopg://referral:referral@localhost:5432/referral_engine python seed.py
```

## Run Backend Locally Against PostgreSQL

If you want to run the backend outside Docker but still use PostgreSQL:

```bash
cd /home/wac/TASK
docker-compose up db -d
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://referral:referral@localhost:5432/referral_engine
python seed.py
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, with Swagger at `http://localhost:8000/docs`.

## Run frontend

```bash
cd /home/wac/TASK/frontend
npm install
VITE_API_URL=http://localhost:8000/api npm run dev
```

The dashboard will be available at `http://localhost:5173`.

## Key endpoints

- `POST /api/referral/claim`
- `GET /api/user`
- `POST /api/user`
- `GET /api/user/{id}/graph`
- `GET /api/user/{id}/rewards`
- `GET /api/fraud/flags`
- `GET /api/dashboard/metrics`
- `GET /api/dashboard/activities`
- `GET /api/dashboard/stream`
- `POST /api/dashboard/simulate`
- `GET /api/admin/reward-config`
- `PATCH /api/admin/reward-config`
