---
name: reviewer-rgaa-accessibility
description: RGAA 4.1.2 accessibility review checklist — 106 criteria across 13 themes, aligned with WCAG 2.1 AA. Covers images, frames, colors, multimedia, tables, links, scripts, mandatory elements, structure, presentation, forms, navigation, consultation. Use when a caller needs to verify accessibility against a fixed checklist and return a structured list of findings — no rapport formatting.
---

This skill provides the **checklist** and **traceability rules** for a RGAA 4.1.2 accessibility review. The caller loads this skill, applies it to a scope, and gets back a flat list of findings. Formatting is the caller's responsibility.

## When to load this skill (triggers)

Apply when the diff contains any user-facing rendering surface:

- HTML / templates: `.html`, `.htm`, `.cshtml`, `.razor`, `.vue`, `.svelte`, `.jsx`, `.tsx`.
- Styling: `.css`, `.scss`, `.sass`, `.less` (theme 3 colors / contrast, theme 10 presentation).
- Component / page source files that emit DOM.

Skip only when the diff has zero user-facing rendering: pure backend services, configuration, scripts, or documentation.

## How to apply

1. **Scope**: the caller provides the file list. If none is provided, fall back to `src/`.
2. **Theme restriction** (optional): if the caller specifies one or more themes (e.g. `themes=[3,11]`), evaluate only those. Default = all 13 themes.
3. For each criterion in scope: assign one status — **Pass**, **Fail**, **Warning** (cannot be statically verified — needs manual / AT testing), or **N/A** (element type provably absent).
4. Cite the exact HTML element, line number, CSS rule, or component name for every Fail / Warning.
5. Produce only Fail / Warning rows in the findings list. Pass and N/A counts are summary-level and the caller can request them separately.

## Checklist — 13 Themes / 106 criteria

Each finding MUST cite one of the `checklist_id` values below (`RGAA-X.Y`).

### Theme 1 – Images
- **RGAA-1.1** Each image conveying information has a text alternative (`alt`, `aria-label`, `role="img"` + label for `<svg>`).
- **RGAA-1.2** Decorative images ignored by AT (`alt=""`, `role="presentation"`, or `aria-hidden="true"`).
- **RGAA-1.3** Text alternatives for informative images are relevant and meaningful.
- **RGAA-1.4** CAPTCHA/test images: alternative describes nature/function, not content.
- **RGAA-1.5** CAPTCHA images: accessible alternative access method provided.
- **RGAA-1.6** Complex images (charts, diagrams) have a detailed description when needed.
- **RGAA-1.7** Detailed descriptions for complex images are accurate.
- **RGAA-1.8** Text images replaced with actual styled text where no replacement mechanism exists.
- **RGAA-1.9** Image with caption: `<figure>` + `<figcaption>` + matching `aria-label`.

### Theme 2 – Frames
- **RGAA-2.1** Each `<iframe>` / `<frame>` has a `title` attribute.
- **RGAA-2.2** Frame `title` is meaningful and descriptive.

### Theme 3 – Colors
- **RGAA-3.1** Information never conveyed by color alone (text, images, CSS).
- **RGAA-3.2** Text contrast ratios: ≥ 4.5:1 for text < 24px normal / < 18.5px bold; ≥ 3:1 for large text.
- **RGAA-3.3** UI components and graphical elements conveying information: ≥ 3:1 contrast against adjacent background.

### Theme 4 – Multimedia
- **RGAA-4.1** Pre-recorded audio/video/synchronized media: transcript or audio description provided.
- **RGAA-4.2** Transcripts / audio descriptions accurate and relevant.
- **RGAA-4.3** Pre-recorded synchronized media has captions (`<track kind="captions">`).
- **RGAA-4.4** Captions are accurate.
- **RGAA-4.5** Pre-recorded media has synchronized audio description when needed.
- **RGAA-4.6** Audio descriptions are relevant.
- **RGAA-4.7** Media clearly identified by adjacent text.
- **RGAA-4.8** Non-time-based media has an accessible alternative.
- **RGAA-4.9** Non-time-based media alternative is relevant.
- **RGAA-4.10** Auto-playing audio ≤ 3 s or user-controllable.
- **RGAA-4.11** Time-based media player controls keyboard- and pointer-accessible.
- **RGAA-4.12** Non-time-based media controls keyboard- and pointer-accessible.
- **RGAA-4.13** Media compatible with assistive technologies.

