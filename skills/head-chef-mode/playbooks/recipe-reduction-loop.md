# Playbook: Scientific Recipe Reduction Loop (`recipe-reduction-loop.md`)

Use this playbook when reducing a sauce—optimizing a measurable target (accuracy, latency, token cost, conversion, or food-cost margin) over iterative tasting brackets.

## Todo List Steps (Copy into Todo Tool First)

1. **Frame the Tasting Predicate & Calibrate the Thermometer First**:
   - State the exact numerical metric, its current baseline reading on the real dish, and the target threshold (`principle-taste-before-serving`).
   - Run [`../../thermometer-check/SKILL.md`](../../thermometer-check/SKILL.md) and the project's tasting harness ([`../../taste-the-dish/SKILL.md`](../../taste-the-dish/SKILL.md)) to capture the pre-change baseline before touching the stove.
   - Initialize `decisions.tsv` via [`../../prep-log/SKILL.md`](../../prep-log/SKILL.md) (`scripts/log-decision.sh`) and log the `frame` row.
2. **Run Bracketed Single-Ingredient Reductions (`principle-one-course-at-a-time`)**:
   - For each tasting bracket:
     1. **State 1 Hypothesis**: Name the single ingredient or step you are adjusting and why it moves the limiter.
     2. **Apply Smallest Diff**: Make one atomic change on an isolated git worktree cutting board.
     3. **Taste on the Real Dish**: Re-run the live tasting harness, [`../../thermometer-check/SKILL.md`](../../thermometer-check/SKILL.md), and [`../../food-cost-guard/SKILL.md`](../../food-cost-guard/SKILL.md).
     4. **Keep or Dump the Pan**:
        - If the verdict is `VERIFIED` and the reading improved without breaking postconditions or food-cost margin: **commit the bracket** and append a `tests green` row to `decisions.tsv`.
        - If the reading regressed, failed a gate, or returned `INCONCLUSIVE`: **dump the pan (`git checkout` / `git reset`) back to the bracket start immediately** and append a `reverted` row to `decisions.tsv`. Never add more ingredients to a burned pan.
3. **Check the Oven After Two Failed Tweaks (`principle-check-the-oven`)**:
   - Track consecutive failed tweaks per gate.
   - The moment **2 distinct tweaks fail the same tasting gate**, STOP proposing tweak #3.
   - Write down the single shared premise both failed tweaks assumed (e.g., *"is the oven pilot light even lit?"*), design a read-only observation probe to test that premise directly, run it, and log an `attack-premise` row to `decisions.tsv`.
4. **Health Inspection & Prep-Log Audit (`health-inspector` + `prep-log`)**:
   - Once the target reading is reached, run [`../../health-inspector/SKILL.md`](../../health-inspector/SKILL.md) to verify the optimization didn't game Goodhart's Law (*Kramer & Newman's Michigan bottle-deposit run*).
   - Audit `decisions.tsv` against the transcript using a cross-vendor taster model and present the final `Attention` block.
