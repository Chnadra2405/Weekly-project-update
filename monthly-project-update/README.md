# Monthly Project Update

Standalone MVP for collecting one employee's monthly update for one team or project, storing the submission and optional reference files, and delivering an escaped multipart email through configurable SMTP.

## Requirements

- Python 3.12 or newer
- Node.js 20 or newer
- SQL Server 2022 (the included Compose services are suitable for local development)
- Microsoft ODBC Driver 18 for SQL Server

## Local setup

1. Copy `.env.example` to `.env` and set SMTP recipients and credentials.
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
SELECT id, employee_name, employee_email, reporting_month, team_project,
	   delivery_status, sent_at, created_at
FROM dbo.project_updates
ORDER BY created_at DESC;
```

## Delivery and storage behavior

Each fresh form owns one UUID idempotency key. Replaying the same key and exact payload returns the stored result and does not invoke SMTP. Reusing a key with changed content returns HTTP 409. Delivery failures are persisted as `FAILED` and are never retried automatically. `PENDING` means the durable submission requires operational reconciliation.

A replay received while the original request is still `PENDING` returns HTTP 202. Terminal replays return HTTP 200. Clients must not treat a `PENDING` response as confirmed delivery.

Validated files are held under `STORAGE_ROOT/.staging`, then atomically moved to `STORAGE_ROOT/submissions/<submission-id>`. Database records contain relative paths only. Back up SQL Server and the complete storage root together and grant the API process read/write access only to that root. Stale staging directories may be inspected operationally; v1 does not delete them automatically.

Allowed uploads are one `.eml` or `.msg` reference email and one PNG, JPEG, or WebP image, each up to 10 MiB and 20 MiB total. Images are decoded and checked for matching type. MSG files require an OLE compound-file signature. EML files require parseable message headers.

SMTP recipients come from comma-separated `SMTP_TO`, `SMTP_CC`, and `SMTP_BCC`. BCC recipients are passed only in the SMTP envelope. User content is HTML-escaped, a plain-text alternative is included, and attachments retain only a sanitized display filename.

SMTP cannot provide a transaction spanning the remote mail server and SQL Server. A process crash after SMTP accepts a message but before `SENT` is recorded can leave `PENDING`; blindly retrying could duplicate mail, so reconciliation is intentionally manual.

## Deployment security

This MVP does not include application-level authentication. Deploy the API and frontend only behind the organization's authenticated access gateway, restrict network access to employees, and rate-limit `POST /api/v1/project-updates`. Do not expose the API directly to the public internet.

Configure the reverse proxy or ingress with a request-body limit of 20 MiB. FastAPI parses multipart bodies before application upload validation runs, so the proxy limit is required to reject oversized requests early. Keep the backend per-file and aggregate checks enabled as defense in depth.

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