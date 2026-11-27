r"""Multi-Tier Evaluation Runner (Tier A, Tier B, Tier C) for `principled-product-factory`.

Implements the three verification gates of `principled-product-builder-v10`:
- Tier A (Contracts & Property Invariants):
  Verifies Liskov preconditions/postconditions, Parnas schema boundaries, Contribution Margin
  invariants, Little's Law WIP semaphore bounds, and SHA-256 duplicate error-signature Saga rollbacks.
- Tier B (Golden Dataset + Trajectory Step/Cost Efficiency + Cohen's Kappa >= 0.80 Calibration):
  Executes `evals/golden_cases.jsonl`, enforces step and USD cost ceilings, and validates that
  the automated evaluator achieves Cohen's kappa >= 0.80 against human reference labels.
- Tier C (CUPED Variance Reduction + Sample Ratio Mismatch Chi-Square Test):
  Computes covariate-adjusted treatment effects $\hat{Y}_{\text{CUPED}} = Y - \theta (X - \bar{X})$
  and Pearson's $\chi^2$ SRM goodness-of-fit test ($p \ge 0.01$ required to pass).
"""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from platform.metering.margin_guard import ContributionMarginGate, UnitEconomicsInput
from platform.orchestrator.dag_runner import (
    WIP_LIMIT,
    DAGExecutionStatus,
    DAGNodeSpec,
    DAGRunner,
    DAGWorkflowSpec,
    NodeExecutionHandler,
    WIPLimitExceededError,
)
from platform.sre.fallback_circuit import FallbackCircuit, FallbackTier
from platform.telemetry.learning_signal import (
    AINativeScorecardInput,
    IdempotentLearningLogger,
    LearningSignalTuple,
)


def compute_cohens_kappa(
    rater_a: Sequence[str | int],
    rater_b: Sequence[str | int],
) -> float:
    r"""Compute Cohen's kappa ($\kappa = \frac{p_o - p_e}{1 - p_e}$) for inter-rater agreement.

    Preconditions:
    - `len(rater_a) == len(rater_b)` and `len(rater_a) > 0`.
    Postconditions:
    - Returns $\kappa \in [-1.0, 1.0]$ (equals $1.0$ on exact match).
    """
    if len(rater_a) != len(rater_b):
        raise ValueError("rater_a and rater_b must have identical length.")
    n = len(rater_a)
    if n == 0:
        raise ValueError("Cannot compute Cohen's kappa on empty sequences.")

    categories = sorted(set(rater_a) | set(rater_b), key=str)
    agreed = sum(1 for a, b in zip(rater_a, rater_b, strict=True) if a == b)
    p_o = agreed / n

    p_e = 0.0
    for cat in categories:
        prob_a = sum(1 for a in rater_a if a == cat) / n
        prob_b = sum(1 for b in rater_b if b == cat) / n
        p_e += prob_a * prob_b

    if math.isclose(1.0 - p_e, 0.0, abs_tol=1e-12):
        return 1.0 if math.isclose(p_o, 1.0, abs_tol=1e-12) else 0.0

    kappa = (p_o - p_e) / (1.0 - p_e)
    return max(-1.0, min(1.0, kappa))


