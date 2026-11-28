---
name: ship
description: Take a ticket or well-defined task to a verified draft pull request. Use for "ship this", "fix issue N", implementing a feature or refactor, overnight runs, and catching up on a previous run.
---

# Ship

Stop at a draft PR. A person marks it ready and merges.

1. **Frame.** Restate the task. If it is ambiguous, ask (or, unattended, write the
   questions and stop). If it is an unproven feature idea, use `shape` first.
2. **Plan.** Read the real code. Write 3 to 6 acceptance criteria that a command can
   prove true or false. Cross-module changes: settle types and signatures first.
   Sensitive areas (see `review`): add at least two negative tests.
3. **Isolate.** Work on a `factory/<ticket>` branch, ideally in its own worktree:
   `git worktree add ../<ticket> -b factory/<ticket>`
4. **Build.** Hand the task and criteria to the `implementer` agent. Riskiest step
   first. One change at a time; keep it if the check passes, revert it if not.
   The same error twice means stop. Two different fixes failing the same check means
   test the assumption they share.
5. **Verify.** Use `verify` on the running software.
6. **Review.** Give the `reviewer` agent only the task, the criteria, the branch and
   the test output, never the implementer's reasoning. At most two rounds of fixes,
   then stop and report what still fails. No PR on a failing review.
7. **Hand off.** Open a draft PR: what changed, proof for each criterion, risks, and
   the decisions the person must make.

## Long runs
Append one line per decision to `decisions.tsv`: time, decision, why, evidence
(commit, file:line or command), result. Never edit old lines.

## Catching up
Read `decisions.tsv`, `factory/*` branches, recent commits and open draft PRs. Report
what changed, what was reverted, what waits on the person, and the next step.
