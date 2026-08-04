# Weekly Project Update

Standalone application for collecting and storing one weekly update for one team or project. Each record covers exactly seven inclusive days.

## Requirements

- Python 3.12 or newer
- Node.js 20 or newer
- SQL Server 2022 (the included Compose services are suitable for local development)
- Microsoft ODBC Driver 18 for SQL Server

## Local setup

1. Copy `.env.example` to `.env` and adjust the database or CORS settings when needed.
2. Start SQL Server and create `ProjectUpdateDB` with `docker compose up -d`.
3. In `backend`, create a virtual environment and install `pip install -e ".[dev]"`.
4. Apply the schema with `python -m alembic upgrade head`.
5. Start the API with `python -m uvicorn app.main:app --reload`.
6. In `frontend`, run `npm install` and `npm run dev`.

The frontend runs at `http://localhost:5173`, the API at `http://localhost:8000`, and OpenAPI at `http://localhost:8000/docs`.

The sample connection uses SQL authentication and trusts the development container certificate. For Windows authentication, replace `DATABASE_URL` with an environment-specific URL such as:

```text
mssql+pyodbc://localhost/ProjectUpdateDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
```

Inspect saved updates in SQL Server Management Studio or Azure Data Studio:

```sql
SELECT id, start_of_week, end_of_week, team_project,
	   achievements, initiatives, next_weeks_plan, created_at
FROM dbo.project_updates
ORDER BY created_at DESC;
```

## Submission behavior

Each fresh form owns one UUID idempotency key. Replaying the same key and exact payload returns the original stored record with HTTP 200 and the `Idempotent-Replayed` response header. Reusing a key with changed content returns HTTP 409. A new record returns HTTP 201.

`end_of_week` must equal `start_of_week + 6 days`. The application enforces this rule in the frontend, domain model, and SQL Server check constraint. The result page displays the persisted identifier, reporting dates, narrative fields, and timestamps returned by the API.

Migration `0002` first maps each legacy `reporting_month` to a seven-day interval beginning on that date. It then permanently drops employee identity, reporting month, attachment, SMTP, and delivery-status data. The migration is intentionally irreversible because the removed data cannot be reconstructed.

## Deployment security

This MVP does not include application-level authentication. Deploy the API and frontend only behind the organization's authenticated access gateway, restrict network access to employees, and rate-limit `POST /api/v1/project-updates`. Do not expose the API directly to the public internet.

Configure the reverse proxy or ingress with an appropriate request-body limit and preserve the `Idempotency-Key` request header.

## Validation

Run backend checks from `backend`:

```text
python -m ruff check .
python -m mypy app
python -m pytest -q
python -m alembic check
```

Run frontend checks from `frontend`:

```text
npm run lint
npm run test -- --run
npm run build
```