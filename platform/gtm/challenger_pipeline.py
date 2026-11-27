r"""Challenger Sale & Commercial Teaching Pipeline Engine (`platform/gtm/challenger_pipeline.py`).

Implements Matthew Dixon & Brent Adamson's *The Challenger Sale* and *The JOLT Effect*
directly inside `principled-product-factory`:

1. **Why Relationship Builders Lose Complex B2B Deals (The 5 Archetypes)**:
   - Dixon & Adamson's CEB/Gartner study of 6,000+ reps found that in complex solutions,
     **Challengers** make up 54% of star performers, while **Relationship Builders** make up
     only 4%—because Relationship Builders acquiesce to every one-off customer feature demand
     (dragging the software factory straight into the **Build Trap** and margin destruction).
   - Challengers win on three pillars:
     * **Teach for Differentiation** (Commercial Teaching)
     * **Tailor for Resonance** (Stakeholder-specific economic & operational outcomes)
     * **Take Control of the Sale** (Constructive Tension around value, price, and custom demands)

2. **The 6-Step Commercial Teaching Choreography (`ChallengerChoreographyValidator`)**:
   - **Rule**: Never lead with your product capabilities! Leading with product features commoditizes
     you into a feature-comparison bakeoff.
   - Canonical 6-Step Sequence:
     1. `warmer`: Validate the customer's world using benchmarked industry observations (never
        the lazy "What keeps you up at night?" interrogation).
     2. `reframe`: Introduce a non-obvious insight showing that what they thought was a normal
        cost of doing business is actually a structural blind spot costing them margin or velocity.
     3. `rational_drowning`: Quantify the exact financial Cost of Inaction ($\text{COI}_{\text{annual}}$)
        using their own unit economics.
     4. `emotional_impact`: Humanize how that broken workflow hurts their team day-to-day.
     5. `a_new_way`: Define the architectural/operational capabilities required to solve the
        reframed problem—**still without pitching product brand names or SKU features**.
     6. `our_solution_map`: Prove how our unique differentiators (`platform/` + `products/` invariants)
        are the only way to execute Step 5.

3. **Tailoring for Resonance Across the Mobilizer & Consensus Committee**:
   - Maps the same commercial reframe onto four distinct enterprise buyer lenses:
     `ECONOMIC_BUYER_CFO` (ROIC, margin, CAC payback), `TECHNICAL_ARCHITECT_VP_ENG` (Liskov/Parnas,
     3-tier SRE fallback, zero lock-in), `MOBILIZER_CHAMPION` (internal political win, fast Stage A proof),
     and `END_USER_OPERATOR` (workflow elimination, zero drudgery).

4. **Taking Control & Constructive Tension (Anti-Build-Trap Deal Guard)**:
   - When a prospect demands a bespoke one-off feature or an unprincipled discount, a Relationship
     Builder caves. Our `ChallengerPipelineEngine` evaluates:
     * Does the custom demand pass `BuildTrapGate` (Ulwick Opportunity Score $\ge 10.0$ across the
       broader market)? If not, **push back with Constructive Tension** and re-anchor on the
       core reframed ROI rather than polluting the product roadmap.
     * Does the deal preserve the **Contribution Margin Gate** (`margin_guard.py`)? Never trade
       discount without extracting a **Give-Get** (multi-year commitment, case study, faster signature,
       or upfront payment).

5. **Overcoming Customer Indecision (*The JOLT Effect*)**:
   - 40–60% of B2B pipeline is lost not to competitors, but to **"No Decision"** driven by
     **FOMU (Fear of Messing Up)** vs. FOMO.
   - Enforces the 4 JOLT moves: **J**udge the level of indecision, **O**ffer a bold recommendation
     (narrowing option overload), **L**imit the exploration (cap endless POC scope creep), and
     **T**ake risk off the table (via Stage A bounded trials and SLA fallback guarantees).
"""

from __future__ import annotations

import math
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platform.discovery.build_trap_guard import (
    BuildTrapGate,
    CustomerEvidenceArtifact,
)
from platform.metering.margin_guard import ContributionMarginGate, UnitEconomicsInput


