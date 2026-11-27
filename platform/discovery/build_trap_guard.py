r"""Anti-Build-Trap Customer Value & Outcome Gate (`platform/discovery/build_trap_guard.py`).

An autonomous software factory (Foreman + pstack loops) makes *building* 10x faster—which makes
falling into **Melissa Perri's "Build Trap"** (measuring success by pull requests merged rather
than customer problems solved) 10x more dangerous.

This module enforces four structural anti-Build-Trap invariants before and after engineering:

1. **Tony Ulwick's Outcome-Driven Innovation (ODI) / JTBD Opportunity Score**:
   $$\text{OpportunityScore} = \text{Importance} + \max(\text{Importance} - \text{Satisfaction}, 0)$$
   - Where $\text{Importance} \in [1.0, 10.0]$ and $\text{Satisfaction} \in [1.0, 10.0]$ come from
     observed customer pain on the specific job step.
   - Scores $< 10.0$ are **overserved / low-value** (Seinfeld metaphor: building **Kramer's
     Coffee Table Book About Coffee Tables** or **The Urban Sombrero**—clever craftsmanship
     for a job no customer is hiring you to do).
   - Scores $\ge 10.0$ (and $\ge 12.0$ for Stage B/C) represent genuinely underserved customer outcomes.

2. **Skin-in-the-Game Customer Commitment Ladder (Rob Fitzpatrick *The Mom Test* & Ramanujam *Monetizing Innovation*)**:
   - "Someone at some point might like it" (`SPECULATIVE_IDEA` or `POLITE_COMPLIMENT`) has zero
     predictive validity and is **BLOCKED** from production buildout.
   - Reaching the `implementer` station requires verifiable customer skin-in-the-game:
     - `TIME_COMMITMENT` (customer invested $\ge 45$ mins shadowing a live workflow or providing real production data).
     - `REPUTATION_COMMITMENT` (champion introduced decision-makers / procurement).
     - `FINANCIAL_OR_PAIN_COMMITMENT` (signed Letter of Intent, paid pilot deposit, contractual WTP, or verified production churn/support ticket spike with $n \ge \text{min\_customers}$).

3. **Falsifiable Customer Outcome Predicate (Not an Output / Feature Checkbox)**:
   - Every proposal must declare a measurable **customer behavior shift** (`baseline_metric -> target_metric`
     within `evaluation_window_days`), e.g., *"Reduce customer onboarding time-to-first-value from
     45 mins to < 5 mins across >= 30% of active cohort"*, NOT *"Ship settings modal v2"*.

4. **Post-Ship Adoption & Value Realization Audit (Zombie Feature Sunset)**:
   - Shipping a PR is the *start* of accountability, not the finish line.
   - After `evaluation_window_days`, `PostShipOutcomeAudit` compares realized customer adoption
     and outcome lift against the pre-build promise.
   - If customers aren't using it (`realized_adoption_rate < min_adoption_rate`) or the customer's
     job metric didn't improve, the factory emits `SUNSET_AND_DELETE_CODE` (`principle-subtract-before-you-add`)
     rather than letting dead features accrete maintenance tax.
"""

from __future__ import annotations

import math
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BuildTrapViolationError(PermissionError):
    """Raised when a feature request or work item fails the Customer Value & Anti-Build-Trap Gate."""


class CommitmentTier(str, Enum):
    """Customer evidence hierarchy from *The Mom Test* (Fitzpatrick) and *Monetizing Innovation*."""

    SPECULATIVE_IDEA = "speculative_idea"  # "I think users at some point will like this" -> BLOCKED
    POLITE_COMPLIMENT = "polite_compliment"  # "Sounds cool, let me know when you launch" -> BLOCKED
    TIME_COMMITMENT = "time_commitment"  # Allowed for Stage A discovery probes only
    REPUTATION_COMMITMENT = "reputation_commitment"  # Allowed for Stage A / early Stage B
    FINANCIAL_OR_PAIN_COMMITMENT = "financial_or_pain_commitment"  # Required for Stage B/C buildout

    @property
    def evidence_rank(self) -> int:
        return {
            CommitmentTier.SPECULATIVE_IDEA: 0,
            CommitmentTier.POLITE_COMPLIMENT: 1,
            CommitmentTier.TIME_COMMITMENT: 2,
            CommitmentTier.REPUTATION_COMMITMENT: 3,
            CommitmentTier.FINANCIAL_OR_PAIN_COMMITMENT: 4,
        }[self]


