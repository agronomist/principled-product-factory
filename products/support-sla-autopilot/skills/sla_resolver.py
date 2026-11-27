"""Second Real Customer-Facing Product: Enterprise SLA Breach & Refund Autopilot
(`products/support-sla-autopilot/skills/sla_resolver.py`).

Solves a concrete customer problem (Joel Spolsky's FogBugz / Customer Support domain):
When an enterprise customer opens a severity ticket or experiences downtime exceeding their
contractual SLA (e.g., 99.9% monthly uptime = 43.2 minutes allowed downtime), manual support
queues take 4 days to calculate service credits, causing churn.

This product shares `platform.metering`, `platform.sre`, `platform.telemetry`, and
`platform.storage` with `products/demo-decision-engine/` without importing a single line
from `demo-decision-engine` (enforcing Law 2 Topological Isolation & Rule-of-Two).
"""

from __future__ import annotations

import math
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from platform.metering.margin_guard import ContributionMarginGate, UnitEconomicsInput
from platform.sre.fallback_circuit import (
    CircuitBreakerConfig,
    FallbackCircuit,
    FallbackTier,
)
from platform.telemetry.learning_signal import (
    IdempotentLearningLogger,
    LearningSignalTuple,
    compute_correction_diff,
)


class SLAResolutionAction(str, Enum):
    """Canonical customer support & SLA resolution outcomes."""

    AUTO_ISSUE_SERVICE_CREDIT = "auto_issue_service_credit"
    RESOLVE_WITH_RCA_NO_CREDIT = "resolve_with_rca_no_credit"
    ESCALATE_HIGH_VALUE_RETENTION = "escalate_high_value_retention"
    REJECT_INELIGIBLE_CLAIM = "reject_ineligible_claim"


class SLATicketInput(BaseModel):
    """Immutable Liskov precondition schema for an incoming customer SLA ticket."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticket_id: str = Field(..., min_length=1)
    customer_account_id: str = Field(..., min_length=1)
    monthly_contract_value_usd: float = Field(..., gt=0.0)
    contractual_sla_uptime_pct: float = Field(default=99.9, ge=90.0, lt=100.0)
    observed_downtime_minutes: float = Field(..., ge=0.0, le=43200.0)
    verified_by_telemetry: bool = Field(
        ...,
        description="True if platform Shewhart/Pingdom logs confirm the outage occurred.",
    )
    customer_churn_risk_score: float = Field(default=0.20, ge=0.0, le=1.0)
    simulate_primary_failure: bool = Field(default=False)
    agent_override_credit_usd: float | None = Field(default=None, ge=0.0)


class SLAResolutionOutput(BaseModel):
    """Immutable Liskov postcondition schema returned by `SLAAutopilotSkill`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticket_id: str = Field(..., min_length=1)
    customer_account_id: str = Field(..., min_length=1)
    allowed_downtime_minutes: float = Field(..., gt=0.0)
    excess_downtime_minutes: float = Field(..., ge=0.0)
    sla_breached: bool = Field(...)
    calculated_credit_usd: float = Field(..., ge=0.0)
    resolution_action: SLAResolutionAction = Field(...)
    selected_sre_tier: FallbackTier = Field(...)
    margin_gate_passed: bool = Field(...)
    learning_signal_key: str = Field(..., min_length=64, max_length=64)


