# Weekly Project Update (WPU) – Requirements

## Overview

WPU is a web application for collecting and storing weekly project status updates from teams. Each team submits one report per week covering achievements, ongoing initiatives, and next week's plans. The system enforces one report per team per 7-day window, supports safe re-submission via idempotency, and provides role-based access so employees, managers, and admins see the appropriate scope of data.

---

## Functional Requirements

### Authentication & User Management

| ID | Requirement |
|----|-------------|
| AUTH-01 | Users must register with a unique username, unique email address, password, and role (EMPLOYEE, MANAGER, or ADMIN). |
| AUTH-02 | Users must be able to log in with their username and password and receive a JWT access token in response. |
| AUTH-03 | All project-update endpoints must require a valid JWT token in the `Authorization` header. |
| AUTH-04 | The JWT payload must include the user's ID, username, and role. |
| AUTH-05 | Passwords must be stored as a secure hash; plaintext passwords must never be persisted. |

### Report Submission

| ID | Requirement |
|----|-------------|
| SUB-01 | An authenticated user must be able to submit a weekly project update containing: team/project name, start date, end date, achievements, initiatives, and next week's plan. |
| SUB-02 | The end date must equal the start date plus exactly 6 days (a full 7-day week). The system must reject submissions where this constraint is not met. |
| SUB-03 | Each submission must include a client-supplied idempotency key. Re-submitting the same key with identical content must return the existing record (HTTP 200) without creating a duplicate. |
| SUB-04 | Re-submitting the same idempotency key with different content must be rejected with HTTP 409 Conflict. |
| SUB-05 | The system must expose an endpoint to check whether a report already exists for a given team and week before submission. |
| SUB-06 | The team/project name must not exceed 300 characters. |
| SUB-07 | The achievements, initiatives, and next week's plan fields must each not exceed 5,000 characters. |

### Report Retrieval & Listing

| ID | Requirement |
|----|-------------|
| RET-01 | An authenticated user must be able to retrieve a list of project updates filtered by their role (see Role-Based Access below). |
| RET-02 | An authenticated user must be able to retrieve a single project update by its ID, subject to role-based access rules. |
| RET-03 | Report listings must support grouping by current month vs. older reports. |

### Report Editing

| ID | Requirement |
|----|-------------|
| EDIT-01 | The owner of a report must be able to edit its content after initial submission. |
| EDIT-02 | Users who do not own a report must not be permitted to edit it (EMPLOYEE role). |

### Role-Based Access Control

| Role | Access Scope |
|------|-------------|
| **EMPLOYEE** | May submit and edit their own reports; may only view their own reports. |
| **MANAGER** | May submit and view their own reports; may view reports submitted by team members. |
| **ADMIN** | Full read access to all reports across all teams; may edit any report. |

---

## Non-Functional Requirements

### Performance & Reliability

| ID | Requirement |
|----|-------------|
| NFR-01 | The API must expose `/api/v1/health/live` and `/api/v1/health/ready` liveness and readiness endpoints for deployment health checks. |
| NFR-02 | Idempotency handling must ensure that network retries do not create duplicate records. |

### Security

| ID | Requirement |
|----|-------------|
| SEC-01 | JWT tokens must be signed with a secret key configured via environment variable; the secret must never be hard-coded. |
| SEC-02 | CORS must be restricted to the configured list of allowed origins (not wildcard `*` in production). |
| SEC-03 | All HTML content rendered in the frontend must be sanitised (e.g. via DOMPurify) before display to prevent XSS. |
| SEC-04 | Database credentials and connection strings must be supplied through environment variables or a `.env` file and must not be committed to source control. |

### Usability

| ID | Requirement |
|----|-------------|
| UX-01 | The frontend must warn the user before submission if a report already exists for the selected team and week. |
| UX-02 | Date fields must auto-calculate the end date when the start date is selected (start + 6 days). |
| UX-03 | The application must be accessible; key UI flows must pass automated accessibility checks. |
| UX-04 | Rich text editing must be supported for the achievements, initiatives, and next week's plan fields. |

### Data Integrity

| ID | Requirement |
|----|-------------|
| DI-01 | The database must enforce a check constraint that `end_of_week = start_of_week + 6 days`. |
| DI-02 | The idempotency key must be unique across the `project_updates` table. |
| DI-03 | User email addresses and usernames must each be unique across the `users` table. |

---

## Technology Constraints

| Area | Constraint |
|------|-----------|
| Backend language | Python 3.12+ |
| Backend framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQL Server 2022 (ODBC Driver 18) |
| Migrations | Alembic |
| Frontend framework | React (Vite) |
| Node.js | 20+ |
| Containerisation | Docker Compose |
| API server | Uvicorn (ASGI) |

---

## Out of Scope

- Email / SMTP notifications (removed in migration 0002).
- File attachments (removed in migration 0002).
- Multi-tenancy beyond the single-organisation deployment model.
- External SSO / OAuth integration.