def compute_ulwick_opportunity_score(importance: float, satisfaction: float) -> float:
    r"""Compute Tony Ulwick's JTBD Opportunity Score:
    $$\text{OpportunityScore} = \text{Importance} + \max(\text{Importance} - \text{Satisfaction}, 0)$$

    Preconditions:
    - `1.0 <= importance <= 10.0`
    - `1.0 <= satisfaction <= 10.0`
    Postconditions:
    - Returns score in `[1.0, 19.0]`. Scores `>= 10.0` indicate an underserved customer outcome.
    """
    if not (1.0 <= importance <= 10.0):
        raise ValueError(f"importance must be in [1.0, 10.0], got {importance}.")
    if not (1.0 <= satisfaction <= 10.0):
        raise ValueError(f"satisfaction must be in [1.0, 10.0], got {satisfaction}.")
    return round(importance + max(importance - satisfaction, 0.0), 4)


class JTBDOpportunityInput(BaseModel):
    """Customer Job-to-Be-Done (JTBD) and measurable outcome contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    customer_segment: str = Field(
        ...,
        min_length=3,
        description="Specific customer persona/segment struggling with the job.",
    )
    struggling_moment: str = Field(
        ...,
        min_length=10,
        description="Concrete situation/trigger where the customer's current workaround fails.",
    )
    desired_customer_outcome: str = Field(
        ...,
        min_length=10,
        description="Measurable progress the customer wants to achieve (not a UI feature description).",
    )
    importance_score: float = Field(
        ...,
        ge=1.0,
        le=10.0,
        description="Customer rating [1..10] of how important this outcome is.",
    )
    current_satisfaction_score: float = Field(
        ...,
        ge=1.0,
        le=10.0,
        description="Customer rating [1..10] of satisfaction with their current alternative.",
    )


class JTBDOpportunityScore(BaseModel):
    """Evaluated JTBD opportunity score and underserved classification."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    opportunity_score: float = Field(..., ge=1.0, le=19.0)
    is_underserved: bool = Field(..., description="True when opportunity_score >= 10.0.")
    is_high_leverage: bool = Field(..., description="True when opportunity_score >= 12.0.")


class CustomerEvidenceArtifact(BaseModel):
    """Empirical proof that real customers experience this problem and committed skin-in-the-game."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    proposal_id: str = Field(..., min_length=1)
    lifecycle_stage: str = Field(default="Stage_B", pattern=r"^Stage_[ABC]$")
    jtbd: JTBDOpportunityInput = Field(...)
    commitment_tier: CommitmentTier = Field(...)
    verified_customer_count: int = Field(
        ...,
        ge=0,
        description="Number of distinct customers exhibiting the pain or signing commitments.",
    )
    evidence_pointers: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Links/IDs to real customer call transcripts, LOIs, churn logs, or support tickets.",
    )
    falsifiable_outcome_metric: str = Field(
        ...,
        min_length=5,
        description="Customer behavior or value metric that must move post-ship.",
    )
    baseline_metric_value: float = Field(...)
    target_metric_value: float = Field(...)
    evaluation_window_days: int = Field(
        default=30,
        ge=7,
        le=180,
        description="Days post-launch before running the mandatory Zombie-Feature Sunset Audit.",
    )

    @model_validator(mode="after")
    def _validate_finite_metrics(self) -> CustomerEvidenceArtifact:
        if not math.isfinite(self.baseline_metric_value) or not math.isfinite(
            self.target_metric_value
        ):
            raise ValueError("baseline_metric_value and target_metric_value must be finite.")
        return self


class BuildTrapVerdictType(str, Enum):
    """Verdicts emitted by `BuildTrapGate`."""

    APPROVED_FOR_BUILD = "approved_for_build"
    APPROVED_DISCOVERY_PROTOTYPE_ONLY = "approved_discovery_prototype_only"
    BLOCKED_SPECULATIVE_BUILD_TRAP = "blocked_speculative_build_trap"
    BLOCKED_OVERSERVED_JTBD = "blocked_overserved_jtbd"
    BLOCKED_INSUFFICIENT_CUSTOMER_EVIDENCE = "blocked_insufficient_customer_evidence"
    BLOCKED_NO_MEASURABLE_OUTCOME_SHIFT = "blocked_no_measurable_outcome_shift"


class BuildTrapVerdict(BaseModel):
    """Immutable postcondition verdict from `BuildTrapGate.evaluate`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    proposal_id: str = Field(..., min_length=1)
    verdict: BuildTrapVerdictType = Field(...)
    approved_for_production_build: bool = Field(...)
    approved_for_discovery_probe: bool = Field(...)
    jtbd_score: JTBDOpportunityScore = Field(...)
    commitment_tier: CommitmentTier = Field(...)
    blocking_reasons: tuple[str, ...] = Field(default_factory=tuple)
    metaphor_summary: str = Field(..., min_length=1)


