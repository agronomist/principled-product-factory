---
name: show-me-your-work
description: Append-only TSV decision trail logger (decisions.tsv) and cross-vendor transcript auditor for long-running, multi-phase, or autonomous factory loops. Logs ts, phase, decision, why, evidence, and result with formula-injection sanitization. Use for /show-me-your-work.
---

# Show Me Your Work (`/show-me-your-work`)

Keep one canonical, human-scannable decision trail (`decisions.tsv`) during any multi-step or autonomous run so a reviewer can audit what happened, why, and what proved it in 30 seconds.

## 1. The Canonical TSV Format

Six tab-separated columns (`ts | phase | decision | why | evidence | result`), strictly single-line per row:
- **`ts`**: ISO-8601 UTC timestamp (`2026-11-27T07:15:00Z`).
- **`phase`**: Workflow phase, station name, or loop iteration (`frame`, `classifier`, `loop-iter-1`, `attack-premise`, `canary-10pct`).
- **`decision`**: One-line plain-English description of what was chosen or done.
- **`why`**: Plain-English reason (no bloated AI jargon).
- **`evidence`**: A resolvable pointer (`file:line`, commit SHA, artifact ID, or proof JSON path)—**never a prose paragraph**.
- **`result`**: Outcome or predicate state (`VERIFIED`, `NOT_VERIFIED`, `INCONCLUSIVE`, `tests green`, `reverted`).

Use the bundled executable helper in `factory-mode`:
```bash
skills/factory-mode/scripts/log-decision.sh \
  decisions.tsv \
  "loop-iter-1" \
  "Switched primary fallback threshold to 2 failures" \
  "Prevent tail-latency pileup under Kingman's formula" \
  "skills/sre-fallback-and-postmortem/SKILL.md:14" \
  "tests green"
```
The script strips stray tabs/newlines and prefixes any cell starting with `=`, `+`, `-`, or `@` with a single quote (`'`) to prevent spreadsheet formula injection.

## 2. Append-Only & Multi-Run Rules

1. **Append-Only**: Never edit or delete a historical row. If an earlier decision is superseded or reverted, append a new row starting with `SUPERSEDE:` or `REVERTED:`.
2. **Multi-Run Continuation (`phase="start"`)**: When a new agent run resumes an existing `decisions.tsv` written by a prior run, its first row must use `phase="start"`, naming the timestamp range of preceding rows in `why` and this run's ID in `evidence`.

## 3. Cross-Vendor Audit of the Trail

Before handing back a completed run:
1. Verify every row's `evidence` pointer resolves on disk.
2. Flag any `INCONCLUSIVE` row (inconclusive is never counted as a pass).
3. Have a **cross-vendor reviewer model** (different vendor family than the worker) audit `decisions.tsv` against the run transcript and end your reply with an `Attention` section starting with `reviewed by <model-slug>`.
