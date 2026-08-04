---
name: reviewer-separation-of-concerns
description: Architectural Separation-of-Concerns review checklist. Detects business logic in UI, presentation concerns in services, invalid dependency directions. Auto-enriches with .NET/EF Core/Blazor checks when `.csproj` files are present. Use when a caller needs to verify architectural layering and return a structured list of findings — no rapport formatting.
---

This skill provides the **checklist** and **traceability rules** for a Separation-of-Concerns review. The caller loads this skill, applies it to a scope, and gets back a flat list of findings. Formatting is the caller's responsibility.

## When to load this skill (triggers)

Apply when the diff touches any of:

- Source files in a layered codebase: anything under `src/`, `app/`, `lib/`, project source folders.
- UI/presentation files: `.razor`, `.cshtml`, `.html`, `.vue`, `.svelte`, `.tsx`, `.jsx`, files under `components/`, `pages/`, `views/`, `ui/`, `web/`.
- Service / business-logic files: under `services/`, `core/`, `domain/`, `use-cases/`, `application/`.
- Data-access files: under `data/`, `repositories/`, `infrastructure/`, `db/`, `dal/`.
- Dependency manifests: `package.json`, `pyproject.toml`, `pom.xml`, `*.csproj` (to detect cross-layer references).

Skip only when the diff is documentation-only, pure static assets (CSS/images/fonts), or pipeline/CI files with no application code.

## How to apply

1. **Scope**: the caller provides the file list. If none is provided, fall back to `src/`.
2. **Tech detection**: search for `*.csproj` in scope. If any are found, set `isDotNet = true` and apply the .NET enrichment in step 4.
3. **Identify the project structure** using directory layout, module names, and import patterns:

   | Layer | Typical Names | Responsibility |
   |-------|---------------|----------------|
   | UI / Presentation | `components/`, `pages/`, `views/`, `ui/`, `web/`, `frontend/` | Display, navigation, user interaction only |
   | Business Logic | `services/`, `core/`, `domain/`, `use-cases/`, `application/` | Domain rules, orchestration, validation |
   | Data Access | `data/`, `repositories/`, `infrastructure/`, `db/`, `dal/` | Persistence, external APIs, ORM |

   If no clear layer structure exists, scan the full scope and detect violations via import/dependency patterns alone (still apply the checklist).

4. **Generic analysis**: apply the checklist below.
5. **.NET enrichment** (only if `isDotNet = true`): read `development-generic/.apm/skills/dotnet-review-criteria/references/separation-of-concerns-dotnet.md` and apply every criterion listed there — additive only. If the reference file is not found, record `severity=Info, checklist_id=ENV, finding="Dotnet enrichment skipped — reference file missing"`.

## Checklist

Each finding MUST cite one of the `checklist_id` values below.

### SOC-UI – Business logic leaking into the UI layer

Check every file under the UI/Presentation layer:

- **SOC-UI-1** Direct data access — database queries, ORM calls, or raw persistence operations called directly from a UI component, page, or view.
- **SOC-UI-2** Domain decisions in UI — branching on business rules (pricing, eligibility, state transitions, permission logic) inside view/component code instead of delegating to a service.
- **SOC-UI-3** Non-trivial validation rules duplicated in the presentation layer that should live in a service or validator.
- **SOC-UI-4** UI component performing computation beyond simple display formatting.
- **SOC-UI-5** Direct HTTP calls to third-party or internal APIs made from a UI component instead of through a service abstraction.

### SOC-SVC – Presentation concerns leaking into services / data

Check every file under the Business Logic and Data Access layers:

- **SOC-SVC-1** Service returning UI-ready formatted strings (formatted dates, currency strings, localized messages) instead of domain objects.
- **SOC-SVC-2** Service or repository function accepting or returning types defined in the UI layer (view models, display enums, web-layer DTOs).
- **SOC-SVC-3** Display formatting (date/currency/number for human display) performed inside a service function.
- **SOC-SVC-4** Imports of UI framework packages (`react`, `vue`, `angular`, framework HTTP request/response objects) inside a service or data module.

### SOC-DEP – Dependency direction violations

- **SOC-DEP-1** Business Logic layer references the UI layer (upward dependency).
- **SOC-DEP-2** Data Access layer references the Business Logic or UI layer (except for shared interfaces/models).
- **SOC-DEP-3** Expected direction `UI → Business Logic → Data Access` violated by an import or project reference.
- **SOC-DEP-4** Dependency manifests (`package.json`, `*.csproj`, `pom.xml`) declare cross-layer references that break the expected graph.

## Output rules

### Right to find nothing

If after applying every checklist item, no violation emerges, return an **empty findings list**. This is the expected outcome for well-layered code. Do not invent findings.

### Traceability constraint (no inflation)

Each finding MUST:

- cite an exact `file:line`;
- reference a specific `checklist_id` (e.g. `SOC-UI-1`);
- describe a concrete violation — not a stylistic preference or a hypothetical concern about a layer that does not exist in this codebase;
- propose a minimal, concrete fix (extract to service, introduce mapper, invert dependency, etc.).

A finding without a `checklist_id` is forbidden.

### Severity mapping

- **Blocker**: dependency direction violation that breaks the build or creates a cycle — `SOC-DEP-1`, `SOC-DEP-2` with concrete project reference.
- **Major**: business logic in UI that bypasses authorization, validation, or domain rules — `SOC-UI-1`, `SOC-UI-2`.
- **Minor**: presentation concerns in services (formatting, display strings) — `SOC-SVC-1`, `SOC-SVC-3`.
- **Info**: observation only (e.g. "scope contains no UI layer; SOC-UI-* trivially N/A").

### Output schema

Return a flat array, one row per finding, fields in this exact order:

```
severity | file | line | checklist_id | finding | recommendation
```

Sort by severity descending, then by file/line. No HTML, no markdown headers — the caller formats.

### Determinism

Apply mechanically. Do not pick "interesting" violations — return every match from the checklist.
