---
name: prep-log
description: Append-only TSV prep log (decisions.tsv) and cross-vendor shift auditor for long-running, multi-course, or autonomous kitchen runs. Logs ts, phase, decision, why, evidence, and result with formula-injection sanitization. Use for /prep-log.
---

# Prep Log (`/prep-log`)

Keep one canonical, human-scannable prep log (`decisions.tsv`) during any multi-step or autonomous shift so the Head Chef can audit what was cooked, why, and what proved it in 30 seconds.

## 1. The Canonical TSV Format

Six tab-separated columns (`ts | phase | decision | why | evidence | result`), strictly single-line per row:
- **`ts`**: ISO-8601 UTC timestamp (`2026-11-27T07:50:00Z`).
- **`phase`**: Service phase, station name, or reduction iteration (`frame`, `host_triage`, `reduction-iter-1`, `check-the-oven`, `first-tables-10pct`).
- **`decision`**: One-line plain-English description of what was chosen or cooked.
- **`why`**: Plain-English reason (zero corporate foam).
- **`evidence`**: A resolvable pointer (`file:line`, commit SHA, prep-note ID, or proof JSON path)—**never a prose paragraph**.
- **`result`**: Outcome or tasting state (`VERIFIED`, `NOT_VERIFIED`, `INCONCLUSIVE`, `tests green`, `reverted`).

Use the bundled executable helper in `head-chef-mode`:
```bash
skills/head-chef-mode/scripts/log-decision.sh \
  decisions.tsv \
  "reduction-iter-1" \
  "Lowered primary burner breaker threshold to 2 failures" \
  "Prevent ticket-rail pileup under Kingman's formula" \
  "skills/pantry-backup-and-incident-card/SKILL.md:14" \
  "tests green"
```
The script strips stray tabs/newlines and prefixes any cell starting with `=`, `+`, `-`, or `@` with a single quote (`'`) to prevent spreadsheet formula injection.

## 2. Append-Only & Shift-Change Rules

1. **Append-Only**: Never edit or erase a historical row. If an earlier decision is superseded or a pan is dumped, append a new row starting with `SUPERSEDE:` or `REVERTED:`.
2. **Shift Change (`phase="start"`)**: When a new shift/run resumes an existing `decisions.tsv` written by a prior shift, its first row must use `phase="start"`, naming the timestamp range of preceding rows in `why` and this shift's run ID in `evidence`.

## 3. Cross-Vendor Blind Audit of the Prep Log

Before handing back a completed shift:
1. Verify every row's `evidence` pointer resolves on disk.
2. Flag any `INCONCLUSIVE` row (inconclusive is never counted as a pass).
3. Have a **cross-vendor taster model** (different vendor family than the cook) audit `decisions.tsv` against the shift transcript and end your reply with an `Attention` section starting with `reviewed by <model-slug>`.