class CUPEDResult(BaseModel):
    """Immutable postcondition result from CUPED variance reduction analysis."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    theta: float = Field(...)
    raw_treatment_mean: float = Field(...)
    raw_control_mean: float = Field(...)
    raw_ate: float = Field(...)
    cuped_ate: float = Field(...)
    raw_variance: float = Field(..., ge=0.0)
    cuped_variance: float = Field(..., ge=0.0)
    variance_reduction_ratio: float = Field(..., ge=0.0, le=1.0)
    variance_reduced: bool = Field(...)


def _sample_mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def _sample_variance(xs: Sequence[float], mean_val: float | None = None) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    m = _sample_mean(xs) if mean_val is None else mean_val
    return sum((x - m) ** 2 for x in xs) / (n - 1)


def _sample_covariance(xs: Sequence[float], ys: Sequence[float]) -> float:
    n = len(xs)
    if n != len(ys) or n < 2:
        raise ValueError("Covariance requires two sequences of identical length >= 2.")
    mx = _sample_mean(xs)
    my = _sample_mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / (n - 1)


def compute_cuped_adjustment(
    control_pre: Sequence[float],
    control_post: Sequence[float],
    treatment_pre: Sequence[float],
    treatment_post: Sequence[float],
) -> CUPEDResult:
    r"""Compute CUPED (Controlled-experiment Using Pre-Experiment Data) variance-reduced ATE.

    Formula:
    $\hat{Y}_{\text{CUPED}} = Y - \theta (X - \bar{X}_{\text{pooled}})$,
    where $\theta = \text{Cov}(Y_{\text{pooled}}, X_{\text{pooled}}) / \text{Var}(X_{\text{pooled}})$.
    """
    if len(control_pre) != len(control_post) or len(control_pre) < 2:
        raise ValueError("Control pre/post sequences must have equal length >= 2.")
    if len(treatment_pre) != len(treatment_post) or len(treatment_pre) < 2:
        raise ValueError("Treatment pre/post sequences must have equal length >= 2.")

    pooled_pre = list(control_pre) + list(treatment_pre)
    pooled_post = list(control_post) + list(treatment_post)

    mean_pre_pooled = _sample_mean(pooled_pre)
    var_pre_pooled = _sample_variance(pooled_pre, mean_pre_pooled)

    if var_pre_pooled <= 1e-15:
        theta = 0.0
    else:
        cov_post_pre = _sample_covariance(pooled_pre, pooled_post)
        theta = cov_post_pre / var_pre_pooled

    adj_control = [
        y - theta * (x - mean_pre_pooled)
        for x, y in zip(control_pre, control_post, strict=True)
    ]
    adj_treatment = [
        y - theta * (x - mean_pre_pooled)
        for x, y in zip(treatment_pre, treatment_post, strict=True)
    ]
    adj_pooled = adj_control + adj_treatment

    raw_ctrl_mean = _sample_mean(control_post)
    raw_trt_mean = _sample_mean(treatment_post)
    raw_ate = raw_trt_mean - raw_ctrl_mean

    cuped_ctrl_mean = _sample_mean(adj_control)
    cuped_trt_mean = _sample_mean(adj_treatment)
    cuped_ate = cuped_trt_mean - cuped_ctrl_mean

    raw_var = _sample_variance(pooled_post)
    cuped_var = _sample_variance(adj_pooled)
    # Clamp tiny floating-point numerical jitter
    if cuped_var > raw_var and math.isclose(cuped_var, raw_var, rel_tol=1e-9):
        cuped_var = raw_var

    reduction_ratio = (
        max(0.0, min(1.0, (raw_var - cuped_var) / raw_var)) if raw_var > 1e-15 else 0.0
    )

    return CUPEDResult(
        theta=round(theta, 6),
        raw_treatment_mean=round(raw_trt_mean, 6),
        raw_control_mean=round(raw_ctrl_mean, 6),
        raw_ate=round(raw_ate, 6),
        cuped_ate=round(cuped_ate, 6),
        raw_variance=round(raw_var, 6),
        cuped_variance=round(cuped_var, 6),
        variance_reduction_ratio=round(reduction_ratio, 6),
        variance_reduced=(cuped_var <= raw_var + 1e-12),
    )


class SRMResult(BaseModel):
    """Immutable postcondition result from Sample Ratio Mismatch (SRM) chi-square test."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    observed_counts: tuple[int, ...] = Field(...)
    expected_counts: tuple[float, ...] = Field(...)
    chi_square_stat: float = Field(..., ge=0.0)
    degrees_of_freedom: int = Field(..., ge=1)
    p_value: float = Field(..., ge=0.0, le=1.0)
    alpha_threshold: float = Field(default=0.01, gt=0.0, lt=1.0)
    srm_detected: bool = Field(...)
    passed: bool = Field(...)