class BuildTrapGate:
    """Enforces the Anti-Build-Trap Customer Value Gate before engineering capacity is spent.

    Blocks any work item where:
    1. Commitment is merely `SPECULATIVE_IDEA` ("someone at some point will like it") or
       `POLITE_COMPLIMENT` ("that sounds neat").
    2. Ulwick JTBD Opportunity Score `< min_opportunity_score` (default `10.0`), meaning
       customers are already satisfied with their status quo.
    3. `verified_customer_count` is below stage minimum (`>= 3` for Stage A, `>= 10` for Stage B,
       `>= 25` for Stage C) or `evidence_pointers` is empty.
    4. `target_metric_value == baseline_metric_value` (measuring output/"ship it" instead of
       a customer outcome delta).
    """

    def __init__(self, min_opportunity_score: float = 10.0) -> None:
        if not (1.0 <= min_opportunity_score <= 19.0):
            raise ValueError("min_opportunity_score must be in [1.0, 19.0].")
        self._min_opp_score = min_opportunity_score

    def evaluate(self, artifact: CustomerEvidenceArtifact) -> BuildTrapVerdict:
        opp_val = compute_ulwick_opportunity_score(
            artifact.jtbd.importance_score,
            artifact.jtbd.current_satisfaction_score,
        )
        jtbd_score = JTBDOpportunityScore(
            opportunity_score=opp_val,
            is_underserved=(opp_val >= 10.0),
            is_high_leverage=(opp_val >= 12.0),
        )

        reasons: list[str] = []

        # Rule 1: Reject "someone at some point will like it" (Speculative / Polite Compliments)
        if artifact.commitment_tier in (
            CommitmentTier.SPECULATIVE_IDEA,
            CommitmentTier.POLITE_COMPLIMENT,
        ):
            reasons.append(
                f"Commitment tier '{artifact.commitment_tier.value}' is a Build Trap: "
                "building because 'someone at some point might like it' or gave a polite compliment "
                "violates The Mom Test. Require time, reputation, or financial/pain skin-in-the-game."
            )

        # Rule 2: Reject overserved jobs where customers don't have an acute gap
        if opp_val < self._min_opp_score:
            reasons.append(
                f"Ulwick JTBD Opportunity Score {opp_val:.2f} < {self._min_opp_score:.2f} "
                f"(importance={artifact.jtbd.importance_score}, satisfaction={artifact.jtbd.current_satisfaction_score}): "
                "customers are already adequately served by their current alternative."
            )

        # Rule 3: Stage-appropriate empirical customer sample & resolvable evidence pointers
        min_customers_by_stage = {"Stage_A": 3, "Stage_B": 10, "Stage_C": 25}
        req_customers = min_customers_by_stage.get(artifact.lifecycle_stage, 10)
        if artifact.verified_customer_count < req_customers:
            reasons.append(
                f"{artifact.lifecycle_stage} requires >= {req_customers} verified customers with this pain; "
                f"found {artifact.verified_customer_count}."
            )
        if not artifact.evidence_pointers:
            reasons.append(
                "Zero customer evidence_pointers provided (must cite real call transcripts, LOIs, churn logs, or support tickets)."
            )

        # Rule 4: Stage B/C production buildout requires FINANCIAL_OR_PAIN_COMMITMENT or REPUTATION_COMMITMENT
        if (
            artifact.lifecycle_stage in ("Stage_B", "Stage_C")
            and artifact.commitment_tier.evidence_rank < CommitmentTier.REPUTATION_COMMITMENT.evidence_rank
        ):
            reasons.append(
                f"{artifact.lifecycle_stage} production buildout requires at least 'reputation_commitment' "
                f"or 'financial_or_pain_commitment', got '{artifact.commitment_tier.value}'."
            )

        # Rule 5: Outcome metric must demand a measurable change from baseline
        if math.isclose(
            artifact.baseline_metric_value,
            artifact.target_metric_value,
            rel_tol=1e-6,
            abs_tol=1e-9,
        ):
            reasons.append(
                "No measurable customer outcome shift: target_metric_value equals baseline_metric_value "
                "(feature-shipping output theater instead of customer outcome)."
            )

        if not reasons:
            if (
                artifact.lifecycle_stage == "Stage_A"
                and artifact.commitment_tier == CommitmentTier.TIME_COMMITMENT
            ):
                verdict = BuildTrapVerdictType.APPROVED_DISCOVERY_PROTOTYPE_ONLY
                prod_ok = False
                probe_ok = True
                metaphor = (
                    "Stage A Concierge Probe Approved: Customers put time on the pitch; "
                    "run a cheap falsification prototype before building stadium infrastructure."
                )
            else:
                verdict = BuildTrapVerdictType.APPROVED_FOR_BUILD
                prod_ok = True
                probe_ok = True
                metaphor = (
                    f"Total Football Through-Ball into Open Space: Acute underserved customer job "
                    f"(Opportunity Score={opp_val:.1f}) backed by {artifact.verified_customer_count} "
                    f"verified customers with '{artifact.commitment_tier.value}'."
                )
        else:
            prod_ok = False
            probe_ok = False
            if artifact.commitment_tier in (
                CommitmentTier.SPECULATIVE_IDEA,
                CommitmentTier.POLITE_COMPLIMENT,
            ):
                verdict = BuildTrapVerdictType.BLOCKED_SPECULATIVE_BUILD_TRAP
            elif opp_val < self._min_opp_score:
                verdict = BuildTrapVerdictType.BLOCKED_OVERSERVED_JTBD
            elif math.isclose(
                artifact.baseline_metric_value,
                artifact.target_metric_value,
                rel_tol=1e-6,
                abs_tol=1e-9,
            ):
                verdict = BuildTrapVerdictType.BLOCKED_NO_MEASURABLE_OUTCOME_SHIFT
            else:
                verdict = BuildTrapVerdictType.BLOCKED_INSUFFICIENT_CUSTOMER_EVIDENCE

            metaphor = (
                "Blocked Build Trap (Kramer's Coffee Table Book / Sterile 80% Midfield Possession): "
                "Refusing to burn engineering cycles on a feature without verified customer pull and skin-in-the-game."
            )

        return BuildTrapVerdict(
            proposal_id=artifact.proposal_id,
            verdict=verdict,
            approved_for_production_build=prod_ok,
            approved_for_discovery_probe=probe_ok,
            jtbd_score=jtbd_score,
            commitment_tier=artifact.commitment_tier,
            blocking_reasons=tuple(reasons),
            metaphor_summary=metaphor,
        )

    def check_or_raise(self, artifact: CustomerEvidenceArtifact) -> BuildTrapVerdict:
        """Evaluate the Anti-Build-Trap Gate and raise `BuildTrapViolationError` if blocked."""
        res = self.evaluate(artifact)
        if not (res.approved_for_production_build or res.approved_for_discovery_probe):
            raise BuildTrapViolationError(
                f"Build Trap Gate blocked '{artifact.proposal_id}': {'; '.join(res.blocking_reasons)}"
            )
        return res


