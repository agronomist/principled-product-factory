# `principled-product-factory` (`v10`)

Multi-product software factory implementing the **`principled-product-builder-v10`** operating system: mandatory lifecycle stage routing, Bayesian portfolio kill-switches, Contribution Margin gates, Little's Law DAG orchestration (`WIP_LIMIT = 5`), 3-tier SRE graceful degradation, idempotent flywheel telemetry, and Tier A/B/C statistical evaluation gates.

---

## Before vs. After Primitives

| Surface | Before (Ad-Hoc AI Wrapper / Feature Factory) | After (`principled-product-builder-v10`) |
| :--- | :--- | :--- |
| **Stage & Capital Governance** | One-size-fits-all process; zombie bets drag on for quarters on sunk-cost inertia. | **Step 0 Router** (`Stage A` Discovery vs. `Stage B` Growth vs. `Stage C` Scale) + **Bayesian Kill-Switches** that sunset bets when posterior odds drop below $P_{\text{kill}}$. |
| **AI Feature Triage** | "AI Bolt-On Theater": slapping an LLM chat box onto tasks where $\text{EVOI} = 0$ or a 10-line SQL query suffices. | **4-Axis AI-Native Scorecard** (Workflow Elimination, Flywheel Velocity, Deterministic Verifiability, Unit Margin Resilience) + hard **EVOI Gate**. |
| **Unit Economics** | Unbounded token & human-in-the-loop (HITL) costs discovered at end-of-quarter billing. | Pre-flight **Contribution Margin Gate**: `unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin` + **6-Month Re-Pricing Retro-Audit**. |
| **Concurrency & Retries** | Unbounded async fan-out thrashing downstream APIs; blind retry loops burning tokens on identical deterministic crashes. | **Little's Law WIP Semaphore** (`WIP_LIMIT = 5`), **Bellman Router** (`fast_implement` vs. `parallel_fan_out`), and **SHA-256 Error-Signature Deduplication** triggering immediate **Saga Rollback + HITL Escalation**. |
| **Reliability & Incidents** | Single foundation-model vendor lock-in; post-mortems filed as forgotten Google Docs. | **3-Tier SRE Fallback Circuit** (`primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`) + **`BlamelessPostMortem`** compiling SEV / Shewhart $\pm 3\sigma$ breaches into minimized JSON regression fixtures. |
| **Learning & Evaluation** | Nagging users with thumbs-up/down popups; uncalibrated LLM-as-a-judge vibes; noisy A/B readouts. | Zero-friction idempotent `(input_state, system_output, user_correction_diff, verified_outcome)` tuples + **Tier A** (Liskov/Hypothesis), **Tier B** (Golden set + Cohen's $\kappa \ge 0.80$), and **Tier C** (**CUPED** variance reduction + **SRM** $\chi^2$ check). |

---

## Repository Architecture

```text
principled-product-factory/
├── CLAUDE.md                                           # Repo operating laws & merge gates
├── README.md                                           # Quickstart & Before vs. After primitives
├── .claude/skills/principled-product-builder/
│   ├── SKILL.md                                        # Full v10 operating specification
│   └── references/
│       ├── frameworks.md                               # Tier-1 math, Tier-2 canons, metaphors
│       └── harness_eval_specs.md                       # Topology, DAG YAML schema, Tier A/B/C gates
├── .agents/skills/principled-product-builder/          # Symlink to .claude skill
├── platform/                                           # Shared multi-product substrate (Rule-of-Two)
│   ├── metering/margin_guard.py                        # Contribution Margin Gate & Cohort P&L
│   ├── telemetry/learning_signal.py                    # Idempotent 4-tuples & 4-axis AI scorecard
│   ├── sre/fallback_circuit.py                         # 3-tier circuit breaker & BlamelessPostMortem
│   ├── orchestrator/dag_runner.py                      # WIP_LIMIT=5, Bellman router, SHA-256 Saga
│   └── evals/runner.py                                 # Tier A, Tier B (kappa >= 0.80), Tier C (CUPED/SRM)
├── products/demo-decision-engine/                      # Reference vertical product implementation
│   ├── skills/decision_triage.py                       # Liskov-verified domain skill
│   ├── workflows/factory_dag.yaml                      # Typed state-machine DAG configuration
│   └── evals/golden_cases.jsonl                        # 10 verified golden & margin-boundary cases
└── tests/test_factory.py                               # Pytest + Hypothesis property-based test suite
```

---

## Quickstart (30 Seconds)

### 1. Run the Pytest + Hypothesis Property-Based Test Suite

```bash
pytest -v
```

### 2. Run the Reference Product DAG & Multi-Tier Evaluation Suite (Tier A / B / C)

```bash
python3 -m platform.evals.runner
```

### 3. Inspect a Single Decision Triage & Contribution Margin Execution in Python

```python
from platform.metering.margin_guard import UnitEconomicsInput
from products.demo_decision_engine.skills.decision_triage import (
    DecisionTriageInput,
    DecisionTriageSkill,
    LifecycleStage,
)

skill = DecisionTriageSkill()
output = skill.execute(
    DecisionTriageInput(
        proposal_id="bet-stage-b-autopilot",
        lifecycle_stage=LifecycleStage.STAGE_B,
        prior_success_prob=0.55,
        likelihood_ratio=2.20,
        evoi_usd=0.40,
        user_override_action=None,
    ),
    UnitEconomicsInput(
        transaction_id="tx-quickstart-01",
        unit_revenue=0.80,
        inference_cost=0.10,
        data_api_cost=0.04,
        hitl_prob=0.05,
        human_review_cost=1.00,
        infra_cost=0.03,
        min_margin=0.25,
    ),
)

print(output.model_dump_json(indent=2))
```
