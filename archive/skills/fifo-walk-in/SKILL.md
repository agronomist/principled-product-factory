---
name: fifo-walk-in
description: Green painter's tape and FIFO (First-In, First-Out) Date-Dot hygiene for temporary feature flags, backwards-compatibility shims, Stage A pop-up experiments, and TODOs. Prevents mystery containers from rotting in the codebase walk-in cooler via structured FIFO-DATE-DOT expiration tags and automated spoilage scans. Use for /fifo-walk-in, "check date dots", or tech-debt walk-in purges.
---

# Green Painter's Tape & FIFO Date Dots (`/fifo-walk-in`)

> *"Open the walk-in cooler at any Michelin kitchen and every single cambro container has a strip of green painter's tape written in Sharpie: `Veal Stock — Prep: 11/24 — Use By: 11/27 — Sous Chef`. If the Sous Chef spots a container past its date dot—or an unlabeled mystery container—it goes straight into the trash."*

## 1. The Rule: No Unlabeled Mystery Containers in the Walk-In

AI agents love leaving behind `"temporary"` backwards-compatibility shims, feature flags, dual-write migration bridges, and vague `# TODO: clean up later` comments that sit in the codebase for 18 months until everyone is afraid to touch them.

In this kitchen:
1. **Prefer Immediate Migration Over Compatibility Shims**: Whenever possible, migrate all callers and delete the legacy path in the same ticket ([`/principle-one-course-at-a-time`](../principle-one-course-at-a-time/SKILL.md)).
2. **Every Temporary Container Gets a Green Tape Date Dot**: If a temporary shim, feature flag, fallback bridge, or `Stage A` pop-up experiment must stay in the repo across merges, you MUST label it with a machine-readable **`FIFO-DATE-DOT`** comment on the line above it:

```text
# FIFO-DATE-DOT: expires=2026-12-27 owner=line-cook ticket=TKT-104 action=86-shim-or-graduate
```

Required fields in a Date-Dot label:
- `expires=YYYY-MM-DD`: Hard expiration date (default maximum shelf life: **30 days** for Stage A pop-ups per [`/no-empty-calories`](../no-empty-calories/SKILL.md); **14 days** for migration shims).
- `ticket=<id>`: The originating ticket or issue slug.
- `action=<what-to-do>`: Exact instructions when the date arrives (e.g., `delete-legacy-v1-endpoint`, `86-dish-if-adoption-below-15pct`).

---

## 2. Running the Walk-In Spoilage Audit

Run the automated walk-in scanner anytime (or automatically via [`/pre-shift-lineup`](../pre-shift-lineup/SKILL.md) and `closing-duty.sh`):

```bash
bash skills/head-chef-mode/scripts/audit-date-dots.sh
```

What `audit-date-dots.sh` checks:
1. **Active Date-Dot Inventory**: Lists every `FIFO-DATE-DOT` container in the repository with its remaining shelf life.
2. **Spoiled Containers (`expires < today`)**: Fails with exit code `1` whenever any `FIFO-DATE-DOT` has passed its `expires=YYYY-MM-DD` date, naming the exact file, line number, ticket, and cleanup `action=`.
3. **Unlabeled Mystery Containers**: Counts bare `TODO` / `FIXME` / `HACK` comments that are missing a `FIFO-DATE-DOT` expiration label so the Sous Chef can either slap a date dot on them or dump them.