# ---------------------------------------------------------------------------
# Post-Ship Customer Outcome & Zombie-Feature Sunset Audit
# ---------------------------------------------------------------------------


class PostShipRecommendation(str, Enum):
    """Post-launch outcome audit decisions."""

    SCALE_AND_COMPOUND = "scale_and_compound"
    ITERATE_ON_FRICTION = "iterate_on_friction"
    SUNSET_AND_DELETE_CODE = "sunset_and_delete_code"


class PostShipOutcomeInput(BaseModel):
    """Telemetry snapshot comparing a shipped feature's promised customer outcome against reality."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_id: str = Field(..., min_length=1)
    days_since_ship: int = Field(..., ge=1)
    target_adoption_rate: float = Field(..., gt=0.0, le=1.0)
    realized_adoption_rate: float = Field(..., ge=0.0, le=1.0)
    baseline_outcome_metric: float = Field(...)
    promised_outcome_metric: float = Field(...)
    realized_outcome_metric: float = Field(...)
    higher_is_better: bool = Field(default=True)
    unprompted_positive_retention_signal: bool = Field(
        default=False,
        description="True if cohort retention or repeat task completion visibly lifted.",
    )


class PostShipOutcomeAuditResult(BaseModel):
    """Immutable verdict from `PostShipOutcomeAudit.evaluate`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_id: str = Field(..., min_length=1)
    adoption_ratio_of_target: float = Field(..., ge=0.0)
    outcome_lift_achieved_ratio: float = Field(...)
    is_zombie_feature: bool = Field(...)
    recommendation: PostShipRecommendation = Field(...)
    rationale: str = Field(..., min_length=1)


