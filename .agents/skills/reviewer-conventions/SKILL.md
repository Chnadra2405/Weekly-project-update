---
name: reviewer-conventions
description: Code conventions & best-practices review checklist. Naming, code structure, async patterns, error handling, SOLID, hygiene. Auto-enriches with .NET/C#/Blazor/EF Core checks when `.csproj` files are present. Use when a caller needs to verify code against a fixed checklist of conventions and return a structured list of findings — no rapport formatting.
---

This skill provides the **checklist** and **traceability rules** for a code-conventions review. The caller (an agent, a Zephyr step, or a developer) loads this skill, applies it to a scope, and gets back a flat list of findings. Formatting the findings into a human report is the caller's responsibility.

## When to load this skill (triggers)

- **Default: always.** Code = conventions. There is no diff for which this skill is irrelevant.
- Skip only when there is no source file in scope at all (e.g. a doc-only commit).

## How to apply

1. **Scope**: the caller provides the file list. If none is provided, fall back to `src/` (or the repo root if no `src/`).
2. **Tech detection**: search for `*.csproj` in scope. If any are found, set `isDotNet = true` and apply the .NET enrichment in step 4.
3. **Generic analysis**: walk the checklist below, evaluate each criterion against each in-scope file. A criterion that does not apply to a given file is silently skipped (no finding).
4. **.NET enrichment** (only if `isDotNet = true`): read `development-generic/.apm/skills/dotnet-review-criteria/references/conventions-dotnet.md` and apply every criterion listed there. These are **additive** — do not re-evaluate criteria already covered generically. If the reference file is not found, record a single warning row `severity=Info, checklist_id=ENV, finding="Dotnet enrichment skipped — reference file missing"` and continue.

## Checklist

Each finding MUST cite one of the `checklist_id` values below (`G1.1`, `G2.4`, …). A concern that cannot be mapped to a listed id does not belong in the output.

### G1 – Naming

- **G1.1** Names are descriptive and convey intent without requiring a comment to understand.
- **G1.2** Boolean variables, properties, and functions named as predicates (`isValid`, `hasPermission`, `canSubmit`).
- **G1.3** No single-letter names except loop counters (`i`, `j`, `k`) and universally understood abbreviations (`id`, `url`).
- **G1.4** No misleading names (a function named `getUser` does not also mutate state; a variable named `count` does not hold a string).
- **G1.5** Consistent casing convention used throughout the codebase (follow the language-idiomatic style).

### G2 – Code Structure & Readability

- **G2.1** Functions/methods do one thing and are no longer than ~40 lines.
- **G2.2** Classes/modules have a single, well-defined responsibility; no god objects.
- **G2.3** Guard clauses (early returns / early throws) preferred over deeply nested `if`/`else` blocks.
- **G2.4** No commented-out code blocks left in production files.
- **G2.5** No `TODO` / `FIXME` / `HACK` comments without an associated ticket or work item reference.
- **G2.6** Magic numbers and magic strings replaced with named constants or configuration values.
- **G2.7** No unused imports, unused variables, or unused function parameters.

### G3 – Async & Concurrency

- **G3.1** No blocking calls on asynchronous operations (`.Wait()`, `.Result`, `sync_to_async` misuse, etc.).
- **G3.2** Fire-and-forget async operations are intentional and documented; accidental unhandled async errors not possible.
- **G3.3** Shared mutable state accessed concurrently is protected by appropriate synchronization.

### G4 – Error Handling

- **G4.1** Exceptions / errors not silently swallowed — empty `catch {}` / bare `except:` blocks prohibited.
- **G4.2** Specific error types caught; generic catch-all used only at the outermost boundary.
- **G4.3** Error messages informative for developers but do not leak sensitive implementation details to end users.
- **G4.4** Errors logged at the point of occurrence with sufficient context (file, function, relevant inputs where safe).

### G5 – SOLID Principles

- **G5.1** **Single Responsibility** — each class/module has one reason to change; god classes split.
- **G5.2** **Open/Closed** — behavior extended via interfaces, inheritance, or composition; not by modifying existing classes.
- **G5.3** **Liskov Substitution** — derived classes fully honor the contract of their base type.
- **G5.4** **Interface Segregation** — interfaces are small and focused; no "fat" interfaces.
- **G5.5** **Dependency Inversion** — high-level modules depend on abstractions; concrete types not instantiated inside business logic.

### G6 – Code Hygiene

- **G6.1** No dead code (unreachable branches, unused private/internal functions, parameters never read).
- **G6.2** No duplicate code blocks — shared logic extracted to a helper or utility. (Defer detailed duplication detection to `reviewer-code-duplication`; here only flag blatant cases.)
- **G6.3** No deeply nested control flow (> 3 levels is a smell).
- **G6.4** Consistent formatting and indentation across the codebase (enforced by formatter/linter).

## Output rules

### Right to find nothing

If after applying every checklist item to every in-scope file, no concern emerges, return an **empty findings list**. This is the expected and preferred outcome for clean code. Do not invent findings.

### Traceability constraint (no inflation)

Each finding MUST:

- cite an exact `file:line` (or `file:line-line` for a range);
- reference a specific `checklist_id` from the list above (e.g. `G3.1`);
- describe a concrete issue, not a stylistic preference;
- propose a minimal, concrete fix.

A finding that cannot satisfy all four points is forbidden. If you cannot map a concern to a listed `checklist_id`, do not include it.

### Severity mapping

- **Blocker**: correctness risk that will manifest at runtime — deadlocks (G3.1), swallowed exceptions hiding failures (G4.1), unhandled async errors (G3.2).
- **Major**: maintainability or testability degradation that compounds — god classes (G2.2, G5.1), magic strings/numbers in business logic (G2.6), dependency inversion violation (G5.5).
- **Minor**: localized smell — single function too long (G2.1), commented-out code (G2.4), unused imports (G2.7).
- **Info**: cosmetic / style — naming preferences when the existing name is unambiguous (G1.1).

### Output schema

Return a flat array, one row per finding, fields in this exact order:

```
severity | file | line | checklist_id | finding | recommendation
```

Sort the array by severity descending (Blocker → Major → Minor → Info), then by file/line. No HTML, no markdown headers, no executive summary — the caller formats.

### Determinism

This skill expects deterministic output: apply the checklist mechanically. Do not pick "interesting" findings — return all that the checklist matches.