### Theme 5 – Tables
- **RGAA-5.1** Complex data tables have a summary.
- **RGAA-5.2** Table summary is relevant.
- **RGAA-5.3** Layout tables: linearized content understandable; no `<th>`, `<caption>`, `scope`, `headers`.
- **RGAA-5.4** `<caption>` correctly associated with its `<table>`.
- **RGAA-5.5** Table title is relevant.
- **RGAA-5.6** Column and row headers identified with `<th>` and `scope`.
- **RGAA-5.7** Data cells associated with headers via `scope` or `headers`/`id`.
- **RGAA-5.8** Layout tables contain no data-table markup.

### Theme 6 – Links
- **RGAA-6.1** Each link has an explicit, unambiguous purpose (link text or accessible name + context).
- **RGAA-6.2** Each link has non-empty link text / accessible name.

### Theme 7 – Scripts
- **RGAA-7.1** Scripts compatible with AT (ARIA roles, states, keyboard events).
- **RGAA-7.2** Script alternatives are relevant.
- **RGAA-7.3** Scripts controllable by keyboard and pointing device.
- **RGAA-7.4** Context changes initiated by scripts: user warned or given control.
- **RGAA-7.5** Status messages announced via `role="status"`, `role="alert"`, or `aria-live`.

### Theme 8 – Mandatory Elements
- **RGAA-8.1** Page has a valid `<!DOCTYPE>`.
- **RGAA-8.2** Generated source code validates per the declared doctype.
- **RGAA-8.3** Default language declared (`<html lang="...">`).
- **RGAA-8.4** Language code is valid (BCP 47).
- **RGAA-8.5** Page has a `<title>`.
- **RGAA-8.6** `<title>` is relevant and descriptive.
- **RGAA-8.7** Language changes in content indicated with `lang` attribute.
- **RGAA-8.8** Inline `lang` codes are valid.
- **RGAA-8.9** HTML tags not used for presentation only (no `<b>`, `<i>`, `<u>` for style).
- **RGAA-8.10** Text direction changes indicated with `dir`.

### Theme 9 – Information Structure
- **RGAA-9.1** Content structured with appropriate, hierarchically ordered headings (`<h1>`–`<h6>`).
- **RGAA-9.2** Document structure consistent: `<header>`, `<main>`, `<nav>`, `<footer>`, landmark roles.
- **RGAA-9.3** Lists marked up with `<ul>`, `<ol>`, `<dl>`.
- **RGAA-9.4** Quotations marked with `<blockquote>` or `<q>`.

### Theme 10 – Information Presentation
- **RGAA-10.1** CSS used to control presentation; content not embedded in stylesheets.
- **RGAA-10.2** Visible informative content present when CSS disabled.
- **RGAA-10.3** Content comprehensible without CSS.
- **RGAA-10.4** Text readable when font size increased to 200%.
- **RGAA-10.5** Foreground and background colors declared together.
- **RGAA-10.6** Links visually distinguishable from surrounding text by more than color.
- **RGAA-10.7** Focus indicator visible for all focusable elements.
- **RGAA-10.8** No information lost when text spacing adjusted (WCAG 1.4.12).
- **RGAA-10.9** Content not hidden by overlapping text when magnified.
- **RGAA-10.10** Content operable in both portrait and landscape.
- **RGAA-10.11** No horizontal scroll at 320 px width; no vertical scroll at 256 px height.
- **RGAA-10.12** Text spacing properties can be overridden without loss of content.
- **RGAA-10.13** Hover/focus additional content dismissible, hoverable, persistent.
- **RGAA-10.14** CSS-triggered additional content reachable by keyboard and pointer.