class PostShipOutcomeAudit:
    """Closes the loop *after* code ships so the factory deletes features that fail to deliver
    real customer value (`principle-subtract-before-you-add`).

    If a shipped feature fails to reach even 40% of its target adoption AND delivers < 25%
    of the promised customer outcome improvement, it is classified as a **Zombie Feature**
    (`SUNSET_AND_DELETE_CODE`).
    """

    def evaluate(self, payload: PostShipOutcomeInput) -> PostShipOutcomeAuditResult:
        adoption_ratio = payload.realized_adoption_rate / payload.target_adoption_rate

        if payload.higher_is_better:
            promised_delta = payload.promised_outcome_metric - payload.baseline_outcome_metric
            realized_delta = payload.realized_outcome_metric - payload.baseline_outcome_metric
        else:
            promised_delta = payload.baseline_outcome_metric - payload.promised_outcome_metric
            realized_delta = payload.baseline_outcome_metric - payload.realized_outcome_metric

        if abs(promised_delta) <= 1e-12:
            lift_ratio = 0.0
        else:
            lift_ratio = realized_delta / promised_delta

        is_zombie = (adoption_ratio < 0.40) and (lift_ratio < 0.25)

        if is_zombie:
            rec = PostShipRecommendation.SUNSET_AND_DELETE_CODE
            rationale = (
                f"Zombie Feature Detected (George Costanza relationship exit / subtract-before-you-add): "
                f"'{payload.feature_id}' achieved only {adoption_ratio:.0%} of target adoption and "
                f"{lift_ratio:.0%} of promised customer outcome lift after {payload.days_since_ship} days. "
                "Sunset the feature and delete the dead code rather than paying permanent maintenance tax."
            )
        elif adoption_ratio >= 0.80 and lift_ratio >= 0.75:
            rec = PostShipRecommendation.SCALE_AND_COMPOUND
            rationale = (
                f"Verified Customer Value: '{payload.feature_id}' achieved {adoption_ratio:.0%} of target "
                f"adoption and {lift_ratio:.0%} of promised outcome lift. Graduate to core workflow."
            )
        else:
            rec = PostShipRecommendation.ITERATE_ON_FRICTION
            rationale = (
                f"Partial value realization (adoption={adoption_ratio:.0%}, outcome_lift={lift_ratio:.0%}): "
                "customers want the job done, but usability or onboarding friction is limiting full lift."
            )

        return PostShipOutcomeAuditResult(
            feature_id=payload.feature_id,
            adoption_ratio_of_target=round(adoption_ratio, 4),
            outcome_lift_achieved_ratio=round(lift_ratio, 4),
            is_zombie_feature=is_zombie,
            recommendation=rec,
            rationale=rationale,
        )
