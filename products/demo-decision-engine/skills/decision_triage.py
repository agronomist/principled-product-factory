"""Reference Product Domain Skill: Decision Triage Engine (`products/demo-decision-engine/skills/decision_triage.py`).

Implements the domain skill for `demo-decision-engine` using:
1. Step 0 Lifecycle Stage & Portfolio Bayesian Kill-Switch Routing (`Stage_A`, `Stage_B`, `Stage_C`).
2. Strict Liskov Preconditions (`validate_preconditions`) and Postconditions (`validate_postconditions`)
   and Parnas information hiding (`frozen=True`, `extra="forbid"` Pydantic v2 models).
3. 3-Tier SRE Fallback Chain (`primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`).
4. Contribution Margin Gate integration (`platform.metering.margin_guard`).
5. Passive Zero-Friction Correction-Diff Emission (`platform.telemetry.learning_signal`).
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from platform.evals.runner import GoldenCase
from platform.metering.margin_guard import (
    ContributionMarginGate,
    MarginDecision,
    MarginEvaluationResult,
    UnitEconomicsInput,
)
from platform.orchestrator.dag_runner import (
    BellmanStateVector,
    DAGExecutionResult,
    DAGExecutionStatus,
    DAGRunner,
    NodeExecutionHandler,
    load_dag_workflow_yaml,
)
from platform.sre.fallback_circuit import (
    CircuitBreakerConfig,
    FallbackCircuit,
    FallbackTier,
)
from platform.telemetry.learning_signal import (
    AINativeScorecardInput,
    IdempotentLearningLogger,
    LearningSignalRecord,
    LearningSignalTuple,
    compute_correction_diff,
)


class LifecycleStage(str, Enum):
    """Step 0 Lifecycle Stage classifications."""

    STAGE_A = "Stage_A"
    STAGE_B = "Stage_B"
    STAGE_C = "Stage_C"


class TriageAction(str, Enum):
    """Canonical decision triage actions emitted by `DecisionTriageSkill`."""

    FAST_TRACK_EXPERIMENT = "fast_track_experiment"
    SCALE_WITH_GUARDRAILS = "scale_with_guardrails"
    DISTILL_AND_PROCEED = "distill_and_proceed"
    BLOCK_AI_THEATER = "block_ai_theater"
    SUNSET_KILL_SWITCH = "sunset_kill_switch"
    BLOCK_MARGIN_GATE = "block_margin_gate"


class DecisionTriageInput(BaseModel):
    """Immutable Liskov precondition schema for `DecisionTriageSkill`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    proposal_id: str = Field(..., min_length=1)
    lifecycle_stage: LifecycleStage = Field(default=LifecycleStage.STAGE_B)
    prior_success_prob: float = Field(..., gt=0.0, lt=1.0)
    likelihood_ratio: float = Field(..., gt=0.0)
    kill_threshold_posterior: float = Field(default=0.25, gt=0.0, lt=1.0)
    evoi_usd: float = Field(...)
    deterministic_rule_suffices: bool = Field(default=False)
    complexity: float = Field(default=0.40, ge=0.0, le=1.0)
    risk: float = Field(default=0.30, ge=0.0, le=1.0)
    simulate_primary_failure: bool = Field(default=False)
    simulate_secondary_failure: bool = Field(default=False)
    user_override_action: str | None = Field(
        default=None,
        description="Optional post-hoc user edit to demonstrate passive correction-diff emission.",
    )


