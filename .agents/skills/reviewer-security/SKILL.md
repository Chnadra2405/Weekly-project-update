---
name: reviewer-security
description: Security review checklist mapped to OWASP Top 10 (2021). Auto-enriches with .NET/ASP.NET Core/Blazor/EF Core checks when `.csproj` files are present. Use when a caller needs to verify code against a fixed OWASP checklist and return a structured list of findings — no rapport formatting.
---

This skill provides the **checklist** and **traceability rules** for an OWASP security review. The caller loads this skill, applies it to a scope, and gets back a flat list of findings. Formatting is the caller's responsibility.

## When to load this skill (triggers)

Apply when the diff contains any of:

- Source files of an executable language: `.cs`, `.ts`, `.js`, `.py`, `.java`, `.go`, `.rb`, `.php`, `.ps1`, `.sh`, `.sql`.
- Configuration files that touch auth, secrets, transport, or CI/CD: `Dockerfile`, `*.yml` / `*.yaml` (pipelines), `appsettings*.json`, `.env*`, `web.config`.
- UI files that have an XSS / CSRF / external-link surface: `.html`, `.htm`, `.razor`, `.cshtml`, `.vue`, `.svelte`, `.tsx`, `.jsx`.

Skip **only** when the diff is 100% pure static assets (`.css`, `.md`, `.txt`, `.svg`, images, fonts). The cost of loading this skill in vain is low (it returns 0 findings on truly inert content); the cost of skipping it on code is a potential vulnerability.

## How to apply

1. **Scope**: the caller provides the file list. If none is provided, fall back to `src/` (or the repo root if no `src/`).
2. **Tech detection**: search for `*.csproj` in scope. If any are found, set `isDotNet = true` and apply the .NET enrichment in step 4.
3. **Generic analysis**: walk the 10 OWASP categories below. For each criterion, evaluate against each in-scope file. A category that has no surface in the diff (e.g. A07 on a pure UI file) is silently skipped.
4. **.NET enrichment** (only if `isDotNet = true`): read `development-generic/.apm/skills/dotnet-review-criteria/references/owasp-security-dotnet.md` and apply every criterion listed there. These are **additive** — do not re-evaluate criteria already covered generically. If the reference file is not found, record `severity=Info, checklist_id=ENV, finding="Dotnet enrichment skipped — reference file missing"` and continue.

## Checklist — OWASP Top 10 (2021)

Each finding MUST cite one of the `checklist_id` values below.

### A01 – Broken Access Control

- **A01-G1** Authentication required for all routes/endpoints exposing non-public data or actions.
- **A01-G2** Authorization checks performed server-side; no reliance on client-supplied roles or flags.
- **A01-G3** No insecure direct object references — user-supplied IDs validated against the current user's ownership.
- **A01-G4** CORS policy is restrictive; `*` (wildcard) origin not combined with credentials.
- **A01-G5** No privilege escalation through request parameters or form fields.

### A02 – Cryptographic Failures

- **A02-G1** Sensitive data (passwords, tokens, PII, financial data) not logged, not exposed in error messages, and not returned in full in API responses.
- **A02-G2** Passwords stored using a strong adaptive hash (bcrypt, Argon2, scrypt, PBKDF2); no MD5, SHA-1, or unsalted hashes.
- **A02-G3** All connections to external services and databases use TLS; no plaintext HTTP for sensitive data transfer.
- **A02-G4** No hardcoded secrets, API keys, passwords, or tokens in source files, configuration files, or committed `.env` files.
- **A02-G5** Tokens (JWT, OAuth, session) validated for signature, expiry, issuer, and audience; `none` algorithm or unsigned tokens rejected.
- **A02-G6** Sensitive cookies marked `Secure`, `HttpOnly`, and `SameSite=Strict` (or `Lax`).

### A03 – Injection

- **A03-G1** All database queries use parameterized queries or an ORM with safe query building — no string concatenation with user input.
- **A03-G2** No user-controlled input passed directly to shell commands, `exec`, `eval`, or OS-level APIs.
- **A03-G3** HTML output encodes user-supplied content; no raw user input rendered into HTML/DOM (XSS).
- **A03-G4** User-supplied file paths sanitized before disk access; no path traversal via `..` sequences.
- **A03-G5** XML parsing disables external entity processing (XXE).
- **A03-G6** LDAP and XPath queries use parameterized or escaped inputs.

### A04 – Insecure Design

