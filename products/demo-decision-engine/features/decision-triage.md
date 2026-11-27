# Feature: Decision Triage & Bayesian Kill-Switch

Evaluates product and AI workflow proposals through Step 0 Lifecycle Stage routing (`Stage_A`, `Stage_B`, `Stage_C`), Bayesian posterior odds updating, and the 4-Axis AI-Native Prioritization Filter.

## Sub-features

- Step 0 Lifecycle Stage classification (`Stage_A` fast-track experiment vs. `Stage_B`/`Stage_C` scale with guardrails).
- Bayesian prior-to-posterior odds update (`sunset_kill_switch` when posterior $< P_{\text{kill}}$).
- 4-Axis AI-Native Prioritization Filter blocking AI bolt-on theater (`evoi_usd <= 0` or `deterministic_rule_suffices == True`).
- Passive zero-friction `(input_state, system_output, user_correction_diff, verified_outcome)` telemetry tuple emission.

## How to get to it (user POV)

Invoke the CLI driver `products/demo-decision-engine/harness/drive_cli.py --case-id <case_id>` or call `DecisionTriageSkill.execute(triage_input, economics)` via the `factory_dag.yaml` orchestrator.

## Driving it with SubprocessCLIHarness

```bash
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-01-stage-a-discovery
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-07-bayesian-kill-switch-sunset
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-08-ai-theater-zero-evoi-block
```

Observable end state: JSON output on stdout with `"triage_action"` matching `"fast_track_experiment"`, `"sunset_kill_switch"`, or `"block_ai_theater"`, exit code `0`, and durable proof JSON written to the harness `evidence_root` that survives `cleanup()`.

## Gotchas

- `prior_success_prob` must be strictly inside $(0.0, 1.0)$ and `likelihood_ratio` strictly $> 0.0$; boundary values `0.0` or `1.0` are rejected by Liskov precondition checks.
- Always run `harness.doctor()` before `harness.drive()`; driving an unchecked instance raises `HarnessStateError`.
