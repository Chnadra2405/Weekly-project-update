---
name: reviewer-code-duplication
description: Code duplication detection checklist. Finds duplicated or near-duplicated logic (functions, validation rules, SQL queries, regex literals, business conditionals) across the codebase. Use when a caller needs to verify the diff does not reintroduce known duplication patterns and return a structured list of findings — no rapport formatting.
---

This skill provides the **checklist** and **traceability rules** for a code-duplication review. The caller loads this skill, applies it to a scope, and gets back a flat list of findings. Formatting is the caller's responsibility.

## When to load this skill (triggers)

Apply when the diff contains code that could realistically embed copy/pasted logic:

- Source files of any executable language: `.cs`, `.ts`, `.js`, `.py`, `.java`, `.go`, `.rb`, `.php`, `.sql`, `.ps1`.
- Files containing SQL fragments (anywhere they appear).

Skip when:

- The diff is documentation, static assets (CSS/images/HTML markup only), or pipeline configs.
- The diff is a pure rename, a comment change, or a formatting-only change (no logic added).
- The scope is a **single small file** with no other files of the same language in the project — there is nothing to duplicate against.

## How to apply

1. **Scope**: the caller provides the file list (and optionally a `threshold` for similarity, default `80`). If none is provided, scan `src/`.
2. **Normalize candidates**: by language — strip comments, normalize whitespace, collapse identifiers — so structural comparison is possible.
3. **Detect exact duplicates** first: identical files or identical method/function bodies (byte or token match).
4. **Detect near-duplicates** using:
   - token sequence similarity (n-gram / shingling) above `threshold`;
   - normalized AST subtree similarity for typed languages (C#, Java, TypeScript) above `threshold`;
   - repeated SQL query text or near-identical queries across files;
   - repeated validation rules (same checks, different messages);
   - repeated regex literals or repeated literal constants used semantically (not single tokens).
5. **Group** findings by logical unit (method/function/SQL/regex). De-duplicate overlapping pairs — one group per logical duplicate.

## Checklist

Each finding MUST cite one of the `checklist_id` values below.

- **DUP-EXACT** Exact file or method/function body duplicated verbatim in two or more locations.
- **DUP-NEAR** Method/function bodies with normalized similarity ≥ threshold across two or more locations.
- **DUP-VALIDATION** Same validation rule (same conditional checks, possibly different error messages) implemented in two or more places — typically UI and service.
- **DUP-SQL** Same or near-identical SQL query text appearing in two or more files.
- **DUP-REGEX** Same regex literal repeated in two or more files (one is fine if local; two implies a shared concept).
- **DUP-CONSTANT** Same business literal value (magic number, magic string with semantic meaning) repeated in two or more files without a shared constant.
- **DUP-UI** Copy/pasted UI component logic (same lifecycle / data-loading / event-handler block in two or more components).

## Output rules

### Right to find nothing

If after applying every checklist item to the scope, no duplication group above `threshold` emerges, return an **empty findings list**. This is the expected outcome for tightly factored code. Do not invent findings; do not flag two-line snippets as duplicates.

### Traceability constraint (no inflation)

Each finding MUST:

- cite the **primary** location as `file:line-line` and list the other locations in the `finding` text as `file:line-line` for each;
- reference a specific `checklist_id` (e.g. `DUP-VALIDATION`);
- include a similarity score (0–100) for `DUP-NEAR`, `DUP-VALIDATION`, `DUP-UI`; report `100` for `DUP-EXACT`, `DUP-SQL`, `DUP-REGEX`, `DUP-CONSTANT`;
- propose a concrete extraction target (shared service, validator, SQL view/stored proc, constants module, helper).

A finding without a `checklist_id` is forbidden. A finding for a duplicate pair where one of the locations is trivial boilerplate (< 5 statements and < 30 tokens) is forbidden.

### Severity mapping

- **Blocker**: duplicated security check or duplicated business rule with conflicting branches (the two copies disagree) — `DUP-VALIDATION` with divergence.
- **Major**: large method duplicated (≥ 30 statements) — `DUP-EXACT`, `DUP-NEAR`. Duplicated SQL on the same domain concept — `DUP-SQL`.
- **Minor**: duplicated regex / business constant — `DUP-REGEX`, `DUP-CONSTANT`. Duplicated UI block — `DUP-UI`.
- **Info**: near-miss below threshold worth a manual look (do not raise routinely; only when the caller asked for low-confidence hints).

### Output schema

Return a flat array, one row per duplicate group, fields in this exact order:

```
severity | file | line | checklist_id | finding | recommendation
```

`file:line` is the **primary** location. The `finding` text MUST include the other locations and the similarity score:

```
"DUP-NEAR (sim=87): also at src/B.cs:42-78, src/C.cs:11-47 — duplicated `ValidateOrder` body"
```

Sort by severity descending, then by similarity descending. No HTML, no markdown — the caller formats.

### Determinism

Apply mechanically. Re-running on the same input must produce the same groups in the same order.

### Hints for callers

- For Zephyr (US implementation review): apply only to **added or modified** code, not to the full repo. Detecting that pre-existing duplication still exists is not in scope of a per-US review.
- For a refactoring audit: apply to the full scope provided.
