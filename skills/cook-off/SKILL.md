---
name: cook-off
description: Spawn N parallel line cooks at the same recipe brief on isolated git worktree cutting boards, score with a cross-vendor blind taster against a hidden rubric, pick the cleanest base dish, and plate the strongest elements of the runners-up into it. Use for /cook-off or one-way door architecture choices.
---

# Cook-Off (`/cook-off`)

Open a todo list with one entry per phase (`Frame`, `Fire stations`, `Blind taste`, `Pick base`, `Plate & graft`, `Final taste`) before lighting any burners.

## Phase A: Frame the Recipe Contract
Every contender gets the exact same order brief, so the brief is the contract.
1. State the dish artifact each contender is producing.
2. Derive the **tasting rubric** (3–6 concrete gradeable criteria including correctness, Liskov/Parnas container hygiene, and food-cost margin impact). Contenders only see the task brief; the rubric stays hidden with the taster.
3. Give each contender its own isolated cutting board (`git worktree` on `factory/cookoff-<slug>-cand-<n>` or `/tmp/cookoff-<slug>/candidate-<n>/`), per [`../principle-clean-cutting-boards/SKILL.md`](../principle-clean-cutting-boards/SKILL.md).

## Phase B: Fire All Stations in Parallel
Spawn all $N$ line cooks concurrently (`run_in_background: true`), starting each kickoff with `Read <path>/station-brief.md before anything else.` and passing the task, shared grounding paths, its isolated cutting-board path, and instructions to produce the dish plus a short note naming approaches considered and rejected.

## Phase C: Cross-Vendor Blind Tasting
After all contenders finish plating, spawn one readonly taster on a **different model vendor** than the parent (`principle-blind-taste-test`). The taster scores each dish by cutting-board label on every rubric criterion and recommends a base plate.

## Phase D: Pick the Base Plate
Taste every contender end-to-end and score criterion-by-criterion against the rubric. Pick the base a future line cook can extend most easily without breaking invariants. When two contenders tie on rubric score, **prefer the simpler recipe with fewer ingredients / smaller API surface** (Laziness Protocol).

## Phase E: Plate & Graft the Best Garnishes
Walk each runner-up dish once more for the 1–2 unique strengths worth folding into the winning base (e.g., a sharper edge-case guard or cleaner error signature). Fold each graft in by hand from first principles so the final dish tastes coherent under one culinary concept.

## Phase F: Final Taste
Run the live tasting harness ([`../taste-the-dish/SKILL.md`](../taste-the-dish/SKILL.md)) and tests on the synthesized dish (`principle-taste-before-serving`). Return the final dish, winning base rationale, blind taster verdict, grafted elements, and verification output.