- **A04-G1** Sensitive workflows (password reset, account deletion, payment) include rate limiting, confirmations, or challenge steps.
- **A04-G2** Business logic cannot be bypassed by replaying, reordering, or forging requests.
- **A04-G3** File upload endpoints restrict allowed MIME types and extensions; uploaded files not executed from server-accessible paths.
- **A04-G4** Mass assignment prevented — only explicitly allowed fields accepted from user input.

### A05 – Security Misconfiguration

- **A05-G1** Detailed error messages, stack traces, and debug information not exposed in production responses.
- **A05-G2** Security headers configured **in source code or deployment config the diff actually touches**: `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy`. Do not raise A05-G2 against pure HTML/CSS diffs that do not configure a server — headers are a runtime concern.
- **A05-G3** Administrative, diagnostic, and documentation endpoints (`/swagger`, `/healthz`, `/admin`) protected or disabled in production.
- **A05-G4** Default credentials changed; no well-known default usernames/passwords in deployed configuration.
- **A05-G5** HTTPS enforced; HTTP redirected to HTTPS in production.

### A06 – Vulnerable and Outdated Components

- **A06-G1** Dependency manifest files (`package.json`, `requirements.txt`, `pom.xml`, `*.csproj`, `Gemfile.lock`) audited for known CVEs.
- **A06-G2** Runtime and framework versions supported (no EOL runtimes in production).

### A07 – Identification and Authentication Failures

- **A07-G1** Session tokens have a defined expiry; no indefinite sessions.
- **A07-G2** Brute-force protection on authentication endpoints (rate limiting or lockout).
- **A07-G3** Password reset / account recovery flow does not reveal whether an account exists.
- **A07-G4** Session invalidated on logout.

### A08 – Software and Data Integrity Failures

- **A08-G1** Deserialization of user-supplied data does not allow arbitrary type instantiation.
- **A08-G2** External scripts, fonts, and CDN resources use Subresource Integrity (SRI) hashes **when loaded from a CDN**. Do not raise A08-G2 against locally-served scripts/styles.
- **A08-G3** CI/CD pipeline does not consume unverified or unsigned artifacts.

### A09 – Security Logging and Monitoring Failures

- **A09-G1** Authentication failures and successful logins are logged.
- **A09-G2** Authorization failures (access denied events) are logged with user context.
- **A09-G3** Sensitive data (passwords, full tokens, PII) never written to logs.
- **A09-G4** Log injection prevented — user-supplied strings not directly interpolated into log messages.

### A10 – Server-Side Request Forgery (SSRF)

- **A10-G1** HTTP requests to user-supplied URLs restricted to an allowlist of trusted domains.
- **A10-G2** Internal network ranges (loopback, RFC1918 private IPs) blocked when making outbound requests triggered by user input.

### UI-specific (covered above, listed here for navigation)

- External links with `target="_blank"` must also carry `rel="noopener noreferrer"` — covered by **A05-G2** (misconfiguration). A missing `rel` is a Major.
- Forms with state-changing actions must include CSRF protection — covered by **A01-G2**.
- User-supplied content rendered into the DOM must be escaped — covered by **A03-G3**.

## Output rules

### Right to find nothing

If after applying every checklist item to every in-scope file, no concern emerges, return an **empty findings list**. This is the expected outcome for code with no exposed attack surface. Do not invent findings.

### Traceability constraint (no inflation)

Each finding MUST:

- cite an exact `file:line`;
- reference a specific `checklist_id` from the list above (e.g. `A03-G3`);
- describe a concrete vulnerability rooted in the code, not a runtime assumption ("the deployed server might lack header X" without a deployment config in the diff is forbidden);
- propose a minimal, concrete fix.

A finding without a `checklist_id` is forbidden. If you cannot map a concern to a listed id, drop it.

### Severity mapping

- **Blocker**: exploitable, data-breach or full-compromise risk — `A03-G1` SQL injection, `A02-G4` hardcoded secret, `A01-G2` missing server-side auth.
- **Major**: significant risk, likely exploitable in context — missing `rel="noopener noreferrer"` (A05-G2), missing CSRF on state-changing form (A01-G2), `A02-G6` missing `HttpOnly`.
- **Minor**: defense-in-depth — `A08-G2` missing SRI on local script copy (false positive territory, but record as Minor).
- **Info**: observation worth knowing, no actionable defect — e.g. "diff contains no auth surface; A01/A07 trivially N/A".

### Output schema

Return a flat array, one row per finding, fields in this exact order:

```
severity | file | line | checklist_id | finding | recommendation
```

Sort by severity descending, then by file/line. No HTML, no markdown headers — the caller formats.

### Determinism

Apply mechanically. Do not pick "interesting" findings — return all that the checklist matches and nothing else.
