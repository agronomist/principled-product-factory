"""Contribution Margin Gate, Cohort P&L / CAC Payback Validator, and 6-Month Re-Pricing Retro-Audit.

Implements the financial and unit-economics invariants of `principled-product-builder-v10`:
1. Contribution Margin Gate:
   `unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`
2. Cohort P&L & CAC Payback Validator:
   Enforces CAC Payback <= max_payback_months (12.0), LTV/CAC >= min_ltv_to_cac (3.0),
   and Net Dollar Retention checks.
3. 6-Month Re-Pricing Retro-Audit (Ramanujam *Monetizing Innovation*):
   Flags margin leakage or HITL escalation drift comparing forecast vs. realized cohort economics.

Design Contracts:
- Liskov Substitution Principle (LSP): Base `EconomicGateContract` defines strict
  `validate_preconditions` and `validate_postconditions` preserved by all concrete gates.
- Parnas Information Hiding: Internal threshold tolerances and ledger state are encapsulated
  behind immutable (`frozen=True`, `extra="forbid"`) Pydantic v2 data structures.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class MarginViolationError(ValueError):
    """Raised when a unit transaction or cohort fails a mandatory financial gate."""


class MarginDecision(str, Enum):
    """Deterministic decision emitted by the Contribution Margin Gate."""

    APPROVED = "approved"
    DOWNGRADE_TO_DISTILLED = "downgrade_to_distilled"
    BLOCKED_NEGATIVE_MARGIN = "blocked_negative_margin"
    BLOCKED_BELOW_MIN_MARGIN = "blocked_below_min_margin"


class UnitEconomicsInput(BaseModel):
    """Immutable input contract for evaluating a single unit transaction's contribution margin."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transaction_id: str = Field(
        default="tx-default",
        min_length=1,
        description="Unique transaction or workflow execution identifier.",
    )
    unit_revenue: float = Field(
        ...,
        gt=0.0,
        description="Gross revenue attributable to this unit execution in USD.",
    )
    inference_cost: float = Field(
        ...,
        ge=0.0,
        description="Model token / compute inference cost in USD.",
    )
    data_api_cost: float = Field(
        ...,
        ge=0.0,
        description="Third-party retrieval, search, or data enrichment API cost in USD.",
    )
    hitl_prob: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability [0.0, 1.0] that this execution requires human-in-the-loop review.",
    )
    human_review_cost: float = Field(
        ...,
        ge=0.0,
        description="Fully loaded human operator cost per escalated review in USD.",
    )
    infra_cost: float = Field(
        ...,
        ge=0.0,
        description="Allocated database, network, and orchestration infrastructure cost in USD.",
    )
    min_margin: float = Field(
        default=0.05,
        description="Minimum required absolute unit contribution margin in USD.",
    )

    @model_validator(mode="after")
    def _check_finite_numbers(self) -> UnitEconomicsInput:
        for field_name in (
            "unit_revenue",
            "inference_cost",
            "data_api_cost",
            "hitl_prob",
            "human_review_cost",
            "infra_cost",
            "min_margin",
        ):
            val = getattr(self, field_name)
            if not math.isfinite(val):
                raise ValueError(f"Field '{field_name}' must be a finite float, got {val!r}.")
        return self


