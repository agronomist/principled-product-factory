---
name: pre-shift-lineup
description: The 4:30 PM pre-shift kitchen lineup and walk-in cooler inventory check before dinner service opens. Inspects whether the base stockpot (main branch) is clean, audits active factory/* cutting boards against Little's Law WIP limits, checks for spoiled FIFO date-dot containers, and lists Draft PRs waiting under the heat lamp. Use for /pre-shift-lineup, "check the walk-in", or starting a new Claude Code session.
---

# Pre-Shift Lineup & Walk-In Check (`/pre-shift-lineup`)

> *"In a serious kitchen, nobody opens the doors at 5:30 PM and just starts firing tickets. At 4:30 PM, the brigade gathers for Lineup, checks the walk-in cooler, tastes the base stock, and calls out what is 86'd before the first guest sits down."*

## When to Run

Run `/pre-shift-lineup` at the start of a new Claude Code shift, before dispatching [`/kitchen-brigade`](../kitchen-brigade/SKILL.md) on a batch of tickets, or whenever you return to a repository after stepping away.

---

## Step 1: Run the Walk-In Inventory Script

Execute the one-command pre-shift inspection script from the repository root:

```bash
bash skills/head-chef-mode/scripts/pre-shift-check.sh
```

This script inspects four stations in under 2 seconds:
1. **Base Stockpot Health (`git status` & current branch)**: Checks if the working tree has uncommitted leftovers from a previous shift before you slice new ingredients on top of dirty boards.
2. **Active Cutting Boards (`git worktree list`)**: Counts active `factory/*` worktrees against Little's Law (`WIP_LIMIT = 5`, [`/principle-clean-cutting-boards`](../principle-clean-cutting-boards/SKILL.md)) and flags any abandoned cutting boards.
3. **Walk-In Spoilage (`audit-date-dots.sh`)**: Checks for expired `FIFO-DATE-DOT` feature flags, shims, or Stage A experiments via [`/fifo-walk-in`](../fifo-walk-in/SKILL.md).
4. **Heat-Lamp Pass Check (`gh pr list` / `decisions.tsv`)**: Summarizes recent [`/prep-log`](../prep-log/SKILL.md) decisions and any open `factory/*` branches or Draft PRs waiting for the Head Chef's signature.

---

## Step 2: Taste the Base Stock Before Firing New Orders

If `pre-shift-check.sh` or the project's live tasting harness ([`/taste-the-dish`](../taste-the-dish/SKILL.md) / [`/verify-kitchen-cookbook`](../verify-kitchen-cookbook/SKILL.md)) shows that `main` is **already failing before your shift starts**:
- **STOP THE LINE**: Never let a Line Cook start cooking a new feature on top of sour stock. Otherwise the cook will spend 40 minutes trying to debug a failure they didn't cause (George parallel-parking into a space that already has a abandoned car in it).
- Either fix the broken baseline on `main` first, or explicitly document the pre-existing failure in the ticket brief so [`pass-inspector`](../../agents/pass-inspector.md) knows the exact baseline delta.

---

## Step 3: Call the Lineup Brief (Max 8 Lines)

Deliver a tight 4:30 PM Lineup Brief to the Head Chef (human operator):
1. **Stockpot Status**: `CLEAN` or `SPOILED` (with exact failing check if spoiled).
2. **Active Cutting Boards**: `$WIP / 5` (`factory/*` worktrees currently open).
3. **Walk-In Spoilage**: Count of expired `FIFO-DATE-DOT` tags or unlabeled mystery containers.
4. **Tonight's Fire Order**: Recommend the highest-leverage first ticket to fire based on open Draft PRs or queue priority.