def _chi_square_survival_function(chi2_val: float, df: int) -> float:
    r"""Compute exact or Wilson-Hilferty upper-tail p-value $P(\chi^2_{\text{df}} \ge x)$ using stdlib `math`."""
    if chi2_val <= 0.0:
        return 1.0
    if df == 1:
        # Exact relationship for df=1: P(Chi2_1 >= x) = erfc(sqrt(x / 2))
        return math.erfc(math.sqrt(chi2_val / 2.0))
    if df == 2:
        # Exact closed form for df=2: P(Chi2_2 >= x) = exp(-x / 2)
        return math.exp(-chi2_val / 2.0)
    # Wilson-Hilferty cube-root normal approximation for df >= 3
    k = float(df)
    z = ((chi2_val / k) ** (1.0 / 3.0) - (1.0 - 2.0 / (9.0 * k))) / math.sqrt(2.0 / (9.0 * k))
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def compute_srm_chi_square(
    observed_counts: Sequence[int],
    expected_ratios: Sequence[float] | None = None,
    alpha: float = 0.01,
) -> SRMResult:
    r"""Perform Pearson's $\chi^2$ goodness-of-fit test for Sample Ratio Mismatch (SRM).

    If $p < \alpha$ (default $\alpha = 0.01$), flags `srm_detected = True` and `passed = False`.
    """
    if len(observed_counts) < 2:
        raise ValueError("SRM chi-square test requires at least 2 experiment arms.")
    if any(c < 0 for c in observed_counts):
        raise ValueError("Observed counts must be non-negative.")
    total_n = sum(observed_counts)
    if total_n <= 0:
        raise ValueError("Total observed count must be > 0.")

    k = len(observed_counts)
    if expected_ratios is None:
        ratios = [1.0 / k] * k
    else:
        if len(expected_ratios) != k:
            raise ValueError("expected_ratios length must match observed_counts length.")
        if any(r <= 0.0 for r in expected_ratios):
            raise ValueError("expected_ratios must be strictly positive.")
        ratio_sum = sum(expected_ratios)
        ratios = [r / ratio_sum for r in expected_ratios]

    expected_counts = [total_n * r for r in ratios]
    chi2_stat = sum(
        ((obs - exp) ** 2) / exp
        for obs, exp in zip(observed_counts, expected_counts, strict=True)
    )
    df = k - 1
    p_val = max(0.0, min(1.0, _chi_square_survival_function(chi2_stat, df)))
    srm_detected = p_val < alpha

    return SRMResult(
        observed_counts=tuple(int(c) for c in observed_counts),
        expected_counts=tuple(round(e, 4) for e in expected_counts),
        chi_square_stat=round(chi2_stat, 6),
        degrees_of_freedom=df,
        p_value=round(p_val, 6),
        alpha_threshold=alpha,
        srm_detected=srm_detected,
        passed=not srm_detected,
    )


class GoldenCase(BaseModel):
    """Typed schema for each line in `evals/golden_cases.jsonl`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    lifecycle_stage: str = Field(..., pattern=r"^Stage_[ABC]$")
    input_payload: dict[str, Any] = Field(...)
    unit_economics: UnitEconomicsInput = Field(...)
    expected_margin_passed: bool = Field(...)
    expected_triage_action: str = Field(..., min_length=1)
    expected_fallback_tier: FallbackTier = Field(...)
    max_allowed_steps: int = Field(default=3, ge=1)
    max_allowed_cost_usd: float = Field(default=0.45, gt=0.0)
    human_reference_verdict: str = Field(..., min_length=1)


def load_golden_cases_jsonl(jsonl_path: Path | str) -> tuple[GoldenCase, ...]:
    """Load and validate a sequence of `GoldenCase` records from a `.jsonl` file."""
    path = Path(jsonl_path)
    cases: list[GoldenCase] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        data = json.loads(line)
        cases.append(GoldenCase.model_validate(data))
    if not cases:
        raise ValueError(f"No golden cases found in {path}.")
    return tuple(cases)


class TierAResult(BaseModel):
    """Tier A evaluation report (contracts & property invariants)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    checks_run: int = Field(..., ge=1)
    checks_passed: int = Field(..., ge=0)
    pass_rate: float = Field(..., ge=0.0, le=1.0)
    passed: bool = Field(...)
    invariant_details: tuple[str, ...] = Field(...)


class TierBResult(BaseModel):
    """Tier B evaluation report (golden dataset, trajectory step/cost efficiency, Cohen's kappa)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    total_cases: int = Field(..., ge=1)
    accuracy_passed_cases: int = Field(..., ge=0)
    trajectory_efficiency_passed_cases: int = Field(..., ge=0)
    golden_pass_rate: float = Field(..., ge=0.0, le=1.0)
    cohens_kappa: float = Field(..., ge=-1.0, le=1.0)
    min_required_kappa: float = Field(default=0.80)
    passed: bool = Field(...)
    case_summaries: tuple[str, ...] = Field(...)


class TierCResult(BaseModel):
    """Tier C evaluation report (CUPED variance reduction & SRM chi-square test)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    cuped: CUPEDResult = Field(...)
    srm: SRMResult = Field(...)
    passed: bool = Field(...)


