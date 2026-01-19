# College Mayor Elections (Full-Stack)

A contract-driven **college election system** where eligible voters can vote **exactly once** for a candidate and admins manage elections, candidates, and results.

## Key workflows
- **Admin**: create election (draft) → add candidates → open election → close election → view results and audit log
- **Voter**: login → view open election → vote once → confirm “my vote”

## Tech stack
- Frontend: React + Vite + TypeScript, Vitest + React Testing Library
- Backend: FastAPI + SQLAlchemy + Alembic, pytest
- DB: SQLite (dev/test) and Postgres (prod/integration)
- Containerization: Docker + docker-compose
- CI/CD: GitHub Actions (tests + build; deploy hook placeholder)

## API contract (OpenAPI)
- Source of truth: `openapi/openapi.yaml`
- Backend implements this contract.
- Frontend uses it for typing and implementation guidance.

## Local run (Docker)
```bash
docker compose up --build
```
- Frontend: http://localhost:5173
- Backend: http://localhost:8000/docs

## Local run (no Docker)
Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./dev.db
uvicorn app.main:app --reload
```
Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Tests
Backend unit tests:
```bash
cd backend
pytest -q
```
Backend integration tests (needs Postgres):
```bash
cd backend
pytest -q tests/integration
```
Frontend tests:
```bash
cd frontend
npm test
```

## AI-assisted development + MCP
This repo includes an example MCP server (`mcp-server/`) that loads `openapi.yaml` and exposes tools to:
- list endpoints
- show request/response schemas
- generate minimal test skeletons for an endpoint

This is used as a fast “contract navigator” while implementing the backend and writing tests.