class MarginEvaluationResult(BaseModel):
    """Immutable postcondition contract produced by `ContributionMarginGate`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transaction_id: str = Field(..., min_length=1)
    unit_revenue: float = Field(..., gt=0.0)
    expected_hitl_cost: float = Field(..., ge=0.0)
    total_variable_cost: float = Field(..., ge=0.0)
    contribution_margin: float = Field(...)
    margin_ratio: float = Field(...)
    min_margin_required: float = Field(...)
    margin_headroom: float = Field(...)
    passed: bool = Field(...)
    decision: MarginDecision = Field(...)
    explanation: str = Field(..., min_length=1)


class EconomicGateContract(ABC, Generic[TInput, TOutput]):
    """Abstract Liskov contract for all economic and financial gates in `platform/metering`.

    Subtypes must accept at least any valid `TInput` satisfying `validate_preconditions`
    and return a `TOutput` satisfying `validate_postconditions`.
    """

    @abstractmethod
    def validate_preconditions(self, payload: TInput) -> None:
        """Verify Liskov preconditions before executing the economic calculation."""

    @abstractmethod
    def validate_postconditions(self, payload: TInput, result: TOutput) -> None:
        """Verify Liskov postconditions and algebraic invariants before returning."""

    @abstractmethod
    def _compute(self, payload: TInput) -> TOutput:
        """Internal Parnas-encapsulated evaluation logic."""

    def evaluate(self, payload: TInput) -> TOutput:
        """Template method enforcing Liskov preconditions and postconditions around `_compute`."""
        self.validate_preconditions(payload)
        result = self._compute(payload)
        self.validate_postconditions(payload, result)
        return result


class ContributionMarginGate(EconomicGateContract[UnitEconomicsInput, MarginEvaluationResult]):
    """Enforces the canonical Contribution Margin Gate:

    `unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`

    Encapsulates fallback cost-estimation rules behind a strict Parnas boundary so callers
    cannot tamper with the accounting formula.
    """

    def __init__(
        self,
        default_min_margin: float = 0.05,
        distilled_inference_discount_factor: float = 0.20,
    ) -> None:
        if not math.isfinite(default_min_margin):
            raise ValueError("default_min_margin must be finite.")
        if not (0.0 < distilled_inference_discount_factor <= 1.0):
            raise ValueError("distilled_inference_discount_factor must be in (0.0, 1.0].")
        self._default_min_margin = default_min_margin
        self._distilled_discount = distilled_inference_discount_factor

    def validate_preconditions(self, payload: UnitEconomicsInput) -> None:
        if payload.unit_revenue <= 0.0:
            raise MarginViolationError("Precondition failed: unit_revenue must be > 0.")
        if not (0.0 <= payload.hitl_prob <= 1.0):
            raise MarginViolationError("Precondition failed: hitl_prob must be within [0.0, 1.0].")
        if any(
            c < 0.0
            for c in (
                payload.inference_cost,
                payload.data_api_cost,
                payload.human_review_cost,
                payload.infra_cost,
            )
        ):
            raise MarginViolationError("Precondition failed: cost components cannot be negative.")

    def _compute(self, payload: UnitEconomicsInput) -> MarginEvaluationResult:
        expected_hitl_cost = payload.hitl_prob * payload.human_review_cost
        total_variable_cost = (
            payload.inference_cost
            + payload.data_api_cost
            + expected_hitl_cost
            + payload.infra_cost
        )
        contribution_margin = payload.unit_revenue - total_variable_cost
        margin_ratio = contribution_margin / payload.unit_revenue
        # Allow a tiny floating-point tolerance (1e-12) for exact boundary equality
        passed = (contribution_margin + 1e-12) >= payload.min_margin
        margin_headroom = contribution_margin - payload.min_margin

        if passed:
            decision = MarginDecision.APPROVED
            explanation = (
                f"Approved: contribution_margin=${contribution_margin:.4f} "
                f"(ratio={margin_ratio:.1%}) >= min_margin=${payload.min_margin:.4f}."
            )
        else:
            # Check whether switching from primary frontier inference to secondary distilled model rescues margin
            distilled_cost = (
                payload.inference_cost * self._distilled_discount
                + payload.data_api_cost
                + expected_hitl_cost
                + payload.infra_cost
            )
            distilled_margin = payload.unit_revenue - distilled_cost
            if (distilled_margin + 1e-12) >= payload.min_margin:
                decision = MarginDecision.DOWNGRADE_TO_DISTILLED
                explanation = (
                    f"Margin gate failed on frontier tier (${contribution_margin:.4f} < ${payload.min_margin:.4f}), "
                    f"but secondary_distilled_model restores margin to ${distilled_margin:.4f}. "
                    "Subbing off the expensive playmaker for the box-to-box midfielder."
                )
            elif contribution_margin < 0.0:
                decision = MarginDecision.BLOCKED_NEGATIVE_MARGIN
                explanation = (
                    f"Blocked (Kramer/Newman Michigan bottle-run alert): negative unit contribution margin "
                    f"${contribution_margin:.4f} on revenue=${payload.unit_revenue:.4f} and COGS=${total_variable_cost:.4f}."
                )
            else:
                decision = MarginDecision.BLOCKED_BELOW_MIN_MARGIN
                explanation = (
                    f"Blocked: unit contribution margin ${contribution_margin:.4f} is below required "
                    f"min_margin=${payload.min_margin:.4f} even after distilled model substitution."
                )

        return MarginEvaluationResult(
            transaction_id=payload.transaction_id,
            unit_revenue=payload.unit_revenue,
            expected_hitl_cost=expected_hitl_cost,
            total_variable_cost=total_variable_cost,
            contribution_margin=contribution_margin,
            margin_ratio=margin_ratio,
            min_margin_required=payload.min_margin,
            margin_headroom=margin_headroom,
            passed=passed,
            decision=decision,
            explanation=explanation,
        )

    def validate_postconditions(
        self, payload: UnitEconomicsInput, result: MarginEvaluationResult
    ) -> None:
        recomputed_cogs = (
            payload.inference_cost
            + payload.data_api_cost
            + (payload.hitl_prob * payload.human_review_cost)
            + payload.infra_cost
        )
        recomputed_margin = payload.unit_revenue - recomputed_cogs
        if not math.isclose(result.total_variable_cost, recomputed_cogs, rel_tol=1e-9, abs_tol=1e-12):
            raise MarginViolationError("Postcondition breach: total_variable_cost mismatch.")
        if not math.isclose(result.contribution_margin, recomputed_margin, rel_tol=1e-9, abs_tol=1e-12):
            raise MarginViolationError("Postcondition breach: contribution_margin mismatch.")
        expected_pass = (recomputed_margin + 1e-12) >= payload.min_margin
        if result.passed != expected_pass:
            raise MarginViolationError("Postcondition breach: passed boolean contradicts formula.")
        if result.passed and result.decision != MarginDecision.APPROVED:
            raise MarginViolationError("Postcondition breach: passing gate must emit APPROVED.")
        if not result.passed and result.decision == MarginDecision.APPROVED:
            raise MarginViolationError("Postcondition breach: failing gate must never emit APPROVED.")

    def check_or_raise(self, payload: UnitEconomicsInput) -> MarginEvaluationResult:
        """Evaluate the Contribution Margin Gate and raise `MarginViolationError` if not passed."""
        result = self.evaluate(payload)
        if not result.passed:
            raise MarginViolationError(result.explanation)
        return result


class CohortPnLInput(BaseModel):
    """Immutable input contract for Cohort P&L, LTV/CAC, and CAC Payback validation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    cohort_id: str = Field(..., min_length=1)
    active_customers: int = Field(..., gt=0)
    arpa_monthly_usd: float = Field(
        ...,
        gt=0.0,
        description="Average Revenue Per Account per month in USD.",
    )
    monthly_variable_cogs_per_account_usd: float = Field(
        ...,
        ge=0.0,
        description="Average monthly inference + data + HITL + infra COGS per account in USD.",
    )
    cac_per_customer_usd: float = Field(
        ...,
        ge=0.0,
        description="Fully loaded Sales & Marketing Customer Acquisition Cost per customer in USD.",
    )
    monthly_gross_churn_rate: float = Field(
        ...,
        gt=0.0,
        le=1.0,
        description="Monthly gross revenue churn rate in (0.0, 1.0].",
    )
    monthly_expansion_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Monthly expansion revenue rate from existing cohort customers.",
    )
    max_payback_months: float = Field(
        default=12.0,
        gt=0.0,
        description="Maximum allowed CAC payback period in months (Stage B/C standard: 12.0).",
    )
    min_ltv_to_cac: float = Field(
        default=3.0,
        gt=0.0,
        description="Minimum required LTV-to-CAC ratio (Stage B/C standard: 3.0).",
    )
    min_gross_margin_ratio: float = Field(
        default=0.65,
        gt=0.0,
        lt=1.0,
        description="Minimum required cohort gross margin ratio (default 65%).",
    )