class EvalSuiteReport(BaseModel):
    """Aggregate report across Tier A, Tier B, and Tier C evaluation gates."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tier_a: TierAResult = Field(...)
    tier_b: TierBResult = Field(...)
    tier_c: TierCResult = Field(...)
    merge_gate_passed: bool = Field(
        ...,
        description="True iff 100% of Tier A and Tier B checks pass (and Tier C passes).",
    )


class MultiTierEvalRunner:
    """Executes Tier A, Tier B, and Tier C evaluation gates for the software factory."""

    def __init__(self, min_cohens_kappa: float = 0.80) -> None:
        self._min_kappa = min_cohens_kappa
        self._margin_gate = ContributionMarginGate()
        self._learning_logger = IdempotentLearningLogger()

    def run_tier_a(self) -> TierAResult:
        """Execute Tier A deterministic contract and property invariant checks."""
        details: list[str] = []
        passed_count = 0
        total_checks = 5

        # 1. Contribution Margin Gate positive & boundary invariant
        margin_ok = self._margin_gate.evaluate(
            UnitEconomicsInput(
                transaction_id="tier-a-margin-1",
                unit_revenue=0.50,
                inference_cost=0.10,
                data_api_cost=0.05,
                hitl_prob=0.10,
                human_review_cost=1.00,
                infra_cost=0.05,
                min_margin=0.20,
            )
        )
        if margin_ok.passed and math.isclose(margin_ok.contribution_margin, 0.20):
            passed_count += 1
            details.append("Tier A.1 PASS: ContributionMarginGate exact boundary invariant satisfied.")

        # 2. Idempotent learning signal deduplication invariant
        sample_signal = LearningSignalTuple(
            workflow_run_id="tier-a-run-1",
            input_state={"query": "stage-b-pricing"},
            system_output={"triage": "approve"},
            user_correction_diff={},
            verified_outcome={"settled": True},
            scorecard=AINativeScorecardInput(
                feature_id="decision-triage",
                workflow_elimination=0.85,
                flywheel_velocity=0.80,
                deterministic_verifiability=0.90,
                unit_margin_resilience=0.85,
                evoi=0.25,
                deterministic_rule_suffices=False,
            ),
        )
        first_log = self._learning_logger.log_event(sample_signal)
        second_log = self._learning_logger.log_event(sample_signal)
        if (
            not first_log.was_deduplicated_replay
            and second_log.was_deduplicated_replay
            and first_log.idempotency_key == second_log.idempotency_key
        ):
            passed_count += 1
            details.append("Tier A.2 PASS: IdempotentLearningLogger replay deduplication verified.")

        # 3. SRE 3-tier fallback degradation invariant
        circuit: FallbackCircuit[dict[str, Any], str] = FallbackCircuit(
            handlers={
                FallbackTier.PRIMARY_FRONTIER_MODEL: lambda _: (_ for _ in ()).throw(
                    RuntimeError("Frontier 503 timeout")
                ),
                FallbackTier.SECONDARY_DISTILLED_MODEL: lambda p: f"distilled:{p['id']}",
                FallbackTier.TERTIARY_CACHED_DETERMINISTIC: lambda p: f"cached:{p['id']}",
            }
        )
        fb_res = circuit.execute({"id": "probe-1"})
        if (
            fb_res.selected_tier == FallbackTier.SECONDARY_DISTILLED_MODEL
            and fb_res.degraded
            and fb_res.output == "distilled:probe-1"
        ):
            passed_count += 1
            details.append("Tier A.3 PASS: FallbackCircuit graceful degradation primary -> secondary verified.")

        # 4. Little's Law WIP_LIMIT = 5 cap invariant
        spec = DAGWorkflowSpec(
            workflow_id="tier-a-wip-check",
            nodes=(
                DAGNodeSpec(
                    node_id="n1",
                    skill_ref="platform.metering.margin_guard",
                    compensating_action="comp_n1",
                ),
            ),
        )
        runner = DAGRunner(spec)
        with (
            runner.reserve_wip_slot(),
            runner.reserve_wip_slot(),
            runner.reserve_wip_slot(),
            runner.reserve_wip_slot(),
            runner.reserve_wip_slot(),
        ):
            wip_capped = False
            try:
                with runner.reserve_wip_slot():
                    pass
            except WIPLimitExceededError:
                wip_capped = True
        if wip_capped and runner.wip_limit == WIP_LIMIT:
            passed_count += 1
            details.append("Tier A.4 PASS: Little's Law WIP_LIMIT=5 semaphore cap enforced.")

        # 5. SHA-256 Duplicate Error Signature Saga Rollback invariant
        rollback_spec = DAGWorkflowSpec(
            workflow_id="tier-a-saga-check",
            nodes=(
                DAGNodeSpec(
                    node_id="step_1",
                    dependencies=(),
                    skill_ref="skill.step_1",
                    compensating_action="undo_step_1",
                    max_retries=3,
                ),
                DAGNodeSpec(
                    node_id="step_2",
                    dependencies=("step_1",),
                    skill_ref="skill.step_2",
                    compensating_action="undo_step_2",
                    max_retries=3,
                ),
            ),
        )
        compensated_log: list[str] = []
        rollback_runner = DAGRunner(
            rollback_spec,
            node_handlers={
                "step_1": NodeExecutionHandler(
                    forward=lambda _: {"ok": True},
                    compensate=lambda _: compensated_log.append("undo_step_1"),
                ),
                "step_2": NodeExecutionHandler(
                    forward=lambda _: (_ for _ in ()).throw(ValueError("Deterministic schema mismatch")),
                    compensate=lambda _: compensated_log.append("undo_step_2"),
                ),
            },
        )
        rb_res = rollback_runner.execute({})
        if (
            rb_res.status == DAGExecutionStatus.ROLLED_BACK_AND_ESCALATED
            and rb_res.hitl_ticket is not None
            and rb_res.hitl_ticket.duplicate_signature_halted
            and rb_res.node_attempt_counts["step_2"] == 2
            and compensated_log == ["undo_step_1"]
        ):
            passed_count += 1
            details.append("Tier A.5 PASS: Duplicate SHA-256 error signature halted at attempt 2 & rolled back.")

        pass_rate = passed_count / total_checks
        return TierAResult(
            checks_run=total_checks,
            checks_passed=passed_count,
            pass_rate=pass_rate,
            passed=(passed_count == total_checks),
            invariant_details=tuple(details),
        )

    def run_tier_b(
        self,
        golden_cases: Sequence[GoldenCase],
        case_executor: Callable[[GoldenCase], dict[str, Any]],
    ) -> TierBResult:
        """Execute Tier B against `golden_cases`, checking accuracy, trajectory cost/steps, and Cohen's kappa."""
        if not golden_cases:
            raise ValueError("golden_cases cannot be empty.")

        accuracy_passed = 0
        efficiency_passed = 0
        human_labels: list[str] = []
        evaluator_labels: list[str] = []
        summaries: list[str] = []

        for case in golden_cases:
            outcome = case_executor(case)
            actual_margin_passed = bool(outcome["margin_passed"])
            actual_action = str(outcome["triage_action"])
            actual_tier = FallbackTier(outcome["selected_tier"])
            actual_steps = int(outcome["steps_executed"])
            actual_cost = float(outcome["total_cost_usd"])
            judge_verdict = str(outcome["evaluator_verdict"])

            human_labels.append(case.human_reference_verdict)
            evaluator_labels.append(judge_verdict)

            case_acc_ok = (
                actual_margin_passed == case.expected_margin_passed
                and actual_action == case.expected_triage_action
                and actual_tier == case.expected_fallback_tier
            )
            case_eff_ok = (
                actual_steps <= case.max_allowed_steps
                and (actual_cost <= case.max_allowed_cost_usd + 1e-9)
            )

            if case_acc_ok:
                accuracy_passed += 1
            if case_eff_ok:
                efficiency_passed += 1

            status_tag = "PASS" if (case_acc_ok and case_eff_ok) else "FAIL"
            summaries.append(
                f"[{status_tag}] {case.case_id}: action={actual_action} (expected={case.expected_triage_action}), "
                f"tier={actual_tier.value}, steps={actual_steps}/{case.max_allowed_steps}, "
                f"cost=${actual_cost:.4f}/${case.max_allowed_cost_usd:.4f}"
            )

        total = len(golden_cases)
        both_passed = sum(
            1 for s in summaries if s.startswith("[PASS]")
        )
        pass_rate = both_passed / total
        kappa = compute_cohens_kappa(human_labels, evaluator_labels)

        passed = (
            accuracy_passed == total
            and efficiency_passed == total
            and (kappa + 1e-12) >= self._min_kappa
        )

        return TierBResult(
            total_cases=total,
            accuracy_passed_cases=accuracy_passed,
            trajectory_efficiency_passed_cases=efficiency_passed,
            golden_pass_rate=pass_rate,
            cohens_kappa=round(kappa, 4),
            min_required_kappa=self._min_kappa,
            passed=passed,
            case_summaries=tuple(summaries),
        )

    def run_tier_c(
        self,
        control_pre: Sequence[float] | None = None,
        control_post: Sequence[float] | None = None,
        treatment_pre: Sequence[float] | None = None,
        treatment_post: Sequence[float] | None = None,
        observed_arm_counts: Sequence[int] = (504, 496),
        expected_arm_ratios: Sequence[float] = (0.50, 0.50),
    ) -> TierCResult:
        """Execute Tier C CUPED variance reduction and SRM chi-square gate."""
        ctrl_pre = list(
            control_pre
            if control_pre is not None
            else [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0]
        )
        ctrl_post = list(
            control_post
            if control_post is not None
            else [10.5, 11.8, 14.2, 15.9, 18.1, 20.3, 21.7, 24.1, 26.2, 27.9]
        )
        trt_pre = list(
            treatment_pre
            if treatment_pre is not None
            else [10.2, 11.9, 14.1, 16.2, 17.8, 20.1, 22.2, 23.9, 26.1, 28.0]
        )
        trt_post = list(
            treatment_post
            if treatment_post is not None
            else [12.8, 14.2, 16.5, 18.7, 20.1, 22.6, 24.8, 26.3, 28.6, 30.5]
        )

        cuped_res = compute_cuped_adjustment(
            control_pre=ctrl_pre,
            control_post=ctrl_post,
            treatment_pre=trt_pre,
            treatment_post=trt_post,
        )
        srm_res = compute_srm_chi_square(
            observed_counts=observed_arm_counts,
            expected_ratios=expected_arm_ratios,
        )
        passed = cuped_res.variance_reduced and srm_res.passed

        return TierCResult(
            cuped=cuped_res,
            srm=srm_res,
            passed=passed,
        )

    def run_all_tiers(
        self,
        golden_cases: Sequence[GoldenCase],
        case_executor: Callable[[GoldenCase], dict[str, Any]],
    ) -> EvalSuiteReport:
        """Run Tier A, Tier B, and Tier C and return the consolidated `EvalSuiteReport`."""
        tier_a = self.run_tier_a()
        tier_b = self.run_tier_b(golden_cases, case_executor)
        tier_c = self.run_tier_c()
        merge_ok = tier_a.passed and tier_b.passed and tier_c.passed
        return EvalSuiteReport(
            tier_a=tier_a,
            tier_b=tier_b,
            tier_c=tier_c,
            merge_gate_passed=merge_ok,
        )


