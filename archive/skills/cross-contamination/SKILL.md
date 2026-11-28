---
name: cross-contamination
description: Find what a recipe change could spoil somewhere else in the kitchen before it ships, beyond the diff, and prove the one safety fact it depends on by running real code instead of writing an essay. Use for /cross-contamination, 'blast radius of X', or reviewing a shared commissary diff.
---

# Cross-Contamination Check (`/cross-contamination`)

Listing callers with `grep` takes one second and proves nothing. The job of `/cross-contamination` is to find **what a change spoils three stations downstream** (shared central-commissary types, JSON wire formats, SQLite columns, or sibling kitchen lines)—and **prove the one fact that makes the change safe by running real code**.

## 1. Never Trust Your Own Writeup
A blast-radius writeup that *sounds* reassuring is worthless. Push every safety claim as far down this 5-level ladder as possible, and state which rung you reached:
1. *You said so* (worthless).
2. *You pointed at `file:line`* (real source citation).
3. *You traced the step-by-step path showing the allergen cannot reach the plate*.
4. **You ran a script or test calling the real code that would fail loud if you were wrong.**
5. **You reproduced it in the live running application.**

Always aim for Rung 4 or 5.

## 2. Steps
1. **Read the Change**: Inspect the diff, the symbols added/modified/deleted, and what now behaves differently (including implicit ordering or timeout changes).
2. **Find the One Safety Fact**: Most changes that look risky are safe because of a single invariant (e.g., *"this cleanup only deletes `.scratch` folders after `capture_evidence()` flushes to `evidence_root`"*). Spend your effort proving that single fact.
3. **Look Where `grep` Stops**: Follow serialized JSON payloads, SQLite WAL table schemas, environment variables, and shared `platform/` contracts consumed by other products.
4. **Prove the Fact by Running Code**: Write and execute a small verification script or test that imports the real module and proves the invariant holds.

## 3. Output Format
- **What Changed**: Plain-English summary including non-obvious side effects.
- **The One Fact It's Safe Because Of**: State the fact, the ladder rung reached (1–5), and paste the exact command + output that proved it (or mark `UNPROVEN`).
- **Confirmed Cross-Contamination Risks**: `file:line`, likelihood, blast cost, and repro proof.
- **Cleared Stations**: What you checked and cleared, with `file:line` citations.
