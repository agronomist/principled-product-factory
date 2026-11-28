---
name: kitchen-help
description: Guides users through Kitchen Brigade setup (/setup-kitchen), /head-chef-mode, picking the right skill or playbook for a situation, copy-paste recipe prompts, and troubleshooting a shift that went wrong. Use for /kitchen-help or 'how do I use this kitchen?'.
file_names:
  - references/recipe-prompts.md
---

# Kitchen Help (`/kitchen-help`)

Answer the user's question about the Kitchen Brigade skill stack, hand them a copy-pasteable prompt from [`references/recipe-prompts.md`](references/recipe-prompts.md), and link the exact skill file that owns the answer.

- **For a help question**: Don't start cooking the work yourself—a full Brigade shift spends real tokens, so hand them the prompt to send.
- **For a real work request** (e.g., *"use the kitchen brigade to fix this bug"*): That is not a help question! Load [`../head-chef-mode/SKILL.md`](../head-chef-mode/SKILL.md) and execute the work immediately.

---

## 1. Quick Routing Table: "Which Skill Do I Need?"

| You Want To... | Invoke This Skill |
| :--- | :--- |
| Run any non-trivial task with full Brigade rigor | [`/head-chef-mode`](../head-chef-mode/SKILL.md) |
| Configure station models and token budget | [`/setup-kitchen`](../setup-kitchen/SKILL.md) |
| Test if a feature idea is real guest value or the Build Trap | [`/no-empty-calories`](../no-empty-calories/SKILL.md) |
| Check unit economics, AI token/HITL costs, or 6-month re-pricing | [`/food-cost-guard`](../food-cost-guard/SKILL.md) |
| Turn an issue/ticket into a blind-inspected Draft PR via 4 stations | [`/kitchen-brigade`](../kitchen-brigade/SKILL.md) |
| Build a Challenger B2B sales pitch, push back on a discount, or cure buyer FOMU | [`/sommelier-table-pitch`](../sommelier-table-pitch/SKILL.md) |
| Define 5-step menu positioning and 7 Structural Moats moat | [`/signature-dish-moat`](../signature-dish-moat/SKILL.md) |
| Sketch types, function signatures, and contract pre/postconditions before coding | [`/mise-en-place`](../mise-en-place/SKILL.md) |
| Run $N$ parallel line cooks on isolated worktrees and graft the best dish | [`/cook-off`](../cook-off/SKILL.md) |
| Have adversarial inspectors try to break a diff with real repro commands | [`/health-inspector`](../health-inspector/SKILL.md) |
| Prove a change doesn't spoil downstream callers outside the diff | [`/cross-contamination`](../cross-contamination/SKILL.md) |
| Generate a live app tasting harness (`Fire Up -> Station Check -> Plate -> Proof -> Dishpit`) | [`/taste-the-dish`](../taste-the-dish/SKILL.md) |
| Vet a benchmark speedup or eval lift across 7 physical/statistical checks | [`/thermometer-check`](../thermometer-check/SKILL.md) |
| Formally verify concurrency (`WIP_LIMIT=5`) or circuit breakers with a Mermaid statechart | [`/haccp-statechart`](../haccp-statechart/SKILL.md) |
| Keep an append-only `decisions.tsv` prep log during a multi-step shift | [`/prep-log`](../prep-log/SKILL.md) |
| Stop cooks from repeating a mistake (Architecture $\to$ Types $\to$ Fix-Naming Alarm) | [`/sharpen-the-knives`](../sharpen-the-knives/SKILL.md) |
| Mine guest edits (`user_correction_diff`) and $N=1 \to 3 \to 10$ table requests | [`/dining-room-feedback`](../dining-room-feedback/SKILL.md) |
| Stamp out a new product line, harvest Rule-of-Two code, or run a `1%->100%` canary | [`/central-commissary`](../central-commissary/SKILL.md) |
| Set up 3-tier pantry fallbacks or turn an incident into a regression card | [`/pantry-backup-and-incident-card`](../pantry-backup-and-incident-card/SKILL.md) |
| Catch up after an overnight shift and see every Draft PR waiting at the pass | [`/shift-handoff`](../shift-handoff/SKILL.md) |
| Mine the transcript to upgrade `skills/*/SKILL.md` with durable lessons | [`/update-the-cookbook`](../update-the-cookbook/SKILL.md) |
| Strip AI slop out of prose and apply Pitch / Kitchen metaphors | [`/plain-english-menu`](../plain-english-menu/SKILL.md) |

---

## 2. Troubleshooting a Shift That Went Wrong

| Symptom | Cause & Fix |
| :--- | :--- |
| **A feature request was blocked before any code was written** | `/no-empty-calories` or `/food-cost-guard` caught a speculative Build-Trap idea (Opportunity score $< 10.0$ or negative unit margin). Supply real customer commitment evidence or distill model costs. |
| **The Brigade stopped after 2 refires (`MAX_REVISION_ROUNDS = 2`)** | The Pass Inspector requested changes twice and the Line Cook still missed a verbatim plating criterion. Inspect the unresolved findings or run `/principle-check-the-oven` to test the underlying premise. |
| **A station retry halted immediately on attempt 2** | Duplicate SHA-256 burn signature detected (*George parallel parking the same bad angle twice*). The burner turned off automatically to save tokens. |
| **A `git push` to `main` was blocked by a hook** | `hooks/pre-tool-guard.sh` and `principle-plate-at-the-pass` forbid direct pushes to `main`/`master`. Push to `factory/<ticket-slug>` and open a Draft PR. |
| **An overnight loop moved but finished nothing** | Give `/head-chef-mode` a falsifiable tasting check that can pass or fail (`principle-taste-before-serving`), not a vague duration. |