class CohortPnLResult(BaseModel):
    """Immutable output contract from `CohortPnLValidator`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    cohort_id: str = Field(..., min_length=1)
    cohort_mrr_usd: float = Field(..., gt=0.0)
    unit_gross_profit_monthly_usd: float = Field(...)
    cohort_gross_profit_monthly_usd: float = Field(...)
    gross_margin_ratio: float = Field(...)
    cac_payback_months: float = Field(..., ge=0.0)
    ltv_per_customer_usd: float = Field(...)
    ltv_to_cac_ratio: float = Field(..., ge=0.0)
    annualized_ndr: float = Field(..., ge=0.0)
    kill_switch_triggered: bool = Field(...)
    passed: bool = Field(...)
    violations: tuple[str, ...] = Field(default_factory=tuple)


class CohortPnLValidator(EconomicGateContract[CohortPnLInput, CohortPnLResult]):
    """Validates Cohort P&L invariants, CAC Payback Period, LTV/CAC, and Net Dollar Retention.

    Implements the Bayesian/Portfolio Kill-Switch check when cohort contribution margin is negative
    or payback exceeds the capital allocation ceiling.
    """

    def validate_preconditions(self, payload: CohortPnLInput) -> None:
        if payload.active_customers <= 0:
            raise MarginViolationError("Precondition failed: active_customers must be > 0.")
        if payload.arpa_monthly_usd <= 0.0:
            raise MarginViolationError("Precondition failed: arpa_monthly_usd must be > 0.")

    def _compute(self, payload: CohortPnLInput) -> CohortPnLResult:
        cohort_mrr = payload.active_customers * payload.arpa_monthly_usd
        unit_gross_profit = payload.arpa_monthly_usd - payload.monthly_variable_cogs_per_account_usd
        cohort_gross_profit = payload.active_customers * unit_gross_profit
        gross_margin_ratio = unit_gross_profit / payload.arpa_monthly_usd

        violations: list[str] = []

        if unit_gross_profit <= 0.0:
            cac_payback_months = float("inf")
            ltv_per_customer = 0.0
            ltv_to_cac = 0.0
            violations.append(
                f"Negative or zero monthly unit gross profit (${unit_gross_profit:.2f}/acct)."
            )
        else:
            if payload.cac_per_customer_usd == 0.0:
                cac_payback_months = 0.0
            else:
                cac_payback_months = payload.cac_per_customer_usd / unit_gross_profit

            effective_churn = max(payload.monthly_gross_churn_rate, 0.005)
            ltv_per_customer = unit_gross_profit / effective_churn
            if payload.cac_per_customer_usd == 0.0:
                ltv_to_cac = float("inf")
            else:
                ltv_to_cac = ltv_per_customer / payload.cac_per_customer_usd

        if (gross_margin_ratio + 1e-12) < payload.min_gross_margin_ratio:
            violations.append(
                f"Gross margin ratio {gross_margin_ratio:.1%} is below minimum {payload.min_gross_margin_ratio:.1%}."
            )
        if cac_payback_months > (payload.max_payback_months + 1e-12):
            violations.append(
                f"CAC payback {cac_payback_months:.2f} months exceeds max {payload.max_payback_months:.2f} months."
            )
        if (ltv_to_cac + 1e-12) < payload.min_ltv_to_cac:
            violations.append(
                f"LTV/CAC ratio {ltv_to_cac:.2f} is below minimum {payload.min_ltv_to_cac:.2f}."
            )

        monthly_net_retention = max(
            0.0, 1.0 - payload.monthly_gross_churn_rate + payload.monthly_expansion_rate
        )
        annualized_ndr = monthly_net_retention**12

        kill_switch_triggered = unit_gross_profit <= 0.0 or (
            cac_payback_months > payload.max_payback_months * 2.0
        )
        passed = len(violations) == 0

        # Normalize infinite values to large finite sentinel only if needed for JSON, or keep finite caps
        safe_payback = min(cac_payback_months, 9999.0)
        safe_ltv_to_cac = min(ltv_to_cac, 9999.0)

        return CohortPnLResult(
            cohort_id=payload.cohort_id,
            cohort_mrr_usd=cohort_mrr,
            unit_gross_profit_monthly_usd=unit_gross_profit,
            cohort_gross_profit_monthly_usd=cohort_gross_profit,
            gross_margin_ratio=gross_margin_ratio,
            cac_payback_months=safe_payback,
            ltv_per_customer_usd=ltv_per_customer,
            ltv_to_cac_ratio=safe_ltv_to_cac,
            annualized_ndr=annualized_ndr,
            kill_switch_triggered=kill_switch_triggered,
            passed=passed,
            violations=tuple(violations),
        )

    def validate_postconditions(
        self, payload: CohortPnLInput, result: CohortPnLResult
    ) -> None:
        expected_mrr = payload.active_customers * payload.arpa_monthly_usd
        if not math.isclose(result.cohort_mrr_usd, expected_mrr, rel_tol=1e-9):
            raise MarginViolationError("Postcondition breach: cohort_mrr_usd mismatch.")
        if result.passed and len(result.violations) > 0:
            raise MarginViolationError("Postcondition breach: passed=True with active violations.")
        if not result.passed and len(result.violations) == 0:
            raise MarginViolationError("Postcondition breach: passed=False without recorded violations.")


class SixMonthRetroAuditInput(BaseModel):
    """Input contract for Ramanujam's mandatory 6-Month Re-Pricing Retro-Audit."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    product_id: str = Field(..., min_length=1)
    forecast_gross_margin_ratio: float = Field(..., gt=0.0, lt=1.0)
    realized_gross_margin_ratio: float = Field(..., lt=1.0)
    forecast_hitl_prob: float = Field(..., ge=0.0, le=1.0)
    realized_hitl_prob: float = Field(..., ge=0.0, le=1.0)
    max_allowed_margin_drift: float = Field(default=0.05, gt=0.0, lt=0.50)


