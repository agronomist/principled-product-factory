# Multi-Product Harness, DAG State-Machine & Evaluation Gate Specifications (`v10`)

This reference accompanies `.claude/skills/principled-product-builder/SKILL.md` and specifies the repository topology, Parnas module boundaries, typed DAG YAML state-machine contracts, SRE fallback chains, and Tier A/B/C evaluation gates.

---

## 1. Multi-Product Repository Layout (`platform/` + `products/`)

The software factory separates **shared horizontal infrastructure** (`platform/`) from **isolated vertical product lines** (`products/<product-slug>/`):

```text
principled-product-factory/
├── CLAUDE.md                                           # Repo-wide operating laws & merge gates
├── README.md                                           # Rauch-style Before vs. After quickstart
├── .claude/
│   └── skills/
│       └── principled-product-builder/
│           ├── SKILL.md                                # Full v10 operating specification
│           └── references/
│               ├── frameworks.md                       # Tier-1 math, Tier-2 canons, metaphors
│               └── harness_eval_specs.md               # Topology, DAG YAML schema, Tier A/B/C gates
├── .agents/
│   └── skills/
│       └── principled-product-builder/                 # Symlink/mirror to .claude skill
├── platform/                                           # Shared multi-product substrate (Rule-of-Two)
│   ├── __init__.py
│   ├── metering/
│   │   ├── __init__.py
│   │   └── margin_guard.py                             # Contribution Margin Gate & Cohort P&L
│   ├── telemetry/
│   │   ├── __init__.py
│   │   └── learning_signal.py                          # Idempotent event tuples & 4-axis scorecard
│   ├── sre/
│   │   ├── __init__.py
│   │   └── fallback_circuit.py                         # 3-tier circuit breaker & BlamelessPostMortem
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── dag_runner.py                               # WIP_LIMIT=5, Bellman router, SHA-256 Saga rollback
│   └── evals/
│       ├── __init__.py
│       └── runner.py                                   # Tier A, Tier B (kappa >= 0.80), Tier C (CUPED/SRM)
├── products/                                           # Isolated vertical product implementations
│   └── demo-decision-engine/
│       ├── __init__.py
│       ├── skills/
│       │   ├── __init__.py
│       │   └── decision_triage.py                      # Liskov-verified domain skill + diff telemetry
│       ├── workflows/
│       │   └── factory_dag.yaml                        # Typed state-machine DAG definition
│       └── evals/
│           └── golden_cases.jsonl                      # 10 verified golden & boundary test cases
└── tests/
    └── test_factory.py                                 # Pytest + Hypothesis property-based test suite
```

### 1.1 Rule-of-Two Extraction Law & Dependency Direction
1. **Strict DAG Dependency Rule**:
   - `products/<product-a>` MAY import from `platform.*`.
   - `products/<product-a>` MUST NEVER import from `products/<product-b>`.
   - `platform.*` MUST NEVER import from `products.*`.
2. **Rule-of-Two Extraction**:
   - A domain helper stays inside `products/<product-a>/skills/` during Stage A discovery.
   - The moment a second product (`products/<product-b>/`) needs the same primitive, it MUST be generalized behind a frozen Pydantic v2 contract, equipped with Liskov pre/postconditions and Hypothesis property tests, and extracted into `platform/`.

---

## 2. Typed State-Machine DAG YAML & SRE Fallback Chain Schema