class SalesRepArchetype(str, Enum):
    """The 5 sales rep profiles identified in *The Challenger Sale* (Dixon & Adamson)."""

    CHALLENGER = "challenger"  # 54% of high performers in complex sales (Teaches, Tailors, Takes Control)
    LONE_WOLF = "lone_wolf"
    HARD_WORKER = "hard_worker"
    PROBLEM_SOLVER = "problem_solver"
    RELATIONSHIP_BUILDER = "relationship_builder"  # Only 4% of high performers; caves to Build Trap requests


class StakeholderRole(str, Enum):
    """Enterprise buying committee personas for 'Tailor for Resonance'."""

    ECONOMIC_BUYER_CFO = "economic_buyer_cfo"
    TECHNICAL_ARCHITECT_VP_ENG = "technical_architect_vp_eng"
    MOBILIZER_CHAMPION = "mobilizer_champion"
    END_USER_OPERATOR = "end_user_operator"


class ChallengerChoreographyInput(BaseModel):
    """Input contract for the 6-Step Commercial Teaching pitch choreography."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pitch_id: str = Field(..., min_length=1)
    target_segment: str = Field(..., min_length=3)
    step_1_warmer: str = Field(
        ...,
        min_length=15,
        description="Empathetic industry benchmark observation (never 'what keeps you up at night?').",
    )
    step_2_reframe: str = Field(
        ...,
        min_length=15,
        description="Counter-intuitive insight exposing an unrecognized root cause or hidden cost.",
    )
    step_3_rational_drowning_annual_coi_usd: float = Field(
        ...,
        gt=0.0,
        description="Quantified annual Cost of Inaction (COI) in USD if the customer keeps the status quo.",
    )
    annual_solution_price_usd: float = Field(
        ...,
        gt=0.0,
        description="Annual contract value (ACV) of our proposed solution in USD.",
    )
    step_4_emotional_impact: str = Field(
        ...,
        min_length=15,
        description="Concrete narrative showing how the status-quo failure mode burns out their team.",
    )
    step_5_a_new_way: str = Field(
        ...,
        min_length=15,
        description="Vendor-agnostic behavioral/architectural shift required to solve the reframe.",
    )
    step_6_our_solution_map: str = Field(
        ...,
        min_length=15,
        description="How our unique capabilities are the only way to deliver Step 5.",
    )
    leads_with_product_pitch_in_early_steps: bool = Field(
        default=False,
        description="True if Steps 1-5 prematurely pitch product SKU features before earning the reframe.",
    )
    leads_to_unique_differentiators: bool = Field(
        default=True,
        description="True if the reframe leads exclusively to our unique capabilities (Rule 1 of Commercial Teaching).",
    )


class ChallengerChoreographyResult(BaseModel):
    """Immutable evaluation of a 6-Step Commercial Teaching pitch."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pitch_id: str = Field(..., min_length=1)
    roi_multiple_on_inaction: float = Field(..., gt=0.0)
    monthly_cost_of_delay_usd: float = Field(..., gt=0.0)
    payback_months_on_coi: float = Field(..., gt=0.0)
    valid_choreography: bool = Field(...)
    violations: tuple[str, ...] = Field(default_factory=tuple)
    metaphor_summary: str = Field(..., min_length=1)


