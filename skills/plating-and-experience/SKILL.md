---
name: plating-and-experience
description: The Product Trio's Design & Dining-Experience Seat — eliminates Usability Risk and enforces "Plated != Eaten" outcome telemetry. Audits every user-facing feature, CLI, API, or UI on Time-to-First-Bite (<= 3 steps), Empty-Plate & Burned-Plate states (fix-naming errors), zero exposed kitchen plumbing, and mandatory outcome telemetry hooks. Use for /plating-and-experience, UX/DX review, or usability checks.
---

# Plating, Dining Experience & Outcome Telemetry (`/plating-and-experience`)

> *"You can source the finest Dover sole in Paris, nail the food-cost math, and cook it to the exact degree—and still ruin dinner if you serve it on a cold hubcap without a fork, or never bother to look out into the dining room to see if the guest actually ate it."*

## Why This Skill Exists (Giving Design a Seat in the Product Trio)

In the Empowered Product Trio Operating Model, **Product Design / User Experience** is an equal partner alongside Product Management and the Tech Lead Engineer. Whether your dish is a web UI, a CLI tool, an API endpoint, or a Claude Code skill, **Usability Risk** (*"Can the diner figure out how to eat it without frustration?"*) and **Outcome Verification** (*"Did anyone actually eat it after we plated it?"*) must be checked on every user-facing ticket.

---

## The 4 Plating & Experience Laws

Every user-facing change planned by [`sous-chef-planner`](../../agents/sous-chef-planner.md) and graded by [`pass-inspector`](../../agents/pass-inspector.md) must pass these four checks:

### 1. Time-to-First-Bite ($\le 3$ Steps, Zero Uncracked Lobsters)
- Count the exact number of clicks, commands, or required parameters between a cold start and the user's first moment of value.
- **Rule**: A diner should get their first bite in **$\le 3$ steps** with sensible defaults. If a CLI command requires 7 mandatory flags before it does anything useful, add smart defaults so the 1-argument invocation works out of the box.

### 2. The Empty Plate & The Burned Plate (First-Run & Error States)
- **The Empty Plate (Zero-Data / First-Run State)**: What does the user see the very first time they open the page or run the command when no data exists yet? It must never be a blank screen, a `KeyError`, or an empty `{}`—it must show a warm, 1-line next action (*"No cutting boards active yet. Run `spawn-worktree.sh <ticket>` to start one."*).
- **The Burned Plate (Error State)**: When something fails, the error message must follow [`/sharpen-the-knives`](../sharpen-the-knives/SKILL.md) Level 3: **state what went wrong AND name the exact command or fix to recover** (`ERROR: <what failed>. FIX: <exact action>`).

### 3. Keep the Kitchen Plumbing Off the Dining Room Table
- Never leak internal kitchen machinery (raw stack traces, internal database foreign keys, unformatted JSON blobs, or 14 internal tuning flags) onto the guest's tablecloth when a clean domain summary is what they asked for.

### 4. `Plated != Eaten` (Mandatory Outcome Telemetry Hook)
- In an Empowered Kitchen, merging a PR is **output**, not **outcome**.
- Every `work_type == "feature"` ticket MUST wire a concrete **Outcome Telemetry Hook** into the diff itself (an event counter, structured audit/usage log row, or CLI proof entry in `.audit/evidence/` or `decisions.tsv`) that records:
  1. When a diner invokes the feature, and
  2. Whether the diner reached the target outcome or sent the plate back (`user_correction_diff`).
- Without this telemetry hook, [`/dining-room-feedback`](../dining-room-feedback/SKILL.md) and the 30-day [`/fifo-walk-in`](../fifo-walk-in/SKILL.md) sunset gate are flying blind—so [`pass-inspector`](../../agents/pass-inspector.md) will return `request_changes` on any feature diff that lacks an outcome measurement hook.

### 5. "The Schmeer" (Anticipate the Next 30 Seconds)
- Don't stop at the literal acceptance criterion if the user is left holding an awkward manual chore 10 seconds later.
- Ask: *"Once the user sees this output, what is their immediate next click, copy-paste, or question?"*
- Add the **Petit-Four Schmeer** ($\le 15\%$ extra code, zero new dependencies)—such as a ready-to-copy recovery command, a pre-computed delta summary, or a sensible default that saves them a round-trip.
