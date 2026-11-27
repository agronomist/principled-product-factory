---
name: amuse-bouche
description: The One-Bite Proof of Flavor — before spending 20,000 tokens building full database migrations, backend plumbing, and retry queues for a new Stage A feature, serve a working 5-minute interactive/CLI single-bite slice with fixture data so the diner can taste the workflow and say "Yes, cook the full course" or "Change the seasoning." Use for /amuse-bouche, "serve a one-bite prototype", or Stage A 0-to-1 features.
---

# The Amuse-Bouche (`/amuse-bouche`)

> *"Before a guest commits to a 3-hour, 9-course tasting menu, the chef sends out a single bite on a porcelain spoon—an Amuse-Bouche—that proves the flavor thesis in 10 seconds flat."*

## Why Chefs Serve an Amuse-Bouche Before the Banquet

Even when a new feature idea passes [`/no-empty-calories`](../no-empty-calories/SKILL.md) (Ulwick Opportunity Score $\ge 10.0$) and [`/food-cost-guard`](../food-cost-guard/SKILL.md), the #1 waste of tokens in AI software factories is **cooking the entire banquet in the dark**: the agent disappears for 40 minutes, writes 1,400 lines of schema migrations, repository layers, and mocks—and the first time you actually run it, you realize the interaction feels clunky.

`/amuse-bouche` enforces a strict rule for **`Stage A: Test Kitchen 0-to-1`** user-facing features: **Serve the spoon before you boil the 40-gallon stockpot.**

---

## The 4 Rules of a Proper Amuse-Bouche

1. **One Bite, Real Utensils (Under 5 Minutes / 1 File)**:
   - Build the exact surface the diner touches—the CLI command, the single self-contained HTML/UI page, or the exact API request/response payload—wired to an **in-memory or JSON fixture** instead of a database migration.
2. **Real Flavor, Zero Plumbing**:
   - Do **not** build auth middleware, pagination, retry queues, or multi-table SQL joins in the Amuse-Bouche. Put the entire effort into the **core domain transformation or user moment of delight** (e.g., if the feature is a blind-tasting diff packet generator, generate one real packet on a real commit right now so the user can read it).
3. **Label the Spoon with a `FIFO-DATE-DOT`**:
   - Stamp the prototype file or route with a 7-day [`/fifo-walk-in`](../fifo-walk-in/SKILL.md) tag (`FIFO-DATE-DOT: expires=<+7d> ticket=<id> action=graduate-to-full-course-or-86`) so an unapproved amuse-bouche never accidentally ships as permanent infrastructure.
4. **The Tasting Call at the Pass**:
   - Present the runnable 1-command Amuse-Bouche to the Head Chef with three choices:
     1. **"Compliments to the Chef — Fire the Full Course"**: Hand off to [`sous-chef-planner`](../../agents/sous-chef-planner.md) and [`/mise-en-place`](../mise-en-place/SKILL.md) to replace the fixture with production storage and contracts.
     2. **"Needs More Acid — Re-season the Bite"**: Adjust the UX, CLI flags, or output shape while it's still a 100-line file (10x cheaper than refactoring 12 files later).
     3. **"86 It"**: Dump the spoon at almost zero food cost.
