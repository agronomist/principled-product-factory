---
name: health-inspector
description: Adversarial multi-model kitchen health inspection where inspectors try to break a change or recipe and only violations proven by a real failing execution run survive. Use for /health-inspector, adversarial review, stress-testing a diff, or pre-service red-teaming.
---

# Health Inspector (`/health-inspector`)

Adversarial inspectors try to break a dish or kitchen change. **A violation survives only when a runnable command proves it.** Speculative opinions, plating aesthetics, and unexecuted warnings are thrown out.

## 1. Frame the Scope & Health Code Intent
Identify the target diff (`git diff main...HEAD`) or recipe design. Restate the intended behavior and invariants in plain words.

## 2. Send In the Inspectors on Isolated Cutting Boards
Provision an isolated `git worktree` per adversarial inspector (across diverse model vendors) and hand each inspector this brief:

> `Read <path>/station-brief.md before anything else.`
> Try to break this change. Prove each health-code violation with a real run against the code—a failing test, a repro script, or command output showing spoiled output or a breached Liskov/food-cost/security invariant. Keep repros inside your own worktree. Report each violation with: (1) Title, (2) Exact command run, (3) Actual output printed, and (4) Output the recipe requires. Leave out anything you did not run (style, naming, theoretical future risks). "Zero violations" is a valid result.

## 3. Re-Test & Filter (Execution-Only Survival Rule)
For every violation reported by an inspector:
- Re-run its exact command against the target code.
- **Keep** the violation if and only if the command runs, fails as claimed, and breaks the stated intent.
- **Drop** any finding without a runnable command or whose command passes cleanly.
- Merge surviving violations that share the same root cause.
- For any surviving violation that escaped existing checks, laminate a permanent JSON regression fixture via [`../pantry-backup-and-incident-card/SKILL.md`](../pantry-backup-and-incident-card/SKILL.md).

## 4. Inspection Report Format
- **Intent**: One-line restatement of what the change promises.
- **Verified Violations**: Title, exact command, observed output, how it breaks intent, and which inspector models caught it (or `"Zero verified violations — Grade A"`).
- **Dropped**: Count of dropped complaints per inspector model and why (unexecuted opinion vs. non-reproducing).
