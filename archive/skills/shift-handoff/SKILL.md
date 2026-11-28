---
name: shift-handoff
description: Catch the Head Chef up on what happened in the kitchen during an overnight or background shift, or reconstruct recent working context across branches, commits, and prep logs (decisions.tsv). Lists every plated Draft PR waiting at the pass with everything needed to decide from the reply alone. Use for /shift-handoff, 'catch me up', or 'where did I leave off'.
---

# Shift Handoff — Morning Catch-Up & Context Recall (`/shift-handoff`)

When the kitchen runs unattended overnight or across multiple shifts, the incoming Head Chef needs a crisp, zero-fluff briefing at the pass.

## 1. Reconstruct the Kitchen State
Before speaking, inspect:
- Active git branches (`factory/*`), recent commits, and working tree status.
- The tail of `decisions.tsv` ([`../prep-log/SKILL.md`](../prep-log/SKILL.md)) since the last `start` row or user message.
- Any open Draft Pull Requests or halted tickets (`needs_clarification`, `HALTED_BUILD_TRAP_NO_CUSTOMER_VALUE`, or `MAX_REVISION_ROUNDS` exceeded).

## 2. Structure the Shift Handoff Brief
Deliver the catch-up in three tight sections written through [`../plain-english-menu/SKILL.md`](../plain-english-menu/SKILL.md):

1. **What Left the Kitchen / What Changed**:
   - Plain-English summary of completed courses, verified tasting metrics (old value vs. new value), and any pans that were dumped (reverted) with the reason why.
   - Include a small Mermaid diagram or compact table when state moved across multiple stations.
2. **Waiting at the Pass (Actionable Decisions Required from You)**:
   - List every item currently blocked on human judgment (e.g., Draft PRs ready to mark ready/merge, 6-month menu re-pricing triggers, or clarifying questions from `host_triage`).
   - **Self-Contained Decision Rule**: For each waiting item, provide the exact context, diff summary, food-cost impact, and recommendation so the Head Chef can decide *from your reply alone* without opening five other files.
3. **Next Prep on the Rail**:
   - The single highest-leverage next step queued up once the pass is cleared.