class ChallengerChoreographyValidator:
    """Validates the 6-Step Commercial Teaching Choreography from *The Challenger Sale*:

    Enforces:
    1. **No Premature Product Pitch**: Steps 1–5 must build the insight, reframe, rational drowning,
       emotional impact, and "a new way" *before* Step 6 mentions our product features.
    2. **No Lazy Discovery Questions**: Rejects "what keeps you up at night" cliches in Step 1.
    3. **Rational Drowning ROI Threshold**: Annual Cost of Inaction ($\text{COI}$) must be at least
       $3.0\times$ the proposed solution price (`payback_months_on_coi <= 4.0`) so urgency is undeniable.
    4. **Lead to Unique Strengths**: The teaching pitch must tie directly to our unique capabilities.
    """

    def __init__(self, min_coi_to_price_multiple: float = 3.0) -> None:
        if min_coi_to_price_multiple < 1.0:
            raise ValueError("min_coi_to_price_multiple must be >= 1.0.")
        self._min_multiple = min_coi_to_price_multiple

    def evaluate(self, payload: ChallengerChoreographyInput) -> ChallengerChoreographyResult:
        roi_multiple = (
            payload.step_3_rational_drowning_annual_coi_usd / payload.annual_solution_price_usd
        )
        monthly_coi = payload.step_3_rational_drowning_annual_coi_usd / 12.0
        payback_months = payload.annual_solution_price_usd / monthly_coi

        violations: list[str] = []

        if payload.leads_with_product_pitch_in_early_steps:
            violations.append(
                "Premature product pitch in Steps 1-5: Commercial Teaching must earn the Reframe, "
                "Rational Drowning, and 'A New Way' before introducing product features in Step 6."
            )
        if "keeps you up at night" in payload.step_1_warmer.lower():
            violations.append(
                "Step 1 Warmer uses the lazy cliché 'What keeps you up at night?'. "
                "Challengers lead with researched benchmark hypotheses, not blank-slate interrogations."
            )
        if (roi_multiple + 1e-9) < self._min_multiple:
            violations.append(
                f"Step 3 Rational Drowning COI multiple ({roi_multiple:.2f}x) is below required "
                f"{self._min_multiple:.2f}x threshold (COI=${payload.step_3_rational_drowning_annual_coi_usd:,.2f} "
                f"vs Price=${payload.annual_solution_price_usd:,.2f})."
            )
        if not payload.leads_to_unique_differentiators:
            violations.append(
                "Commercial Teaching violation: Reframe does not lead to our unique differentiators "
                "(teaching the customer an insight that a cheaper competitor can fulfill)."
            )

        valid = len(violations) == 0
        if valid:
            metaphor = (
                f"Challenger Commercial Teaching Validated (Cruyff space-creation before the strike): "
                f"Reframed hidden status-quo bleed of ${monthly_coi:,.2f}/month ({roi_multiple:.1f}x ROI, "
                f"{payback_months:.1f}-month payback) leading directly to our unique platform moat."
            )
        else:
            metaphor = (
                "Blocked Pitch (George Costanza pitching 'a show about nothing' without a hook): "
                "Failed Challenger 6-step commercial teaching choreography."
            )

        return ChallengerChoreographyResult(
            pitch_id=payload.pitch_id,
            roi_multiple_on_inaction=round(roi_multiple, 4),
            monthly_cost_of_delay_usd=round(monthly_coi, 2),
            payback_months_on_coi=round(payback_months, 4),
            valid_choreography=valid,
            violations=tuple(violations),
            metaphor_summary=metaphor,
        )


class TailoredResonanceBrief(BaseModel):
    """Pillar 2 ('Tailor for Resonance'): Translates the Commercial Teaching reframe for a specific stakeholder."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    stakeholder_role: StakeholderRole = Field(...)
    primary_value_driver: str = Field(..., min_length=1)
    tailored_reframe_hook: str = Field(..., min_length=1)
    proof_metric_to_lead_with: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Pillar 3: Taking Control of the Sale & Constructive Tension (Anti-Build-Trap + Margin Guard)
# ---------------------------------------------------------------------------


class ConstructiveTensionInput(BaseModel):
    """Evaluates how to handle a prospect's demand for a discount or a bespoke custom feature."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: str = Field(..., min_length=1)
    rep_archetype: SalesRepArchetype = Field(default=SalesRepArchetype.CHALLENGER)
    list_annual_price_usd: float = Field(..., gt=0.0)
    requested_discount_ratio: float = Field(default=0.0, ge=0.0, lt=1.0)
    customer_give_get_concession: str | None = Field(
        default=None,
        description="Concession extracted in exchange for any discount (e.g., '2-year upfront + public case study').",
    )
    unit_economics_at_discounted_price: UnitEconomicsInput = Field(...)
    bespoke_feature_demand: CustomerEvidenceArtifact | None = Field(
        default=None,
        description="Optional custom feature demanded by the prospect as a condition of signing.",
    )