### Theme 11 – Forms
- **RGAA-11.1** Each form field has a label (`<label for>`, `aria-label`, `aria-labelledby`, `title`).
- **RGAA-11.2** Field labels are relevant.
- **RGAA-11.3** Fields appearing multiple times have consistent labels.
- **RGAA-11.4** Labels and fields visually proximate.
- **RGAA-11.5** Related fields grouped with `<fieldset>` or `role="group"`.
- **RGAA-11.6** Field groups have a `<legend>` or `aria-labelledby`.
- **RGAA-11.7** Group legends are relevant.
- **RGAA-11.8** `<select>` options grouped with `<optgroup>` when appropriate.
- **RGAA-11.9** Submit/action button text is relevant.
- **RGAA-11.10** Client-side validation errors programmatically associated with fields (`aria-describedby`, `aria-invalid`).
- **RGAA-11.11** Error messages include correction suggestions.
- **RGAA-11.12** Forms with legal/financial consequences allow review, correction, or confirmation.
- **RGAA-11.13** Personal data fields have `autocomplete` (WCAG 1.3.5).

### Theme 12 – Navigation
- **RGAA-12.1** At least two navigation mechanisms provided (menu, search, sitemap).
- **RGAA-12.2** Navigation landmarks consistently located across pages.
- **RGAA-12.3** Sitemap page is meaningful, complete, functional.
- **RGAA-12.4** Sitemap link consistently located.
- **RGAA-12.5** Search engine consistently reachable.
- **RGAA-12.6** Skip links allow bypassing repeated blocks.
- **RGAA-12.7** Skip-to-main-content link present and functional.
- **RGAA-12.8** Tab order is logical and coherent.
- **RGAA-12.9** No keyboard traps.
- **RGAA-12.10** Single-key shortcuts remappable or disableable.
- **RGAA-12.11** Hover/focus/activation additional content keyboard-accessible.

### Theme 13 – Consultation
- **RGAA-13.1** Time limits can be paused, extended, or disabled.
- **RGAA-13.2** New windows not opened without user action; `target="_blank"` warned.
- **RGAA-13.3** Downloadable office documents have an accessible version if needed.
- **RGAA-13.4** Accessible alternative version provides the same information.
- **RGAA-13.5** Cryptic content (ASCII art, emoticons) has an accessible alternative.
- **RGAA-13.6** Cryptic content alternatives are relevant.
- **RGAA-13.7** Flashing/blinking within safe limits (< 3 Hz or thresholds).
- **RGAA-13.8** Auto-moving/blinking content user-controllable.
- **RGAA-13.9** Content operable regardless of screen orientation.
- **RGAA-13.10** Complex pointer gestures have a single-point alternative.
- **RGAA-13.11** Actions on pointer down-event cancellable or reversible.
- **RGAA-13.12** Device-motion-triggered functions have an alternative input.

## Output rules

### Right to find nothing

If after applying every applicable criterion to every in-scope file, no Fail and no Warning emerges, return an **empty findings list**. This is the expected outcome for an accessible UI. Pass and N/A statuses are not included in the findings list — only Fail and Warning. Do not invent findings.

### Traceability constraint (no inflation)

Each finding MUST:

- cite an exact `file:line` (or `file:line-line` for a range);
- reference a specific `checklist_id` (e.g. `RGAA-1.1`);
- describe a concrete failure or a precise reason the criterion needs manual verification;
- propose a minimal, concrete fix (the exact attribute / role / structure change).

A finding without a `checklist_id` is forbidden. A finding for a criterion that is provably N/A (no `<img>` in scope → no RGAA-1.x findings) is forbidden.

### Severity mapping

- **Blocker**: blocks access entirely for an AT user — missing `alt` on critical content image (`RGAA-1.1`), keyboard trap (`RGAA-12.9`), unlabeled form field (`RGAA-11.1`), contrast < 3:1 on essential text (`RGAA-3.2`).
- **Major**: significantly degrades AT experience — missing landmark structure (`RGAA-9.2`), missing skip link on multi-section page (`RGAA-12.7`), missing `title` on iframe (`RGAA-2.1`).
- **Minor**: degrades experience but workable — missing `lang` on inline foreign-language span (`RGAA-8.7`), missing `<optgroup>` on long `<select>` (`RGAA-11.8`).
- **Info / Warning**: criterion requires manual verification (screen reader test, 200% zoom test, AT testing) — `RGAA-7.5`, `RGAA-10.7` are typical examples.

### Output schema

Return a flat array, one row per finding, fields in this exact order:

```
severity | file | line | checklist_id | finding | recommendation
```

Sort by severity descending, then by `checklist_id` ascending. No HTML, no markdown headers — the caller formats.

### Determinism

Apply mechanically. Two runs on the same input must produce the same findings in the same order.