class DecisionTriageOutput(BaseModel):
    """Immutable Liskov postcondition schema returned by `DecisionTriageSkill`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    proposal_id: str = Field(..., min_length=1)
    lifecycle_stage: LifecycleStage = Field(...)
    posterior_success_prob: float = Field(..., gt=0.0, lt=1.0)
    kill_switch_tripped: bool = Field(...)
    ai_theater_blocked: bool = Field(...)
    margin_passed: bool = Field(...)
    triage_action: TriageAction = Field(...)
    selected_tier: FallbackTier = Field(...)
    degraded_mode: bool = Field(...)
    total_cost_usd: float = Field(..., ge=0.0)
    contribution_margin_usd: float = Field(...)
    learning_signal_key: str = Field(..., min_length=64, max_length=64)
    user_correction_diff: dict[str, Any] = Field(default_factory=dict)
    metaphor_rationale: str = Field(..., min_length=1)


class AbstractDomainSkill(ABC):
    """Liskov base contract for all domain skills in `products/*/skills/`."""

    @abstractmethod
    def validate_preconditions(
        self,
        triage_input: DecisionTriageInput,
        economics: UnitEconomicsInput,
    ) -> None:
        """Liskov precondition check: subtypes must not strengthen preconditions."""

    @abstractmethod
    def validate_postconditions(
        self,
        triage_input: DecisionTriageInput,
        economics: UnitEconomicsInput,
        output: DecisionTriageOutput,
    ) -> None:
        """Liskov postcondition check: subtypes must not weaken postconditions."""


def compute_bayesian_posterior(prior_prob: float, likelihood_ratio: float) -> float:
    r"""Update prior probability $P(H)$ with likelihood ratio $\Lambda = \frac{P(E \mid H)}{P(E \mid \neg H)}$:
    $$\text{Odds}_{\text{post}} = \Lambda \cdot \frac{P(H)}{1 - P(H)}, \quad P(H \mid E) = \frac{\text{Odds}_{\text{post}}}{1 + \text{Odds}_{\text{post}}}$$
    """
    if not (0.0 < prior_prob < 1.0):
        raise ValueError("prior_prob must be in (0.0, 1.0).")
    if likelihood_ratio <= 0.0:
        raise ValueError("likelihood_ratio must be > 0.0.")
    prior_odds = prior_prob / (1.0 - prior_prob)
    post_odds = prior_odds * likelihood_ratio
    posterior = post_odds / (1.0 + post_odds)
    return max(1e-9, min(1.0 - 1e-9, posterior))


class DecisionTriageSkill(AbstractDomainSkill):
    """Concrete Liskov-verified domain skill implementing Step 0 triage, Bayesian kill-switches,
    Contribution Margin Gate checks, 3-tier SRE fallback routing, and passive correction-diff telemetry.
    """

    def __init__(
        self,
        margin_gate: ContributionMarginGate | None = None,
        learning_logger: IdempotentLearningLogger | None = None,
    ) -> None:
        self._margin_gate = margin_gate or ContributionMarginGate()
        self._logger = learning_logger or IdempotentLearningLogger()

    @property
    def learning_logger(self) -> IdempotentLearningLogger:
        return self._logger

    def validate_preconditions(
        self,
        triage_input: DecisionTriageInput,
        economics: UnitEconomicsInput,
    ) -> None:
        if not (0.0 < triage_input.prior_success_prob < 1.0):
            raise ValueError("Precondition failed: prior_success_prob must be in (0, 1).")
        if triage_input.likelihood_ratio <= 0.0:
            raise ValueError("Precondition failed: likelihood_ratio must be > 0.")
        self._margin_gate.validate_preconditions(economics)

    def _build_sre_circuit(
        self,
    ) -> FallbackCircuit[tuple[DecisionTriageInput, MarginEvaluationResult], TriageAction]:
        """Construct the 3-tier SRE fallback circuit for decision triage."""

        def _primary_frontier_handler(
            ctx: tuple[DecisionTriageInput, MarginEvaluationResult]
        ) -> TriageAction:
            inp, margin_res = ctx
            if inp.simulate_primary_failure:
                raise RuntimeError("Primary frontier model HTTP 503 / Shewhart 3-sigma latency spike")
            return self._deterministic_core_decision(inp, margin_res)

        def _secondary_distilled_handler(
            ctx: tuple[DecisionTriageInput, MarginEvaluationResult]
        ) -> TriageAction:
            inp, margin_res = ctx
            if inp.simulate_secondary_failure:
                raise RuntimeError("Secondary distilled model capacity timeout")
            return self._deterministic_core_decision(inp, margin_res)

        def _tertiary_cached_handler(
            ctx: tuple[DecisionTriageInput, MarginEvaluationResult]
        ) -> TriageAction:
            inp, margin_res = ctx
            return self._deterministic_core_decision(inp, margin_res)

        return FallbackCircuit(
            handlers={
                FallbackTier.PRIMARY_FRONTIER_MODEL: _primary_frontier_handler,
                FallbackTier.SECONDARY_DISTILLED_MODEL: _secondary_distilled_handler,
                FallbackTier.TERTIARY_CACHED_DETERMINISTIC: _tertiary_cached_handler,
            },
            config=CircuitBreakerConfig(failure_threshold=2, recovery_timeout_seconds=30.0),
        )

    @staticmethod
    def _deterministic_core_decision(
        inp: DecisionTriageInput,
        margin_res: MarginEvaluationResult,
    ) -> TriageAction:
        posterior = compute_bayesian_posterior(inp.prior_success_prob, inp.likelihood_ratio)

        # 1. Bayesian Kill-Switch check (George Costanza exit / 60th-minute striker substitution)
        if posterior < inp.kill_threshold_posterior:
            return TriageAction.SUNSET_KILL_SWITCH

        # 2. AI Bolt-On Theater filter (The Urban Sombrero / step-overs in your own penalty box)
        if inp.evoi_usd <= 0.0 or inp.deterministic_rule_suffices:
            return TriageAction.BLOCK_AI_THEATER

        # 3. Contribution Margin Gate check
        if not margin_res.passed:
            if margin_res.decision == MarginDecision.DOWNGRADE_TO_DISTILLED:
                return TriageAction.DISTILL_AND_PROCEED
            return TriageAction.BLOCK_MARGIN_GATE

        # 4. Lifecycle Stage routing
        if inp.lifecycle_stage == LifecycleStage.STAGE_A:
            return TriageAction.FAST_TRACK_EXPERIMENT
        return TriageAction.SCALE_WITH_GUARDRAILS

    def execute(
        self,
        triage_input: DecisionTriageInput,
        economics: UnitEconomicsInput,
    ) -> DecisionTriageOutput:
        """Run decision triage with Liskov contract checks, SRE fallback routing, and passive telemetry."""
        self.validate_preconditions(triage_input, economics)

        margin_res = self._margin_gate.evaluate(economics)
        posterior = compute_bayesian_posterior(
            triage_input.prior_success_prob, triage_input.likelihood_ratio
        )
        kill_tripped = posterior < triage_input.kill_threshold_posterior
        ai_theater = triage_input.evoi_usd <= 0.0 or triage_input.deterministic_rule_suffices

        # Determine starting SRE tier: if margin gate recommends downgrade_to_distilled, start at secondary
        start_tier = (
            FallbackTier.SECONDARY_DISTILLED_MODEL
            if (not margin_res.passed and margin_res.decision == MarginDecision.DOWNGRADE_TO_DISTILLED)
            else FallbackTier.PRIMARY_FRONTIER_MODEL
        )

        circuit = self._build_sre_circuit()
        sre_res = circuit.execute((triage_input, margin_res), start_tier=start_tier)
        action = sre_res.output

        # Compute effective inference cost based on the tier that actually served the request
        tier_cost_multiplier = {
            FallbackTier.PRIMARY_FRONTIER_MODEL: 1.0,
            FallbackTier.SECONDARY_DISTILLED_MODEL: 0.20,
            FallbackTier.TERTIARY_CACHED_DETERMINISTIC: 0.02,
        }[sre_res.selected_tier]

        effective_inference_cost = economics.inference_cost * tier_cost_multiplier
        effective_total_cost = (
            effective_inference_cost
            + economics.data_api_cost
            + (economics.hitl_prob * economics.human_review_cost)
            + economics.infra_cost
        )
        effective_margin = economics.unit_revenue - effective_total_cost

        # Emit zero-friction learning signal tuple with passive correction diff
        sys_out_dict = {
            "triage_action": action.value,
            "selected_tier": sre_res.selected_tier.value,
            "posterior_success_prob": round(posterior, 6),
        }
        user_final_dict = (
            {**sys_out_dict, "triage_action": triage_input.user_override_action}
            if triage_input.user_override_action is not None
            else None
        )
        correction_diff = compute_correction_diff(sys_out_dict, user_final_dict)

        learning_tuple = LearningSignalTuple(
            product_id="demo-decision-engine",
            workflow_run_id=triage_input.proposal_id,
            input_state=triage_input.model_dump(mode="json"),
            system_output=sys_out_dict,
            user_correction_diff=correction_diff,
            verified_outcome={
                "margin_passed": margin_res.passed,
                "effective_margin_usd": round(effective_margin, 6),
                "kill_switch_tripped": kill_tripped,
            },
            scorecard=AINativeScorecardInput(
                feature_id=triage_input.proposal_id,
                workflow_elimination=0.85,
                flywheel_velocity=0.90,
                deterministic_verifiability=0.95,
                unit_margin_resilience=0.80 if margin_res.passed else 0.65,
                evoi=triage_input.evoi_usd,
                deterministic_rule_suffices=triage_input.deterministic_rule_suffices,
            ),
        )
        record: LearningSignalRecord = self._logger.log_event(learning_tuple)

        output = DecisionTriageOutput(
            proposal_id=triage_input.proposal_id,
            lifecycle_stage=triage_input.lifecycle_stage,
            posterior_success_prob=round(posterior, 6),
            kill_switch_tripped=kill_tripped,
            ai_theater_blocked=ai_theater,
            margin_passed=margin_res.passed,
            triage_action=action,
            selected_tier=sre_res.selected_tier,
            degraded_mode=sre_res.degraded,
            total_cost_usd=round(effective_total_cost, 6),
            contribution_margin_usd=round(effective_margin, 6),
            learning_signal_key=record.idempotency_key,
            user_correction_diff=correction_diff,
            metaphor_rationale=f"{sre_res.metaphor_summary} | {margin_res.explanation}",
        )
        self.validate_postconditions(triage_input, economics, output)
        return output

    def validate_postconditions(
        self,
        triage_input: DecisionTriageInput,
        economics: UnitEconomicsInput,
        output: DecisionTriageOutput,
    ) -> None:
        expected_post = compute_bayesian_posterior(
            triage_input.prior_success_prob, triage_input.likelihood_ratio
        )
        if not math.isclose(output.posterior_success_prob, expected_post, abs_tol=1e-5):
            raise RuntimeError("Postcondition breach: posterior_success_prob mismatch.")
        if output.kill_switch_tripped and output.triage_action != TriageAction.SUNSET_KILL_SWITCH:
            raise RuntimeError(
                "Postcondition breach: tripped Bayesian kill-switch must emit SUNSET_KILL_SWITCH."
            )
        if (
            not output.kill_switch_tripped
            and output.ai_theater_blocked
            and output.triage_action != TriageAction.BLOCK_AI_THEATER
        ):
            raise RuntimeError(
                "Postcondition breach: AI bolt-on theater must emit BLOCK_AI_THEATER."
            )
        if (output.selected_tier != FallbackTier.PRIMARY_FRONTIER_MODEL) != output.degraded_mode:
            raise RuntimeError(
                "Postcondition breach: degraded_mode boolean inconsistent with selected_tier."
            )


def evaluate_golden_case_with_dag(
    case: GoldenCase,
    dag_path: Path | str | None = None,
) -> dict[str, Any]:
    """Execute a `GoldenCase` end-to-end through `factory_dag.yaml` and `DAGRunner`."""
    if dag_path is None:
        dag_path = (
            Path(__file__).resolve().parents[1] / "workflows" / "factory_dag.yaml"
        )
    workflow_spec = load_dag_workflow_yaml(dag_path)
    margin_gate = ContributionMarginGate()
    logger = IdempotentLearningLogger()
    skill = DecisionTriageSkill(margin_gate=margin_gate, learning_logger=logger)

    triage_input = DecisionTriageInput.model_validate(
        {
            **case.input_payload,
            "proposal_id": case.case_id,
            "lifecycle_stage": case.lifecycle_stage,
        }
    )

    def _node_validate_margin(ctx: dict[str, Any]) -> dict[str, Any]:
        res = margin_gate.evaluate(ctx["economics"])
        return {"margin_result": res}

    def _node_execute_triage(ctx: dict[str, Any]) -> dict[str, Any]:
        out = skill.execute(ctx["triage_input"], ctx["economics"])
        return {"triage_output": out}

    def _node_emit_signal(ctx: dict[str, Any]) -> dict[str, Any]:
        triage_out: DecisionTriageOutput = ctx["execute_decision_triage"]["triage_output"]
        return {
            "learning_signal_key": triage_out.learning_signal_key,
            "unique_events": logger.total_unique_events,
        }

    runner = DAGRunner(
        workflow_spec=workflow_spec,
        node_handlers={
            "validate_margin_gate": NodeExecutionHandler(
                forward=_node_validate_margin,
                compensate=lambda ctx: ctx.update({"margin_released": True}),
            ),
            "execute_decision_triage": NodeExecutionHandler(
                forward=_node_execute_triage,
                compensate=lambda ctx: ctx.update({"triage_reverted": True}),
            ),
            "emit_learning_signal": NodeExecutionHandler(
                forward=_node_emit_signal,
                compensate=lambda ctx: ctx.update({"signal_voided": True}),
            ),
        },
    )

    margin_preview = margin_gate.evaluate(case.unit_economics)
    bellman_state = BellmanStateVector(
        complexity=triage_input.complexity,
        risk=triage_input.risk,
        margin_headroom_usd=margin_preview.margin_headroom,
        evoi=max(0.0, triage_input.evoi_usd),
    )

    dag_result: DAGExecutionResult = runner.execute(
        initial_context={
            "triage_input": triage_input,
            "economics": case.unit_economics,
        },
        bellman_state=bellman_state,
    )

    if dag_result.status != DAGExecutionStatus.COMPLETED:
        raise RuntimeError(f"DAG execution failed on golden case {case.case_id}")

    triage_output: DecisionTriageOutput = dag_result.node_outputs["execute_decision_triage"][
        "triage_output"
    ]

    return {
        "case_id": case.case_id,
        "margin_passed": triage_output.margin_passed,
        "triage_action": triage_output.triage_action.value,
        "selected_tier": triage_output.selected_tier.value,
        "steps_executed": len(dag_result.completed_nodes),
        "total_cost_usd": triage_output.total_cost_usd,
        "evaluator_verdict": triage_output.triage_action.value,
        "bellman_route": dag_result.route_decision.selected_route.value,
    }