class ConstructiveTensionResult(BaseModel):
    """Decision emitted by Challenger Constructive Tension evaluation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: str = Field(..., min_length=1)
    discount_approved: bool = Field(...)
    bespoke_feature_approved: bool = Field(...)
    pushed_back_on_build_trap: bool = Field(...)
    pushed_back_on_untraded_discount: bool = Field(...)
    margin_gate_passed: bool = Field(...)
    challenger_response_script: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# JOLT Effect: Overcoming Customer Indecision (FOMU vs. FOMO)
# ---------------------------------------------------------------------------


class JoltIndecisionSignal(BaseModel):
    """Diagnoses customer FOMU (Fear of Messing Up) across the 3 JOLT dimensions."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: str = Field(..., min_length=1)
    valuation_problem_option_overload: bool = Field(
        default=False,
        description="Customer is paralyzed choosing between too many tiers, models, or configurations.",
    )
    lack_of_information_endless_poc_creep: bool = Field(
        default=False,
        description="Customer keeps asking for 'one more custom demo/POC check' out of fear.",
    )
    outcome_uncertainty_fear_of_failure: bool = Field(
        default=False,
        description="Customer fears getting fired if implementation fails to deliver ROI.",
    )


class JoltIndecisionPlaybook(BaseModel):
    """Prescriptive JOLT intervention to rescue a deal from 'No Decision'."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: str = Field(..., min_length=1)
    fomu_risk_level: str = Field(..., pattern=r"^(low|moderate|high_no_decision_risk)$")
    j_judge_diagnosis: str = Field(..., min_length=1)
    o_offer_recommendation: str = Field(..., min_length=1)
    l_limit_exploration: str = Field(..., min_length=1)
    t_take_risk_off_table: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# End-to-End Challenger Deal & Pipeline Qualification Engine
# ---------------------------------------------------------------------------


class DealHealthVerdict(str, Enum):
    """Pipeline qualification statuses."""

    ADVANCE_HIGH_VELOCITY = "advance_high_velocity"
    INTERVENE_WITH_JOLT_AND_REFRAME = "intervene_with_jolt_and_reframe"
    PUSH_BACK_CONSTRUCTIVE_TENSION = "push_back_constructive_tension"
    DISQUALIFY_UNPROFITABLE_OR_NO_MOBILIZER = "disqualify_unprofitable_or_no_mobilizer"


class DealQualificationInput(BaseModel):
    """Complete Challenger + JOLT + Unit-Margin pipeline deal evaluation input."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: str = Field(..., min_length=1)
    has_verified_mobilizer: bool = Field(
        ...,
        description="True if we have a 'Go-Getter', 'Teacher', or 'Skeptic' Mobilizer (not just a 'Talker').",
    )
    choreography: ChallengerChoreographyInput = Field(...)
    tension: ConstructiveTensionInput = Field(...)
    jolt_signal: JoltIndecisionSignal = Field(...)


