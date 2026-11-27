# CLAUDE.md — Operating Laws for `principled-product-factory` (`v10`)

Every human engineer and autonomous coding agent operating in this repository MUST follow the **`principled-product-builder-v10`** specification in [.claude/skills/principled-product-builder/SKILL.md](file:///home/antigravity/principled-product-factory/.claude/skills/principled-product-builder/SKILL.md).

---

## Law 1: Mandatory Step 0 Stage Triage & Bayesian Kill-Switch Before Planning

Before drafting an implementation plan, creating a product directory, or writing code:
1. **Declare Lifecycle Stage**: Classify the work explicitly as:
   - **`Stage A` (0-to-1 Discovery)**: Falsify value and willingness-to-pay hypotheses with minimal burn inside an isolated `products/<slug>/` leaf.
   - **`Stage B` (PMF & Growth)**: Lock in repeatable unit economics ($\text{Contribution Margin} \ge 65\%$, $\text{CAC Payback} \le 12\text{ months}$) and calibrated golden evaluations ($\kappa \ge 0.80$).
   - **`Stage C` (Enterprise & Multi-Product Scale)**: Enforce full multi-product leverage, 3-tier SRE fallback circuits, CUPED/SRM Tier C gates, and automated Shewhart $\pm 3\sigma$ regression fixtures.
2. **Declare Bayesian Kill-Switch Threshold**: State the prior probability $P(H)$, minimum viable posterior $P_{\text{kill}}$, and sample size/timebox. If posterior evidence falls below $P_{\text{kill}}$ or unit contribution margin remains negative after two pricing/distillation iterations, sunset the bet immediately.
3. **Compute EVOI & 4-Axis AI-Native Filter**: Block any "AI bolt-on theater" where $\text{EVOI} \le 0$ or deterministic rules suffice.

---

## Law 2: Rule-of-Two Extraction into `platform/` & Parnas Information Hiding

1. **Topological Isolation**:
   - Shared horizontal primitives live in `platform/` (`metering`, `telemetry`, `sre`, `orchestrator`, `evals`).
   - Vertical product lines live in `products/<product-slug>/`.
   - Products MUST NEVER import from other products (`products/a` $\not\to$ `products/b`). `platform/` MUST NEVER import from `products/`.
2. **Rule-of-Two Extraction**:
   - The first product to need a capability builds it locally inside `products/<product-a>/skills/`.
   - The moment a **second** product needs that capability, you MUST extract it into `platform/` behind an immutable Pydantic v2 data contract before writing duplicate product code.
3. **Liskov Substitution & Parnas Boundaries**:
   - Every module boundary is typed with Pydantic v2 (`ConfigDict(extra="forbid", frozen=True)` for value objects).
   - Every skill enforces explicit Liskov preconditions (`validate_preconditions`) and postconditions (`validate_postconditions`). Subtypes never strengthen preconditions or weaken postconditions.

---

## Law 3: Mandatory Contribution Margin Gate & SRE Circuit Protection

No workflow node or model invocation may bypass the financial and reliability rails:
1. **Contribution Margin Gate** ([platform/metering/margin_guard.py](file:///home/antigravity/principled-product-factory/platform/metering/margin_guard.py)):
   $$\texttt{unit\_revenue} - \left(\texttt{inference\_cost} + \texttt{data\_api\_cost} + \texttt{hitl\_prob} \cdot \texttt{human\_review\_cost} + \texttt{infra\_cost}\right) \ge \texttt{min\_margin}$$
   Transactions violating this inequality are rejected pre-flight or routed to a lower-cost SRE tier.
2. **3-Tier SRE Fallback Chain** ([platform/sre/fallback_circuit.py](file:///home/antigravity/principled-product-factory/platform/sre/fallback_circuit.py)):
   Every inference/external dependency must degrade gracefully through:
   `primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`.
3. **Little's Law & SHA-256 Saga Rollbacks** ([platform/orchestrator/dag_runner.py](file:///home/antigravity/principled-product-factory/platform/orchestrator/dag_runner.py)):
   - Concurrency is capped at `WIP_LIMIT = 5`.
   - Duplicate SHA-256 error signatures halt retries on the spot, execute reverse-order Saga compensating actions, and emit a structured HITL escalation ticket.
   - Every SEV incident or Shewhart $\pm 3\sigma$ excursion must compile into a minimized JSON regression fixture via `BlamelessPostMortem`.

---

## Law 4: 100% Tier A & Tier B Eval Passes Before Merge

No pull request or commit may be merged unless:
1. **Tier A (Contracts & Property Invariants)**: 100% pass rate on Liskov contracts, Pydantic v2 schemas, Little's Law WIP caps, Contribution Margin invariants, and duplicate error-signature Saga rollbacks.
2. **Tier B (Golden Dataset, Efficiency & Calibration)**: 100% pass rate on `evals/golden_cases.jsonl`, trajectory step/cost budgets satisfied, and evaluator calibration Cohen's $\kappa \ge 0.80$.
3. **Tier C (Production Rollout Validation)**: Sample Ratio Mismatch chi-square check $p \ge 0.01$ and CUPED variance-reduced treatment effect verification.

---

## Law 5: Dynamic Workflows, Closed Loops, Live Harnesses & Structural Ratchets (`pstack` Integration)

Every autonomous or multi-step run MUST enforce the following five `pstack` execution rules:

| Rule | Enforcing Code / Structural Check |
| :--- | :--- |
| **Attack the Premise (`principle-attack-the-premise`)**: After 2 failed fixes on the same gate, block fix #3 until the shared premise is written down and probed directly. | [`PremiseTracker`](file:///home/antigravity/principled-product-factory/platform/orchestrator/loop_engine.py#L48-L106) (`PremiseBlockedError`) |
| **Scientific Hillclimb & Audit Trail (`/figure-it-out` & `/show-me-your-work`)**: Bracket every unit (`baseline -> hypothesis -> verify -> keep/revert`) and log append-only rows to `decisions.tsv` audited by a cross-vendor model. | [`ScientificHillclimbLoop`](file:///home/antigravity/principled-product-factory/platform/orchestrator/loop_engine.py#L148-L270) & [`DecisionTrailLogger`](file:///home/antigravity/principled-product-factory/platform/audit/decision_trail.py#L130-L300) |
| **Isolated Arena Bakeoff (`/arena`)**: For `parallel_fan_out`, run $N$ candidates in separate workspaces, score via a cross-vendor judge, pick the cleanest base (Laziness Protocol), and graft losing strengths. | [`ArenaExecutor`](file:///home/antigravity/principled-product-factory/platform/orchestrator/loop_engine.py#L305-L398) |
| **Live Control Harness & Feature Map (`/create-verification-skill` & `/maintain-verification-skill`)**: Never `drive()` an instance without a fresh green `doctor()` check; ensure evidence survives `cleanup()`; keep `features/*.md` synced. | [`SubprocessCLIHarness`](file:///home/antigravity/principled-product-factory/platform/harness/control_harness.py#L204-L275) & [`FeatureMapAuditor`](file:///home/antigravity/principled-product-factory/platform/harness/control_harness.py#L314-L382) |
| **Adversarial Interrogation, Mutation Proofs & Fix-Naming Lints (`/interrogate`, `/create-formal-verification-skill`, `/correct`)**: Drop unexecuted opinions; prove every check fails on a broken mutation; enforce AST architecture/type barriers with fix-naming lint errors. | [`AdversarialInterrogator`](file:///home/antigravity/principled-product-factory/platform/evals/interrogator.py#L72-L148), [`MutationProofVerifier`](file:///home/antigravity/principled-product-factory/platform/evals/interrogator.py#L179-L217), & [`StructuralRatchetLinter`](file:///home/antigravity/principled-product-factory/platform/evals/interrogator.py#L243-L370) |

---

## Law 6: Vercel `eve` / Foreman Software Factory Pipeline & Security Boundaries

When turning inbound GitHub/Linear work items into reviewed draft pull requests via [`platform/foreman/stations.py`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py):
1. **The Orchestrator Routes, Not Writes (No Self-Delegation)**:
   - [`ForemanOrchestrator`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L486-L654) structurally disables self-delegation (`delegate_to_self()` raises `PermissionError`) and routes every item through four task-mode stations in strict order: `classifier -> analyst -> implementer -> reviewer` (+ optional `researcher`).
   - If `classifier` returns `needs_clarification=True`, the pipeline stops immediately and posts clarification questions rather than stranding an unattended session.
2. **Independent Cross-Vendor Review & Bounded Revisions**:
   - `reviewer` runs on a different model vendor than `implementer` ([`StationModelConfig`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L462-L483)), never receives `implementer.internal_reasoning` ([`ReviewerBrief`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L397-L413)), and grades the analyst's acceptance criteria verbatim.
   - `request_changes` loops are capped at `MAX_REVISION_ROUNDS = 2`.
3. **Pass-by-ID Handoff Artifacts & Anti-Poisoning Factory Brain**:
   - Long station memos travel by regex-anchored ID (`^[a-z0-9]+(?:-[a-z0-9]+)*$`) in [`HandoffArtifactStore`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L198-L234) with zero dots or slashes (preventing `../` traversal and orchestrator context bloat).
   - [`FactoryBrain`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L237-L282) keys are derived purely from `SHA256(FACTORY_REPO)` at module load, and writes from `UNATTENDED_AUTONOMOUS` runs are denied outright so prompt-injected issue bodies cannot poison future runs.
4. **Input-Aware Approval Matrix & Draft-PR Unattended Ceiling**:
   - [`ForemanApprovalPolicy`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L81-L185) inspects both tool name and input: `create_pull_request(draft=True)` runs ungated, `draft=False` / `mark_pr_ready` is **denied** on unattended runs (never parked!) and parks for human approval on interactive sessions, and `merge_pull_request` is structurally absent from the tool surface.
5. **Inert-by-Construction Git Branches, Firewall Egress Broker & Red-CI Cap**:
   - [`validate_branch_name`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L295-L313) blocks `main`, `master`, `HEAD`, `refs/*`, `..`, and non-`factory/` branches.
   - [`FirewallCredentialBroker`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L325-L359) injects git tokens only at the sandbox firewall egress layer to literal `https://github.com/<FACTORY_REPO>.git`, never trusting model-writable remotes.
   - [`RedCIFixLoopGuard`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L362-L392) restricts automated CI fixes to `factory/*` branches and stops after 2 attempts.

---

## Law 7: Anti-Build-Trap Customer Value Gate & Post-Ship Zombie Sunset (`platform/discovery/build_trap_guard.py`)

We build strictly for the customer to solve an acute, underserved problem—**never** "just because someone at some point will like it" (Melissa Perri's *Escaping the Build Trap* / Rob Fitzpatrick's *The Mom Test* / Tony Ulwick's *Outcome-Driven Innovation*):

1. **No Speculative Features or Polite Compliments**:
   - [`BuildTrapGate`](file:///home/antigravity/principled-product-factory/platform/discovery/build_trap_guard.py#L196-L343) blocks any feature proposal backed only by `CommitmentTier.SPECULATIVE_IDEA` or `CommitmentTier.POLITE_COMPLIMENT`.
   - Engineering buildout requires real customer skin-in-the-game (`TIME_COMMITMENT` for Stage A probes; `REPUTATION_COMMITMENT` or `FINANCIAL_OR_PAIN_COMMITMENT` with cited `evidence_pointers` for Stage B/C buildout).
2. **Ulwick JTBD Opportunity Score Gate ($\ge 10.0$)**:
   - Every feature must quantify customer importance and current satisfaction on the struggling job step:
     $$\text{OpportunityScore} = \text{Importance} + \max(\text{Importance} - \text{Satisfaction}, 0) \ge 10.0$$
   - Overserved jobs ($< 10.0$) are rejected before reaching the `analyst` or `implementer` stations ([`ForemanPipelineStatus.HALTED_BUILD_TRAP_NO_CUSTOMER_VALUE`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L461)).
3. **Falsifiable Customer Outcome Shift & Post-Ship Zombie Feature Sunset**:
   - Every feature declares a measurable customer behavior shift (`baseline_metric_value -> target_metric_value` over `evaluation_window_days`).
   - Post-launch, [`PostShipOutcomeAudit`](file:///home/antigravity/principled-product-factory/platform/discovery/build_trap_guard.py#L387-L444) compares realized customer adoption and outcome lift against the promise. Features that fail to reach $40\%$ of target adoption and $25\%$ of promised outcome lift are flagged as **Zombie Features** (`SUNSET_AND_DELETE_CODE`) and removed from the codebase (`principle-subtract-before-you-add`).

---

## Law 8: Challenger Sale (`Teach, Tailor, Take Control`) & JOLT Pipeline Engine (`platform/gtm/challenger_pipeline.py`)

Why do software companies fall into the Build Trap in the first place? Because **"Relationship Builder"** sales reps acquiesce to every prospect's bespoke one-off feature request and discount demand just to keep the buyer happy. Matthew Dixon & Brent Adamson's *The Challenger Sale* and *The JOLT Effect* prove that **Relationship Builders account for only 4% of high performers in complex B2B sales, while Challengers account for 54%**:

1. **Teach for Differentiation (The 6-Step Commercial Teaching Choreography)**:
   - Enforced by [`ChallengerChoreographyValidator`](file:///home/antigravity/principled-product-factory/platform/gtm/challenger_pipeline.py#L142-L214):
     1. **The Warmer**: Lead with benchmarked industry observations—never ask the lazy *"What keeps you up at night?"* cliché.
     2. **The Reframe**: Expose a counter-intuitive structural blind spot the customer thought was a normal cost of doing business.
     3. **Rational Drowning**: Quantify their exact annual Cost of Inaction ($\text{COI} \ge 3.0\times \text{ACV}$, payback $\le 4$ months).
     4. **Emotional Impact**: Connect the broken status quo to their team's day-to-day operational pain.
     5. **A New Way**: Define the behavioral/architectural capabilities required to solve the reframe—**before** pitching product SKU features.
     6. **Our Solution Map**: Prove how our unique platform invariants are the only way to execute Step 5.
2. **Tailor for Resonance Across the Consensus Committee**:
   - [`ChallengerPipelineEngine.tailor_for_committee`](file:///home/antigravity/principled-product-factory/platform/gtm/challenger_pipeline.py#L334-L380) translates the same commercial reframe into stakeholder-specific outcomes for the `ECONOMIC_BUYER_CFO`, `TECHNICAL_ARCHITECT_VP_ENG`, `MOBILIZER_CHAMPION`, and `END_USER_OPERATOR`.
3. **Take Control of the Sale (Constructive Tension = Anti-Build-Trap + Margin Guard)**:
   - [`ChallengerPipelineEngine.evaluate_constructive_tension`](file:///home/antigravity/principled-product-factory/platform/gtm/challenger_pipeline.py#L382-L448) pushes back on bespoke one-off prospect demands that fail [`BuildTrapGate`](file:///home/antigravity/principled-product-factory/platform/discovery/build_trap_guard.py#L196-L343) and rejects any price discount that either lacks a concrete **Give-Get** concession or violates [`ContributionMarginGate`](file:///home/antigravity/principled-product-factory/platform/metering/margin_guard.py#L142-L263).
4. **Overcome Customer Indecision (*The JOLT Effect*)**:
   - 40–60% of enterprise pipeline is lost to **"No Decision"** caused by customer **FOMU (Fear of Messing Up)**. [`ChallengerPipelineEngine.build_jolt_playbook`](file:///home/antigravity/principled-product-factory/platform/gtm/challenger_pipeline.py#L450-L491) applies the 4 JOLT moves: **J**udge the indecision, **O**ffer a bold recommendation (eliminating option overload), **L**imit the exploration (capping POC creep to our 10 golden cases + live CLI harness), and **T**ake risk off the table (3-tier SRE fallback SLA + 6-month re-pricing retro-audit).

---

## Law 9: Continuous Customer Learning & Adaptation Flywheel (`platform/discovery/adaptation_flywheel.py`)

We do not merely filter ideas—we continuously learn from and adapt to how customers actually work:

1. **Correction-Diff Clustering $\to$ Autonomous Product Adaptation**:
   - [`CorrectionDiffClusterer`](file:///home/antigravity/principled-product-factory/platform/discovery/adaptation_flywheel.py#L75-L185) mines passive `user_correction_diff` tuples from [`IdempotentLearningLogger`](file:///home/antigravity/principled-product-factory/platform/telemetry/learning_signal.py#L283-L355).
   - Once $\ge 3$ independent customer runs override a system default in the same direction, it automatically synthesizes a golden evaluation assertion and a validated [`WorkItemIntake`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L311-L331) for [`ForemanOrchestrator`](file:///home/antigravity/principled-product-factory/platform/foreman/stations.py#L502-L702).
2. **Emergent Demand & Sales Objection Accumulator ($N=1 \to N=3 \to N=10$)**:
   - [`DemandSignalAccumulator`](file:///home/antigravity/principled-product-factory/platform/discovery/adaptation_flywheel.py#L232-L347) records rejected sales requests and customer workarounds per distinct `customer_account_id`:
     - **$N < 3$**: Quarantined (`QUARANTINED_NOISE_OR_ONE_OFF`) so a single loud prospect cannot drag the factory into the Build Trap.
     - **$3 \le N < 10$** (with $\ge \text{TIME\_COMMITMENT}$ and Ulwick score $\ge 10.0$): Automatically unlocks `PROMOTED_TO_STAGE_A_DISCOVERY_PROBE`.
     - **$N \ge 10$** (with $\ge \text{REPUTATION\_COMMITMENT}$ or `FINANCIAL_OR_PAIN_COMMITMENT`): Automatically graduates to `GRADUATED_TO_STAGE_B_PRODUCTION_BUILD`.
3. **Bayesian JTBD Belief Updating from Customer Workarounds**:
   - [`BayesianJTBDBeliefUpdater`](file:///home/antigravity/principled-product-factory/platform/discovery/adaptation_flywheel.py#L419-L468) updates our prior Importance and Satisfaction estimates using live behavioral telemetry (`observed_workaround_rate` and `observed_task_drop_off_rate`), escalating underestimated customer pain onto the roadmap automatically.

---

## Law 10: Industrial Factory Floor Operations (`platform/factory_floor/operations.py`)

A multi-product software factory requires industrial floor controls from product stamping through progressive canary delivery and bottleneck management:

1. **Product-Line Stamping Press & Automated Rule-of-Two AST Harvester**:
   - [`ProductLineStampingPress`](file:///home/antigravity/principled-product-factory/platform/factory_floor/operations.py#L81-L165) stamps out a complete vertical product line under `products/<product-slug>/` only after [`BuildTrapGate`](file:///home/antigravity/principled-product-factory/platform/discovery/build_trap_guard.py#L196-L343) passes.
   - [`RuleOfTwoASTHarvester`](file:///home/antigravity/principled-product-factory/platform/factory_floor/operations.py#L178-L227) scans normalized ASTs across all products under `products/*` and flags a [`CrossProductDuplicationFinding`](file:///home/antigravity/principled-product-factory/platform/factory_floor/operations.py#L168-L175) whenever $\ge 2$ products implement structurally identical functions, prescribing extraction into `platform/`.
2. **Supply-Chain BOM & Porter Supplier-Shock Simulator**:
   - [`SupplyChainBOMRegistry`](file:///home/antigravity/principled-product-factory/platform/factory_floor/operations.py#L251-L299) tracks every product's foundation model and data API Bill of Materials and simulates upstream supplier price shocks (e.g., 3x token price hikes), prescribing automatic distillation switches before unit contribution margins turn negative.
3. **Sealed Holdout Digital Twin (Dark-Factory Wind Tunnel)**:
   - [`HoldoutDigitalTwin`](file:///home/antigravity/principled-product-factory/platform/factory_floor/operations.py#L324-L355) replays sealed shadow-traffic scenarios stored outside the implementer agent's repository view so coding agents cannot overfit to `golden_cases.jsonl`.
4. **Progressive Canary Rollout Controller (`1% -> 10% -> 50% -> 100%`)**:
   - [`CanaryRolloutController`](file:///home/antigravity/principled-product-factory/platform/factory_floor/operations.py#L392-L511) gates every traffic ramp on Shewhart $\pm 3\sigma$ latency limits, SRM $\chi^2$ ($p \ge 0.01$), and live unit Contribution Margin. Any breach automatically rolls back to `0%` and compiles a minimized JSON regression fixture via [`BlamelessPostMortem`](file:///home/antigravity/principled-product-factory/platform/sre/fallback_circuit.py#L332-L433).
5. **Factory Floor OEE & Goldratt Theory of Constraints Monitor**:
   - [`FactoryOEEMonitor`](file:///home/antigravity/principled-product-factory/platform/factory_floor/operations.py#L543-L600) computes $\text{OEE} = \text{Availability} \times \text{Performance} \times \text{FirstPassYield}$, tracks Scrap/Rework Cost Ratio, and pinpoints the exact bottleneck station on the assembly line.

### Verification Commands
```bash
# Run the full Pytest + Hypothesis property-based test suite (29 test suites)
pytest -v

# Run the multi-tier evaluation suite and reference DAG workflow directly
python3 -m platform.evals.runner

# Drive the reference product as an isolated black-box CLI subprocess
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-10-sre-double-fallback-to-tertiary
```