Every workflow under `products/<slug>/workflows/*.yaml` is parsed and validated into strict Pydantic v2 models by [dag_runner.py](file:///home/antigravity/principled-product-factory/platform/orchestrator/dag_runner.py).

### 2.1 Canonical `factory_dag.yaml` Structure

```yaml
workflow_id: "demo-decision-engine-v10"
version: "10.0.0"
lifecycle_stage: "Stage_B"
wip_limit: 5

margin_policy:
  min_margin_usd: 0.05
  min_margin_ratio: 0.65
  default_unit_revenue_usd: 0.50

sre_fallback_chain:
  tiers:
    - primary_frontier_model
    - secondary_distilled_model
    - tertiary_cached_deterministic
  failure_threshold: 2
  recovery_timeout_seconds: 30.0
  shewhart_sigma_limit: 3.0

routing_policy:
  complexity_threshold: 0.65
  risk_threshold: 0.60
  min_margin_headroom_usd: 0.10
  low_complexity_route: "fast_implement"
  high_complexity_route: "parallel_fan_out"

nodes:
  - node_id: "validate_margin_gate"
    description: "Pre-flight Contribution Margin Gate verification"
    dependencies: []
    skill_ref: "platform.metering.margin_guard"
    compensating_action: "release_margin_reservation"
    timeout_ms: 500
    max_retries: 2

  - node_id: "execute_decision_triage"
    description: "Run Liskov-verified decision triage with 3-tier SRE fallback"
    dependencies: ["validate_margin_gate"]
    skill_ref: "products.demo_decision_engine.skills.decision_triage"
    compensating_action: "revert_triage_state"
    timeout_ms: 2500
    max_retries: 2

  - node_id: "emit_learning_signal"
    description: "Record idempotent zero-friction learning tuple and 4-axis scorecard"
    dependencies: ["execute_decision_triage"]
    skill_ref: "platform.telemetry.learning_signal"
    compensating_action: "void_learning_signal"
    timeout_ms: 500
    max_retries: 2
```

### 2.2 Orchestrator Execution Invariants
1. **Little's Law WIP Semaphore**: Concurrency is strictly bounded by `WIP_LIMIT = 5`. Any excess concurrent workflow requests are rejected with `WIPLimitExceededError` or queued deterministically.
2. **Bellman Complexity/Risk/Margin Router**:
   - Evaluates state vector $s = (\text{complexity}, \text{risk}, \text{margin\_headroom}, \text{evoi})$.
   - Selects `parallel_fan_out` if and only if $(\text{complexity} \ge \theta_c \lor \text{risk} \ge \theta_r)$ AND $\text{margin\_headroom} \ge M_{\text{headroom}}$ AND $\text{evoi} > 0$; otherwise routes to `fast_implement`.
3. **SHA-256 Error-Signature Deduplication & Saga Rollback**:
   - Every node exception is normalized into an error signature:
     $$\text{sig} = \text{SHA256}(\texttt{node\_id} \parallel \texttt{exception\_type} \parallel \texttt{normalized\_message})$$
   - If the same $\text{sig}$ occurs twice within a node's execution attempts, retry loops halt **immediately** (zero wasted tokens on identical deterministic failures).
   - The orchestrator runs all completed nodes' `compensating_action` callbacks in **reverse topological order** (Saga rollback) and emits a structured `HITLEscalationTicket`.

---

## 3. Multi-Tier Evaluation Gates (Tier A, Tier B, Tier C)

Implemented in [runner.py](file:///home/antigravity/principled-product-factory/platform/evals/runner.py). Merging to main requires **100% pass rate on Tier A and Tier B**, and staging-to-production promotion requires **Tier C pass**.

### 3.1 Tier A: Deterministic Contracts & Property Invariants (Pre-Commit / CI Gate)
- **Scope**: Pydantic v2 schema strictness, Liskov precondition/postcondition satisfaction, Parnas state encapsulation, Little's Law WIP bounds, Contribution Margin algebraic invariants, and duplicate SHA-256 error-signature Saga rollbacks.
- **Pass Criterion**: $100\%$ of contract and property invariants pass (`pass_rate == 1.0`). Zero tolerance for schema violations or uncompensated Saga states.

### 3.2 Tier B: Golden Dataset, Trajectory Efficiency & Judge Calibration (Pre-Merge Gate)
- **Scope**: Runs the product workflow against `evals/golden_cases.jsonl` (10 verified cases covering normal operation, edge cases, fallback transitions, and margin boundary checks).
- **Metrics Enforced**:
  1. **Golden Accuracy**: $100\%$ exact match on expected triage decision, margin gate pass/block outcome, and SRE tier selection.
  2. **Trajectory Step & Cost Efficiency**: Actual DAG steps executed $\le \text{max\_allowed\_steps}$ and actual unit cost $\le \text{max\_allowed\_cost\_usd}$.
  3. **Evaluator Calibration (Cohen's $\kappa$)**: Compares automated evaluator ratings against human expert reference labels across the calibration set. Requires:
     $$\kappa = \frac{p_o - p_e}{1 - p_e} \ge 0.80$$

### 3.3 Tier C: Online Experimentation, CUPED Variance Reduction & SRM Check (Production Rollout Gate)
- **Scope**: Statistical validation of A/B or shadow-traffic telemetry before scaling a Stage B/C capability.
- **Metrics Enforced**:
  1. **Sample Ratio Mismatch (SRM) Gate**: Computes Pearson's $\chi^2$ statistic between observed $(N_{\text{control}}, N_{\text{treatment}})$ and expected split proportions. Passes if and only if $p\text{-value} \ge 0.01$. If $p < 0.01$, the experiment is halted and quarantined.
  2. **CUPED Variance Reduction**: Computes covariate-adjusted treatment outcomes $\hat{Y}_{\text{CUPED}} = Y - \theta (X - \bar{X})$, verifying variance reduction $\text{Var}(\hat{Y}_{\text{CUPED}}) \le \text{Var}(Y)$ and estimating the precision-adjusted Average Treatment Effect (ATE) and $95\%$ confidence interval.
