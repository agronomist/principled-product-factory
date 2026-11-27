---
name: arena
description: Spawn N parallel candidates at the same task in isolated git worktrees, score with a cross-vendor judge against a hidden rubric, pick the cleanest base, and graft the strongest parts of the losers into it. Use for /arena, one-way door architecture choices, or contested designs.
---

# Arena (`/arena`)

Open a todo list with one entry per phase (`Frame`, `Fan out`, `Cross-judge`, `Pick base`, `Graft`, `Verify`) before launching anything.

## Phase A: Frame
Every candidate gets the exact same prompt, so the prompt is the contract.
1. State the artifact each candidate is producing.
2. Derive the **rubric** (3–6 concrete gradeable criteria including correctness, Liskov/Parnas boundary hygiene, and unit margin impact). Candidates only see the task brief; the rubric is for the judge and picker.
3. Give each candidate its own isolated output location (`git worktree` on `factory/arena-<slug>-cand-<n>` or `/tmp/arena-<slug>/candidate-<n>/`), per [`../principle-separate-before-serializing-shared-state/SKILL.md`](../principle-separate-before-serializing-shared-state/SKILL.md).

## Phase B: Fan out
Spawn all $N$ subagents in parallel (`run_in_background: true`), starting each kickoff with `Read <path>/worker.md before anything else.` and passing the task, shared grounding paths, its isolated output path, and instructions to produce the artifact plus a short rationale naming alternatives considered and rejected.

## Phase C: Cross-judge
After all candidates complete, spawn one readonly judge on a **different model vendor** than the parent (`principle-cross-vendor-blind-review`). The judge scores each candidate by path label on every rubric criterion and recommends a base.

## Phase D: Pick a base
Read every candidate end-to-end and score criterion-by-criterion against the rubric. Pick the base a future maintainer can extend most easily without breaking invariants. When two candidates tie on rubric score, **prefer the smaller API surface / fewer lines of code** (Laziness Protocol).

## Phase E: Graft
Walk each losing candidate for the 1–2 unique strengths worth porting into the winning base (e.g., an edge-case guard or cleaner error signature). Fold each graft in by hand from first principles so the synthesized artifact stays coherent under one mental model.

## Phase F: Verify
Run the live verification harness (`verify-*`) and tests on the synthesized artifact (`principle-prove-it-works`). Return the synthesized artifact, winning base rationale, cross-judge verdict, grafted items, and verification output.
