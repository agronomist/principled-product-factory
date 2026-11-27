---
name: interrogate
description: Adversarial multi-model code and design review where adversaries try to break a change and only findings proven by a real failing execution run survive. Use for /interrogate, adversarial review, stress-testing a diff, or pre-merge red-teaming.
---

# Interrogate (`/interrogate`)

Adversaries try to break a change or design. **A finding survives only when a runnable command proves it.** Speculative prose opinions, style nitpicks, and unexecuted warnings are dropped.

## 1. Frame the Scope & Intent
Identify the target diff (`git diff main...HEAD`) or design artifact. Restate the intended behavior and invariants in plain words.

## 2. Fan Out Adversaries in Isolated Worktrees
Provision an isolated `git worktree` per adversarial reviewer (across diverse model vendors) and give each adversary this brief:

> `Read <path>/worker.md before anything else.`
> Break this change. Prove each finding with a run against the real code—a failing test, a repro script, or command output that demonstrates the wrong behavior or a breached Liskov/margin/security invariant. Keep repros inside your own worktree. Report each finding with: (1) Title, (2) Exact command run, (3) Actual output printed, and (4) Output the intent requires. Leave out anything you did not run (style, naming, theoretical future risks). "No findings" is a valid result.

## 3. Verify & Filter (Execution-Only Survival Rule)
For every finding reported by an adversary:
- Re-run its exact command against the target code.
- **Keep** the finding if and only if the command runs, fails as claimed, and breaks the stated intent.
- **Drop** any finding without a runnable command or whose command passes cleanly.
- Merge surviving findings that share the same root cause.
- For any surviving bug that escaped existing tests, compile a minimized regression fixture via [`../sre-fallback-and-postmortem/SKILL.md`](../sre-fallback-and-postmortem/SKILL.md).

## 4. Output Format
- **Intent**: One-line restatement of what the change promises.
- **Verified Findings**: Title, exact command, observed output, how it breaks intent, and which adversary models found it (or `"No verified findings"`).
- **Dropped**: Count of dropped findings per adversary model and why (unexecuted opinion vs. non-reproducing).
