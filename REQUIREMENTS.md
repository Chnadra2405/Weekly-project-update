# Weekly Project Update (WPU) – Requirements

## Overview

WPU is a web application for collecting and storing weekly project status updates from teams. Each team submits one report per week covering achievements, ongoing initiatives, and next week's plans. The system enforces one report per team per 7-day window, supports safe re-submission via idempotency, provides an approval workflow, and enforces role-based access so Team Leads, Team Managers, DU Heads, and Application Admins see the appropriate scope of data.

---

## Functional Requirements

### Authentication & User Management

| ID | Requirement |
|----|-------------|
| AUTH-01 | Users must register with a unique username, unique email address, password, role (`TEAM_LEAD`, `TEAM_MANAGER`, `DU_HEAD`, or `APP_ADMIN`), and an optional team name. |
| AUTH-02 | Users must be able to log in with their username and password and receive a JWT access token in response. |
| AUTH-03 | All project-update endpoints must require a valid JWT token in the `Authorization` header. |
| AUTH-04 | The JWT payload must include the user's ID, username, and role. |
| AUTH-05 | Passwords must be stored as a bcrypt hash; plaintext passwords must never be persisted. |
| AUTH-06 | An `APP_ADMIN` must be able to retrieve a list of all users, optionally filtered by role. |

### Report Submission

| ID | Requirement |
|----|-------------|
| SUB-01 | A `TEAM_LEAD` or `APP_ADMIN` must be able to submit a weekly project update containing: team/project name, start date, end date, achievements, initiatives, and next week's plan. |
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
| RET-04 | Report list and detail responses must include the owning user's username alongside the report data. |
| RET-05 | A `DU_HEAD` must only see reports with `approval_status` of `APPROVED` in the list, detail, and export endpoints. Draft reports must not be visible or exportable to a `DU_HEAD`. |

### Report Editing

| ID | Requirement |
|----|-------------|
| EDIT-01 | A `TEAM_LEAD` must be able to edit their own reports, provided the report has not yet been approved. |
| EDIT-02 | A `TEAM_LEAD` who does not own a report must not be permitted to edit it, unless they are an active delegate. |
| EDIT-03 | A `TEAM_MANAGER` or `APP_ADMIN` may edit any report that has not yet been approved. |
| EDIT-04 | An `APP_ADMIN` may edit any report regardless of approval status. |
| EDIT-05 | A `DU_HEAD` must not be permitted to edit any report. |

### Report Approval

| ID | Requirement |
|----|-------------|
| APPR-01 | Every report must carry an `approval_status` of either `DRAFT` (default) or `APPROVED`. |
| APPR-02 | A `TEAM_MANAGER` or `APP_ADMIN` must be able to approve a report, transitioning its status from `DRAFT` to `APPROVED`. |
| APPR-03 | A `TEAM_LEAD` who is an active delegate for a manager must be able to approve reports on that manager's behalf. |
| APPR-04 | Approving an already-approved report must be idempotent (return the existing record without error). |
| APPR-05 | The database must record who approved a report (`approved_by_id`) and when (`approved_at`). |

### Report Export

| ID | Requirement |
|----|-------------|
| EXP-01 | A `DU_HEAD` must be able to export all approved reports as a Microsoft Excel workbook (`.xlsx`). The exported file must include columns for team/project, week start, week end, owner, approval status, achievements, initiatives, and next week's plan. Rich-text HTML must be stripped to plain text in the export. |
| EXP-02 | A `DU_HEAD` must be able to export all approved reports as a Microsoft PowerPoint presentation (`.pptx`). Each report must be rendered on a separate slide showing the team/project name, date range, owner, approval status, and the three content fields. |

### Delegation

| ID | Requirement |
|----|-------------|
| DLGN-01 | An `APP_ADMIN` must be able to assign a `TEAM_LEAD` as an active delegate for a `TEAM_MANAGER`. |
| DLGN-02 | An active delegate must receive the same read and approval access as the manager they represent. |
| DLGN-03 | Delegation relationships must be persisted in a dedicated `delegations` table with audit fields (`created_by_id`, `is_active`, `created_at`). |

### Role-Based Access Control

| Role | Submission | View | Edit | Approve | Export |
|------|-----------|------|------|---------|--------|
| **TEAM_LEAD** | Own reports only | Own reports only (full visibility if active delegate) | Own unapproved reports only (delegate: any unapproved) | Only if active delegate | No |
| **TEAM_MANAGER** | No | All reports | Any unapproved report | Yes | No |
| **DU_HEAD** | No | Approved reports only | No | No | Yes (Excel & PowerPoint, approved reports only) |
| **APP_ADMIN** | Yes | All reports | Any report (including approved) | Yes | No |

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
| DI-04 | The `approval_status` column must be constrained to `DRAFT` or `APPROVED`. |
| DI-05 | The `role` column on the `users` table must be constrained to `APP_ADMIN`, `DU_HEAD`, `TEAM_MANAGER`, or `TEAM_LEAD`. |

---

## Technology Constraints

| Area | Constraint |
|------|-----------|
| Backend language | Python 3.12+ |
| Backend framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQL Server 2022 (ODBC Driver 18) |
| Migrations | Alembic |
| Password hashing | bcrypt (via `bcrypt` package) |
| Excel export | openpyxl |
| PowerPoint export | python-pptx |
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
