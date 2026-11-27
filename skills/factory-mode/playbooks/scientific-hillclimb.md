# Playbook: Scientific Hillclimb Loop (`scientific-hillclimb.md`)

Use this playbook when optimizing a measurable target (accuracy, latency, token cost, conversion, or unit contribution margin) over iterative experiments.

## Todo List Steps (Copy into Todo Tool First)

1. **Frame the Falsifiable Predicate & Build/Doctor the Harness First**:
   - State the exact numerical metric, its current baseline value on the real artifact, and the target threshold (`principle-prove-it-works`).
   - Run `Doctor` on the project's `verify-*` harness ([`../../create-verification-skill/SKILL.md`](../../create-verification-skill/SKILL.md)) and capture the pre-change baseline before touching code.
   - Initialize `decisions.tsv` via [`../../show-me-your-work/SKILL.md`](../../show-me-your-work/SKILL.md) (`scripts/log-decision.sh`) and log the `frame` row.
2. **Run Bracketed Atomic Experiments (`principle-sequence-verifiable-units`)**:
   - For each iteration:
     1. **State 1 Hypothesis**: Name what you are changing and why it should move the limiter.
     2. **Apply Smallest Diff**: Make one atomic change inside an isolated git branch/worktree.
     3. **Measure on Real Artifact**: Re-run the live `verify-*` harness and [`../../margin-guard/SKILL.md`](../../margin-guard/SKILL.md).
     4. **Keep or Hard-Revert**:
        - If the verdict is `VERIFIED` and the metric improved without breaking Liskov postconditions or unit margin: **commit the bracket** and append a `tests green` row to `decisions.tsv`.
        - If the metric regressed, failed a gate, or returned `INCONCLUSIVE`: **hard-revert (`git checkout` / `git reset`) to the bracket start immediately** and append a `reverted` row to `decisions.tsv`. Never stack a new experiment on top of a regressed or inconclusive change.
3. **Enforce Premise-Attacking Circuit Breaker (`principle-attack-the-premise`)**:
   - Track consecutive failed fixes per gate.
   - The moment **2 distinct fixes fail the same gate**, STOP proposing fix #3.
   - Write down the single shared premise both failed fixes assumed, design a read-only observation probe that directly tests whether that premise is true, run the probe, and log an `attack-premise` row to `decisions.tsv`.
4. **Adversarial Verification & Cross-Vendor Trail Audit (`interrogate` + `show-me-your-work`)**:
   - Once the target metric is reached, run [`../../interrogate/SKILL.md`](../../interrogate/SKILL.md) to ensure the optimization didn't game Goodhart's Law (*Kramer & Newman's Michigan bottle-deposit run*).
   - Audit `decisions.tsv` against the run transcript using a cross-vendor reviewer model and present the final `Attention` block.