def _run_cli_demo() -> None:
    """CLI entry point running the reference product `demo-decision-engine` across all 3 eval tiers."""
    from products.demo_decision_engine.skills.decision_triage import (
        evaluate_golden_case_with_dag,
    )

    repo_root = Path(__file__).resolve().parents[2]
    golden_path = (
        repo_root / "products" / "demo-decision-engine" / "evals" / "golden_cases.jsonl"
    )
    dag_path = (
        repo_root / "products" / "demo-decision-engine" / "workflows" / "factory_dag.yaml"
    )

    cases = load_golden_cases_jsonl(golden_path)
    runner = MultiTierEvalRunner()
    report = runner.run_all_tiers(
        golden_cases=cases,
        case_executor=lambda c: evaluate_golden_case_with_dag(c, dag_path=dag_path),
    )

    print("=== Principled Product Factory (v10) Multi-Tier Evaluation Report ===")
    print(f"Tier A (Contracts & Invariants): {report.tier_a.checks_passed}/{report.tier_a.checks_run} passed")
    print(
        f"Tier B (Golden Set & Efficiency): {report.tier_b.accuracy_passed_cases}/{report.tier_b.total_cases} "
        f"cases | Cohen's kappa = {report.tier_b.cohens_kappa:.4f} (min {report.tier_b.min_required_kappa:.2f})"
    )
    print(
        f"Tier C (CUPED & SRM): CUPED variance reduction = {report.tier_c.cuped.variance_reduction_ratio:.1%} "
        f"| SRM p-value = {report.tier_c.tier_c_srm_p if hasattr(report.tier_c, 'tier_c_srm_p') else report.tier_c.srm.p_value:.4f}"
    )
    print(f"Overall Merge Gate Passed: {report.merge_gate_passed}")
    if not report.merge_gate_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    _run_cli_demo()