class SixMonthRetroAuditResult(BaseModel):
    """Output contract for the 6-Month Re-Pricing Retro-Audit."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    product_id: str = Field(..., min_length=1)
    margin_drift: float = Field(...)
    hitl_drift: float = Field(...)
    repricing_required: bool = Field(...)
    distillation_required: bool = Field(...)
    recommendation: str = Field(..., min_length=1)


class SixMonthPricingRetroAudit(
    EconomicGateContract[SixMonthRetroAuditInput, SixMonthRetroAuditResult]
):
    """Evaluates whether realized 6-month cohort unit economics match launch WTP forecasts."""

    def validate_preconditions(self, payload: SixMonthRetroAuditInput) -> None:
        if not (0.0 < payload.forecast_gross_margin_ratio < 1.0):
            raise MarginViolationError("forecast_gross_margin_ratio must be in (0, 1).")

    def _compute(self, payload: SixMonthRetroAuditInput) -> SixMonthRetroAuditResult:
        margin_drift = payload.forecast_gross_margin_ratio - payload.realized_gross_margin_ratio
        hitl_drift = payload.realized_hitl_prob - payload.forecast_hitl_prob

        repricing_required = margin_drift > (payload.max_allowed_margin_drift + 1e-12)
        distillation_required = hitl_drift > max(0.05, payload.forecast_hitl_prob * 0.50)

        if repricing_required and distillation_required:
            rec = (
                "Re-pricing and distillation required: realized margin drifted down by "
                f"{margin_drift:.1%} and HITL escalation rose by {hitl_drift:.1%}."
            )
        elif repricing_required:
            rec = (
                f"Re-pricing required: realized gross margin ({payload.realized_gross_margin_ratio:.1%}) "
                f"trails forecast ({payload.forecast_gross_margin_ratio:.1%}) by {margin_drift:.1%}."
            )
        elif distillation_required:
            rec = (
                f"Workflow distillation required: realized HITL rate ({payload.realized_hitl_prob:.1%}) "
                f"exceeds forecast ({payload.forecast_hitl_prob:.1%})."
            )
        else:
            rec = "6-month pricing and unit margin invariants are on track."

        return SixMonthRetroAuditResult(
            product_id=payload.product_id,
            margin_drift=margin_drift,
            hitl_drift=hitl_drift,
            repricing_required=repricing_required,
            distillation_required=distillation_required,
            recommendation=rec,
        )

    def validate_postconditions(
        self, payload: SixMonthRetroAuditInput, result: SixMonthRetroAuditResult
    ) -> None:
        expected_drift = payload.forecast_gross_margin_ratio - payload.realized_gross_margin_ratio
        if not math.isclose(result.margin_drift, expected_drift, rel_tol=1e-9, abs_tol=1e-12):
            raise MarginViolationError("Postcondition breach: margin_drift mismatch.")