class DealQualificationResult(BaseModel):
    """Consolidated Challenger pipeline health and action report."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deal_id: str = Field(..., min_length=1)
    verdict: DealHealthVerdict = Field(...)
    choreography_result: ChallengerChoreographyResult = Field(...)
    tension_result: ConstructiveTensionResult = Field(...)
    jolt_playbook: JoltIndecisionPlaybook = Field(...)
    tailored_stakeholder_briefs: tuple[TailoredResonanceBrief, ...] = Field(...)
    weighted_pipeline_ev_usd: float = Field(..., ge=0.0)


class ChallengerPipelineEngine:
    """Orchestrates Challenger Sale (Teach, Tailor, Take Control) + JOLT Effect + Anti-Build-Trap
    + Contribution Margin Gate across the B2B revenue pipeline.
    """

    def __init__(
        self,
        choreography_validator: ChallengerChoreographyValidator | None = None,
        build_trap_gate: BuildTrapGate | None = None,
        margin_gate: ContributionMarginGate | None = None,
    ) -> None:
        self._choreography = choreography_validator or ChallengerChoreographyValidator()
        self._build_trap = build_trap_gate or BuildTrapGate()
        self._margin_gate = margin_gate or ContributionMarginGate()

    def tailor_for_committee(
        self,
        choreography: ChallengerChoreographyInput,
    ) -> tuple[TailoredResonanceBrief, ...]:
        """Pillar 2 ('Tailor for Resonance'): Generate stakeholder-specific resonance briefs."""
        coi = choreography.step_3_rational_drowning_annual_coi_usd
        price = choreography.annual_solution_price_usd
        monthly_bleed = coi / 12.0

        return (
            TailoredResonanceBrief(
                stakeholder_role=StakeholderRole.ECONOMIC_BUYER_CFO,
                primary_value_driver="Contribution Margin Protection, ROIC & CAC Payback",
                tailored_reframe_hook=(
                    f"Every month of status-quo delay leaks ${monthly_bleed:,.2f} in unrecovered COGS/ops "
                    f"(${coi:,.2f}/yr vs ${price:,.2f}/yr ACV)."
                ),
                proof_metric_to_lead_with="Unit Contribution Margin >= 65% & Payback < 4 months",
            ),
            TailoredResonanceBrief(
                stakeholder_role=StakeholderRole.TECHNICAL_ARCHITECT_VP_ENG,
                primary_value_driver="Zero Vendor Lock-In, 3-Tier SRE Fallback & Deterministic Verification",
                tailored_reframe_hook=(
                    "Single-vendor LLM wrappers expose your P99 latency and gross margin to supplier "
                    "pricing power; our 3-tier fallback circuit guarantees clean-sheet degradation."
                ),
                proof_metric_to_lead_with="100% Tier A/B Liskov & Hypothesis Invariant Pass Rate",
            ),
            TailoredResonanceBrief(
                stakeholder_role=StakeholderRole.MOBILIZER_CHAMPION,
                primary_value_driver="Fast Auditable Win & Internal Credibility",
                tailored_reframe_hook=(
                    "Launch a bounded Stage A proof in 14 days with a cross-vendor audited TSV decision trail "
                    "you can hand directly to your executive committee."
                ),
                proof_metric_to_lead_with="Stage A Time-to-Verified-Outcome <= 14 Days",
            ),
            TailoredResonanceBrief(
                stakeholder_role=StakeholderRole.END_USER_OPERATOR,
                primary_value_driver="Workflow Elimination (Zero Babysitting)",
                tailored_reframe_hook=(
                    "Collapses multi-step manual triage into an autonomous state machine with passive "
                    "diff learning—no annoying popup surveys."
                ),
                proof_metric_to_lead_with="Axis 1 Workflow Elimination Score >= 0.85",
            ),
        )

    def evaluate_constructive_tension(
        self,
        payload: ConstructiveTensionInput,
    ) -> ConstructiveTensionResult:
        """Pillar 3 ('Take Control of the Sale'): Push back on Build-Trap custom feature demands
        and unprincipled discounts that violate the Contribution Margin Gate.
        """
        margin_res = self._margin_gate.evaluate(payload.unit_economics_at_discounted_price)

        # 1. Evaluate discount & Give-Get rule
        untraded_discount = (
            payload.requested_discount_ratio > 0.0
            and (
                payload.customer_give_get_concession is None
                or not payload.customer_give_get_concession.strip()
            )
        )
        discount_ok = margin_res.passed and not untraded_discount

        # 2. Evaluate bespoke feature demand against Anti-Build-Trap Gate
        pushed_back_build_trap = False
        bespoke_ok = True
        if payload.bespoke_feature_demand is not None:
            bt_verdict = self._build_trap.evaluate(payload.bespoke_feature_demand)
            if not bt_verdict.approved_for_production_build:
                bespoke_ok = False
                pushed_back_build_trap = True

        # Relationship Builders cave; Challengers hold constructive tension
        if pushed_back_build_trap:
            script = (
                "Challenger Constructive Tension (Anti-Build-Trap Pushback): "
                "'We won't build that bespoke one-off feature because our data across peer deployments "
                "shows it adds maintenance complexity without moving your core cost-of-inaction metric. "
                "Let's stay focused on the core workflow that recovers your 3x ROI in 90 days.'"
            )
        elif untraded_discount:
            script = (
                "Challenger Constructive Tension (Give-Get Price Control): "
                "'Our pricing reflects the verified unit economics of the outcome. If you need a "
                f"{payload.requested_discount_ratio:.0%} price adjustment, we require a concrete Give-Get: "
                "a 24-month commitment, annual upfront billing, and a joint public case study upon Stage B graduation.'"
            )
        elif not margin_res.passed:
            script = (
                f"Challenger Margin Floor Refusal (Soup Nazi / Contribution Margin Gate): "
                f"Discounted unit economics fail our contribution margin floor ({margin_res.explanation}). "
                "We can scope to the secondary distilled tier or hold list price."
            )
        else:
            script = (
                "Constructive Control Maintained: Commercial terms preserve unit contribution margin "
                "and keep product scope 100% aligned with multi-tenant platform leverage."
            )

        return ConstructiveTensionResult(
            deal_id=payload.deal_id,
            discount_approved=discount_ok,
            bespoke_feature_approved=bespoke_ok,
            pushed_back_on_build_trap=pushed_back_build_trap,
            pushed_back_on_untraded_discount=untraded_discount,
            margin_gate_passed=margin_res.passed,
            challenger_response_script=script,
        )

    def build_jolt_playbook(self, signal: JoltIndecisionSignal) -> JoltIndecisionPlaybook:
        """Apply *The JOLT Effect* (Dixon & McKenna) to overcome customer FOMU (Fear of Messing Up)."""
        active_fears = sum(
            (
                signal.valuation_problem_option_overload,
                signal.lack_of_information_endless_poc_creep,
                signal.outcome_uncertainty_fear_of_failure,
            )
        )
        if active_fears >= 2:
            risk_level = "high_no_decision_risk"
        elif active_fears == 1:
            risk_level = "moderate"
        else:
            risk_level = "low"

        j_diag = (
            f"Customer exhibits {active_fears}/3 FOMU indecision triggers "
            f"(overload={signal.valuation_problem_option_overload}, "
            f"poc_creep={signal.lack_of_information_endless_poc_creep}, "
            f"outcome_fear={signal.outcome_uncertainty_fear_of_failure}). "
            "Do NOT dial up FOMO threats—switch to JOLT de-risking."
        )
        o_rec = (
            "Offer a Personal Recommendation: Eliminate the 4-option pricing menu; prescribe the exact "
            "Stage A/B starting configuration that fits their current volume."
        )
        l_limit = (
            "Limit the Exploration: Bound evaluation to our 10 verified golden cases and 1 live CLI "
            "harness journey (14-day timebox). Refuse open-ended 90-day science-project POCs."
        )
        t_derisk = (
            "Take Risk Off the Table: Include an explicit 6-month re-pricing retro-audit clause, "
            "3-tier SRE clean-sheet fallback SLA, and a Stage A Bayesian exit ramp if target outcome lift isn't met."
        )

        return JoltIndecisionPlaybook(
            deal_id=signal.deal_id,
            fomu_risk_level=risk_level,
            j_judge_diagnosis=j_diag,
            o_offer_recommendation=o_rec,
            l_limit_exploration=l_limit,
            t_take_risk_off_table=t_derisk,
        )

    def qualify_deal(self, payload: DealQualificationInput) -> DealQualificationResult:
        """Evaluate an enterprise deal across Challenger Choreography, Committee Tailoring,
        Constructive Tension, Margin Guard, and the JOLT Effect.
        """
        choreo_res = self._choreography.evaluate(payload.choreography)
        tension_res = self.evaluate_constructive_tension(payload.tension)
        jolt_pb = self.build_jolt_playbook(payload.jolt_signal)
        briefs = self.tailor_for_committee(payload.choreography)

        net_acv = payload.tension.list_annual_price_usd * (
            1.0 - payload.tension.requested_discount_ratio
        )

        if not payload.has_verified_mobilizer or not tension_res.margin_gate_passed:
            verdict = DealHealthVerdict.DISQUALIFY_UNPROFITABLE_OR_NO_MOBILIZER
            win_prob = 0.0
        elif (
            tension_res.pushed_back_on_build_trap
            or tension_res.pushed_back_on_untraded_discount
        ):
            verdict = DealHealthVerdict.PUSH_BACK_CONSTRUCTIVE_TENSION
            win_prob = 0.45
        elif not choreo_res.valid_choreography or jolt_pb.fomu_risk_level == "high_no_decision_risk":
            verdict = DealHealthVerdict.INTERVENE_WITH_JOLT_AND_REFRAME
            win_prob = 0.35
        else:
            verdict = DealHealthVerdict.ADVANCE_HIGH_VELOCITY
            win_prob = 0.75

        return DealQualificationResult(
            deal_id=payload.deal_id,
            verdict=verdict,
            choreography_result=choreo_res,
            tension_result=tension_res,
            jolt_playbook=jolt_pb,
            tailored_stakeholder_briefs=briefs,
            weighted_pipeline_ev_usd=round(net_acv * win_prob, 2),
        )