class SLAAutopilotSkill:
    """Liskov-verified domain skill for `products/support-sla-autopilot`.

    Preconditions:
    - `monthly_contract_value_usd > 0`, `90.0 <= contractual_sla_uptime_pct < 100.0`.
    Postconditions:
    - `calculated_credit_usd` never exceeds `0.30 * monthly_contract_value_usd` (30% contractual cap).
    - Unverified claims (`verified_by_telemetry == False`) never issue automated service credits.
    """

    _MINUTES_PER_30_DAY_MONTH: float = 43200.0
    _MAX_CREDIT_CAP_RATIO: float = 0.30

    def __init__(
        self,
        margin_gate: ContributionMarginGate | None = None,
        learning_logger: IdempotentLearningLogger | None = None,
    ) -> None:
        self._margin_gate = margin_gate or ContributionMarginGate()
        self._logger = learning_logger or IdempotentLearningLogger()

    def validate_preconditions(
        self,
        ticket: SLATicketInput,
        economics: UnitEconomicsInput,
    ) -> None:
        if ticket.monthly_contract_value_usd <= 0.0:
            raise ValueError("Precondition failed: monthly_contract_value_usd must be > 0.")
        self._margin_gate.validate_preconditions(economics)

    def _compute_resolution(
        self,
        ticket: SLATicketInput,
    ) -> tuple[float, float, bool, float, SLAResolutionAction]:
        allowed_downtime = self._MINUTES_PER_30_DAY_MONTH * (
            (100.0 - ticket.contractual_sla_uptime_pct) / 100.0
        )
        excess = max(0.0, ticket.observed_downtime_minutes - allowed_downtime)
        breached = excess > 1e-6

        if not ticket.verified_by_telemetry:
            return (
                round(allowed_downtime, 4),
                round(excess, 4),
                False,
                0.0,
                SLAResolutionAction.REJECT_INELIGIBLE_CLAIM,
            )

        if not breached:
            return (
                round(allowed_downtime, 4),
                0.0,
                False,
                0.0,
                SLAResolutionAction.RESOLVE_WITH_RCA_NO_CREDIT,
            )

        # Tiered service credit schedule: 10% credit for < 4x allowed downtime, 25% for >= 4x, capped at 30%
        credit_ratio = 0.10 if excess < (allowed_downtime * 4.0) else 0.25
        credit_ratio = min(credit_ratio, self._MAX_CREDIT_CAP_RATIO)
        credit_usd = round(ticket.monthly_contract_value_usd * credit_ratio, 2)

        if ticket.customer_churn_risk_score >= 0.75 and ticket.monthly_contract_value_usd >= 5000.0:
            action = SLAResolutionAction.ESCALATE_HIGH_VALUE_RETENTION
        else:
            action = SLAResolutionAction.AUTO_ISSUE_SERVICE_CREDIT

        return (
            round(allowed_downtime, 4),
            round(excess, 4),
            True,
            credit_usd,
            action,
        )

    def execute(
        self,
        ticket: SLATicketInput,
        economics: UnitEconomicsInput,
    ) -> SLAResolutionOutput:
        self.validate_preconditions(ticket, economics)
        margin_res = self._margin_gate.evaluate(economics)

        def _primary(t: SLATicketInput) -> tuple[float, float, bool, float, SLAResolutionAction]:
            if t.simulate_primary_failure:
                raise RuntimeError("Primary frontier model timeout during SLA RCA synthesis")
            return self._compute_resolution(t)

        circuit = FallbackCircuit(
            handlers={
                FallbackTier.PRIMARY_FRONTIER_MODEL: _primary,
                FallbackTier.SECONDARY_DISTILLED_MODEL: self._compute_resolution,
                FallbackTier.TERTIARY_CACHED_DETERMINISTIC: self._compute_resolution,
            },
            config=CircuitBreakerConfig(failure_threshold=2, recovery_timeout_seconds=30.0),
        )
        sre_res = circuit.execute(ticket)
        allowed_min, excess_min, breached, credit_usd, action = sre_res.output

        sys_out = {
            "resolution_action": action.value,
            "calculated_credit_usd": credit_usd,
        }
        user_final = (
            {**sys_out, "calculated_credit_usd": ticket.agent_override_credit_usd}
            if ticket.agent_override_credit_usd is not None
            else None
        )
        diff = compute_correction_diff(sys_out, user_final)

        sig_record = self._logger.log_event(
            LearningSignalTuple(
                product_id="support-sla-autopilot",
                workflow_run_id=ticket.ticket_id,
                input_state=ticket.model_dump(mode="json"),
                system_output=sys_out,
                user_correction_diff=diff,
                verified_outcome={
                    "sla_breached": breached,
                    "margin_gate_passed": margin_res.passed,
                },
            )
        )

        out = SLAResolutionOutput(
            ticket_id=ticket.ticket_id,
            customer_account_id=ticket.customer_account_id,
            allowed_downtime_minutes=allowed_min,
            excess_downtime_minutes=excess_min,
            sla_breached=breached,
            calculated_credit_usd=credit_usd,
            resolution_action=action,
            selected_sre_tier=sre_res.selected_tier,
            margin_gate_passed=margin_res.passed,
            learning_signal_key=sig_record.idempotency_key,
        )
        self.validate_postconditions(ticket, out)
        return out

    def validate_postconditions(
        self,
        ticket: SLATicketInput,
        output: SLAResolutionOutput,
    ) -> None:
        max_allowed_credit = ticket.monthly_contract_value_usd * self._MAX_CREDIT_CAP_RATIO + 1e-6
        if output.calculated_credit_usd > max_allowed_credit:
            raise RuntimeError("Postcondition breach: service credit exceeded 30% contractual cap.")
        if not ticket.verified_by_telemetry and output.calculated_credit_usd > 0.0:
            raise RuntimeError("Postcondition breach: unverified outage claim issued positive credit.")
        if not output.sla_breached and not math.isclose(output.calculated_credit_usd, 0.0):
            raise RuntimeError("Postcondition breach: non-breached SLA issued positive credit.")
