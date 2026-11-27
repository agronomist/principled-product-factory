r"""Continuous Customer Learning & Adaptation Flywheel (`platform/discovery/adaptation_flywheel.py`).

Closes the three missing feedback loops between live customer behavior, GTM sales objections,
and autonomous product evolution (Teresa Torres *Continuous Discovery Habits*, Eric Ries
*Validated Learning*, and Reinforcement Learning from Implicit Human Feedback):

1. **Correction-Diff Clustering -> Auto-Synthesized Golden Cases & Foreman Work Items**:
   - Instead of letting `user_correction_diff` tuples sit passively in `IdempotentLearningLogger`,
     `CorrectionDiffClusterer` groups recurring customer edits by `(field_name, before_val -> after_val)`.
   - Once a correction pattern crosses `min_occurrences_to_adapt` (default 3 independent customers/runs),
     it automatically compiles a deterministic `SynthesizedAdaptationRule` and a `WorkItemIntake`
     ready for `ForemanOrchestrator` so the product adapts to how customers actually work.

2. **Emergent Demand & Sales Objection Accumulator ($N=1$ Build Trap -> $N=3$ Stage A Probe -> $N=10$ Stage B Build)**:
   - When *one* prospect asks for a bespoke capability in `ChallengerPipelineEngine`, it is rightly
     blocked as a Build Trap ($N=1$).
   - However, instead of throwing that signal away, `DemandSignalAccumulator` records every
     unique `(topic_slug, customer_account_id)` along with observed pain severity, workaround
     friction, and commitment tier.
   - As independent customer evidence accumulates:
     * $N < 3$: Remains `QUARANTINED_NOISE_OR_ONE_OFF` (protected against the Build Trap).
     * $3 \le N < 10$ (with $\ge \text{Stage A commitment}$): Automatically unlocks
       `PROMOTED_TO_STAGE_A_DISCOVERY_PROBE` and emits a valid `CustomerEvidenceArtifact`.
     * $N \ge 10$ (with $\ge \text{Stage B commitment}$ and Ulwick Opportunity Score $\ge 10.0$):
       Automatically graduates to `GRADUATED_TO_STAGE_B_PRODUCTION_BUILD` and dispatches to Foreman.

3. **Bayesian Customer JTBD Belief Updater (Closing the Post-Ship Loop)**:
   - Updates our prior beliefs on customer Importance and Satisfaction using real post-ship
     behavioral telemetry (`realized_adoption_rate`, `workaround_frequency`, `repeat_usage_retention`).
   - Ensures the roadmap continuously adapts to *what customers actually do*, not what we
     guessed 6 months ago.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from platform.discovery.build_trap_guard import (
    BuildTrapGate,
    BuildTrapVerdict,
    CommitmentTier,
    CustomerEvidenceArtifact,
    JTBDOpportunityInput,
    compute_ulwick_opportunity_score,
)
from platform.telemetry.learning_signal import IdempotentLearningLogger, LearningSignalRecord


# ---------------------------------------------------------------------------
# 1. Correction-Diff Clustering -> Auto-Synthesized Adaptation Work Items
# ---------------------------------------------------------------------------


class CorrectionPatternCluster(BaseModel):
    """A recurring pattern of implicit user edits (`user_correction_diff`) across independent runs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pattern_signature: str = Field(..., min_length=1)
    field_name: str = Field(..., min_length=1)
    system_default_value: str = Field(..., min_length=1)
    customer_preferred_value: str = Field(..., min_length=1)
    occurrence_count: int = Field(..., ge=1)
    distinct_workflow_runs: tuple[str, ...] = Field(...)
    ready_for_product_adaptation: bool = Field(...)


class SynthesizedForemanBrief(BaseModel):
    """Immutable work-item brief synthesized by the flywheel for `ForemanOrchestrator`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    requester_name: str = Field(default="customer-adaptation-flywheel", min_length=1)
    customer_evidence: CustomerEvidenceArtifact = Field(...)


class SynthesizedAdaptationWorkItem(BaseModel):
    """Autonomous product adaptation work item generated when a correction cluster crosses threshold."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    cluster: CorrectionPatternCluster = Field(...)
    recommended_rule_update: str = Field(..., min_length=1)
    synthesized_golden_assertion: dict[str, Any] = Field(...)
    foreman_work_item: SynthesizedForemanBrief = Field(...)


class CorrectionDiffClusterer:
    """Watches `IdempotentLearningLogger` and turns repeated customer edits into actionable
    product adaptations and new golden evaluation cases.
    """

    def __init__(self, min_occurrences_to_adapt: int = 3) -> None:
        if min_occurrences_to_adapt < 2:
            raise ValueError("min_occurrences_to_adapt must be >= 2.")
        self._min_occurrences = min_occurrences_to_adapt

    def analyze_ledger(
        self,
        logger: IdempotentLearningLogger,
    ) -> tuple[CorrectionPatternCluster, ...]:
        """Group all non-empty `user_correction_diff` entries in `logger` into clusters."""
        records: tuple[LearningSignalRecord, ...] = logger.snapshot_ledger()
        grouped: dict[tuple[str, str, str], list[str]] = {}

        for rec in records:
            diff_map = rec.signal.user_correction_diff
            if not diff_map:
                continue
            for field_name, delta in diff_map.items():
                if not isinstance(delta, dict):
                    continue
                before_str = str(delta.get("before", ""))
                after_str = str(delta.get("after", ""))
                key = (field_name, before_str, after_str)
                run_id = rec.signal.workflow_run_id
                runs = grouped.setdefault(key, [])
                if run_id not in runs:
                    runs.append(run_id)

        clusters: list[CorrectionPatternCluster] = []
        for (field_name, before_str, after_str), run_ids in sorted(
            grouped.items(),
            key=lambda item: (-len(item[1]), item[0]),
        ):
            count = len(run_ids)
            sig = f"{field_name}:{before_str}->{after_str}"
            clusters.append(
                CorrectionPatternCluster(
                    pattern_signature=sig,
                    field_name=field_name,
                    system_default_value=before_str,
                    customer_preferred_value=after_str,
                    occurrence_count=count,
                    distinct_workflow_runs=tuple(run_ids),
                    ready_for_product_adaptation=(count >= self._min_occurrences),
                )
            )
        return tuple(clusters)

    def synthesize_adaptations(
        self,
        logger: IdempotentLearningLogger,
    ) -> tuple[SynthesizedAdaptationWorkItem, ...]:
        """Generate Foreman work items and golden test assertions for every cluster >= threshold."""
        clusters = self.analyze_ledger(logger)
        adaptations: list[SynthesizedAdaptationWorkItem] = []

        for cluster in clusters:
            if not cluster.ready_for_product_adaptation:
                continue

            rule_desc = (
                f"Update default decision policy on '{cluster.field_name}': "
                f"{cluster.occurrence_count} independent customer runs overrode "
                f"'{cluster.system_default_value}' -> '{cluster.customer_preferred_value}'."
            )
            golden_assertion = {
                "field_name": cluster.field_name,
                "previous_expected": cluster.system_default_value,
                "adapted_expected": cluster.customer_preferred_value,
                "supporting_runs": list(cluster.distinct_workflow_runs),
            }
            evidence_artifact = CustomerEvidenceArtifact(
                proposal_id=f"adapt-{cluster.field_name}-{cluster.occurrence_count}",
                lifecycle_stage="Stage_A" if cluster.occurrence_count < 10 else "Stage_B",
                jtbd=JTBDOpportunityInput(
                    customer_segment="Active Production Users Emitting Correction Diffs",
                    struggling_moment=(
                        f"When system outputs '{cluster.system_default_value}' on '{cluster.field_name}', "
                        "forcing manual customer override"
                    ),
                    desired_customer_outcome=(
                        f"Receive '{cluster.customer_preferred_value}' autonomously without manual editing"
                    ),
                    importance_score=9.0,
                    current_satisfaction_score=3.0,
                ),
                commitment_tier=(
                    CommitmentTier.TIME_COMMITMENT
                    if cluster.occurrence_count < 10
                    else CommitmentTier.FINANCIAL_OR_PAIN_COMMITMENT
                ),
                verified_customer_count=cluster.occurrence_count,
                evidence_pointers=cluster.distinct_workflow_runs,
                falsifiable_outcome_metric=f"override_rate_on_{cluster.field_name}",
                baseline_metric_value=1.0,
                target_metric_value=0.05,
            )

            work_item = SynthesizedForemanBrief(
                item_id=f"flywheel-adapt-{cluster.field_name}",
                title=f"Adapt '{cluster.field_name}' policy from passive customer correction diffs",
                body=rule_desc,
                requester_name="customer-adaptation-flywheel",
                customer_evidence=evidence_artifact,
            )
            adaptations.append(
                SynthesizedAdaptationWorkItem(
                    cluster=cluster,
                    recommended_rule_update=rule_desc,
                    synthesized_golden_assertion=golden_assertion,
                    foreman_work_item=work_item,
                )
            )
        return tuple(adaptations)


# ---------------------------------------------------------------------------
# 2. Emergent Demand & Sales Objection Accumulator ($N=1$ -> $N=3$ -> $N=10$)
# ---------------------------------------------------------------------------


class CustomerPainSignal(BaseModel):
    """A single customer pain observation from a sales objection, support ticket, or product workaround."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    topic_slug: str = Field(..., min_length=3, pattern=r"^[a-z0-9-]+$")
    customer_account_id: str = Field(..., min_length=1)
    customer_segment: str = Field(..., min_length=3)
    struggling_moment: str = Field(..., min_length=10)
    desired_outcome: str = Field(..., min_length=10)
    reported_importance: float = Field(..., ge=1.0, le=10.0)
    reported_satisfaction: float = Field(..., ge=1.0, le=10.0)
    commitment_tier: CommitmentTier = Field(...)
    evidence_pointer: str = Field(..., min_length=1)


class DemandGraduationStatus(str, Enum):
    """Lifecycle graduation states for accumulated customer demand signals."""

    QUARANTINED_NOISE_OR_ONE_OFF = "quarantined_noise_or_one_off"  # N < 3 or speculative -> Build Trap shield active
    PROMOTED_TO_STAGE_A_DISCOVERY_PROBE = "promoted_to_stage_a_discovery_probe"  # 3 <= N < 10 with skin-in-the-game
    GRADUATED_TO_STAGE_B_PRODUCTION_BUILD = "graduated_to_stage_b_production_build"  # N >= 10 with high JTBD & commitment


class AccumulatedOpportunityStatus(BaseModel):
    """Current graduation state of a customer problem topic in `DemandSignalAccumulator`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    topic_slug: str = Field(..., min_length=3)
    distinct_customer_count: int = Field(..., ge=1)
    mean_importance: float = Field(..., ge=1.0, le=10.0)
    mean_satisfaction: float = Field(..., ge=1.0, le=10.0)
    ulwick_opportunity_score: float = Field(..., ge=1.0, le=19.0)
    highest_commitment_tier: CommitmentTier = Field(...)
    graduation_status: DemandGraduationStatus = Field(...)
    synthesized_evidence_artifact: CustomerEvidenceArtifact | None = Field(default=None)
    build_trap_verdict: BuildTrapVerdict | None = Field(default=None)


class DemandSignalAccumulator:
    r"""Turns individual rejected sales requests and customer workarounds into an adaptive
    discovery pipeline:

    - Blocks $N=1$ or $N=2$ requests so a single loud prospect cannot hijack the roadmap.
    - The moment $N=3$ independent customers exhibit the same struggling moment with real
      skin-in-the-game (`>= TIME_COMMITMENT`) and an Ulwick Opportunity Score $\ge 10.0$,
      it automatically promotes the topic to **Stage A Discovery Probe**.
    - Once $N \ge 10$ independent customers commit `>= REPUTATION_COMMITMENT` or
      `FINANCIAL_OR_PAIN_COMMITMENT`, it graduates the topic to **Stage B Production Build**.
    """

    def __init__(
        self,
        stage_a_threshold: int = 3,
        stage_b_threshold: int = 10,
        min_opportunity_score: float = 10.0,
        sqlite_store: Any | None = None,
    ) -> None:
        if stage_a_threshold < 2 or stage_b_threshold <= stage_a_threshold:
            raise ValueError("Require 2 <= stage_a_threshold < stage_b_threshold.")
        self._stage_a_min = stage_a_threshold
        self._stage_b_min = stage_b_threshold
        self._min_opp = min_opportunity_score
        self._signals_by_topic: dict[str, dict[str, CustomerPainSignal]] = {}
        self._gate = BuildTrapGate(min_opportunity_score=min_opportunity_score)
        self._sqlite_store = sqlite_store

    def ingest_signal(self, signal: CustomerPainSignal) -> AccumulatedOpportunityStatus:
        """Ingest a customer pain/objection signal (deduplicated per `customer_account_id`) and evaluate graduation."""
        if self._sqlite_store is not None:
            self._sqlite_store.upsert_demand_signal(
                topic_slug=signal.topic_slug,
                customer_account_id=signal.customer_account_id,
                commitment_rank=signal.commitment_tier.evidence_rank,
                payload_dict=signal.model_dump(mode="json"),
            )
            # Rehydrate topic map from SQLite so multi-process updates are reflected immediately
            persisted_rows = self._sqlite_store.list_demand_signals_for_topic(signal.topic_slug)
            self._signals_by_topic[signal.topic_slug] = {
                row.customer_account_id: CustomerPainSignal.model_validate_json(row.payload_json)
                for row in persisted_rows
            }
        else:
            topic_map = self._signals_by_topic.setdefault(signal.topic_slug, {})
            existing = topic_map.get(signal.customer_account_id)
            if (
                existing is None
                or signal.commitment_tier.evidence_rank >= existing.commitment_tier.evidence_rank
            ):
                topic_map[signal.customer_account_id] = signal

        return self.evaluate_topic(signal.topic_slug)

    def evaluate_topic(self, topic_slug: str) -> AccumulatedOpportunityStatus:
        """Compute current customer count, Ulwick score, and Stage A/B graduation status for `topic_slug`."""
        if self._sqlite_store is not None and topic_slug not in self._signals_by_topic:
            persisted_rows = self._sqlite_store.list_demand_signals_for_topic(topic_slug)
            if persisted_rows:
                self._signals_by_topic[topic_slug] = {
                    row.customer_account_id: CustomerPainSignal.model_validate_json(row.payload_json)
                    for row in persisted_rows
                }
        topic_map = self._signals_by_topic.get(topic_slug)
        if not topic_map:
            raise KeyError(f"Unknown topic_slug: {topic_slug!r}")

        signals = list(topic_map.values())
        n_customers = len(signals)
        mean_imp = round(sum(s.reported_importance for s in signals) / n_customers, 4)
        mean_sat = round(sum(s.reported_satisfaction for s in signals) / n_customers, 4)
        opp_score = compute_ulwick_opportunity_score(mean_imp, mean_sat)

        # Count only signals with real skin-in-the-game (>= TIME_COMMITMENT)
        committed_signals = [
            s
            for s in signals
            if s.commitment_tier.evidence_rank >= CommitmentTier.TIME_COMMITMENT.evidence_rank
        ]
        high_committed_signals = [
            s
            for s in signals
            if s.commitment_tier.evidence_rank >= CommitmentTier.REPUTATION_COMMITMENT.evidence_rank
        ]

        highest_tier = max(signals, key=lambda s: s.commitment_tier.evidence_rank).commitment_tier
        representative = signals[-1]

        if (
            len(high_committed_signals) >= self._stage_b_min
            and opp_score >= self._min_opp
        ):
            stage = "Stage_B"
            grad_status = DemandGraduationStatus.GRADUATED_TO_STAGE_B_PRODUCTION_BUILD
            effective_tier = max(
                high_committed_signals,
                key=lambda s: s.commitment_tier.evidence_rank,
            ).commitment_tier
        elif (
            len(committed_signals) >= self._stage_a_min
            and opp_score >= self._min_opp
        ):
            stage = "Stage_A"
            grad_status = DemandGraduationStatus.PROMOTED_TO_STAGE_A_DISCOVERY_PROBE
            effective_tier = CommitmentTier.TIME_COMMITMENT
        else:
            stage = "Stage_A"
            grad_status = DemandGraduationStatus.QUARANTINED_NOISE_OR_ONE_OFF
            effective_tier = highest_tier

        artifact = CustomerEvidenceArtifact(
            proposal_id=f"emergent-{topic_slug}",
            lifecycle_stage=stage,
            jtbd=JTBDOpportunityInput(
                customer_segment=representative.customer_segment,
                struggling_moment=representative.struggling_moment,
                desired_customer_outcome=representative.desired_outcome,
                importance_score=mean_imp,
                current_satisfaction_score=mean_sat,
            ),
            commitment_tier=effective_tier,
            verified_customer_count=n_customers,
            evidence_pointers=tuple(s.evidence_pointer for s in signals),
            falsifiable_outcome_metric=f"{topic_slug}_completion_rate",
            baseline_metric_value=0.10,
            target_metric_value=0.80,
        )
        verdict = self._gate.evaluate(artifact)

        return AccumulatedOpportunityStatus(
            topic_slug=topic_slug,
            distinct_customer_count=n_customers,
            mean_importance=mean_imp,
            mean_satisfaction=mean_sat,
            ulwick_opportunity_score=opp_score,
            highest_commitment_tier=highest_tier,
            graduation_status=grad_status,
            synthesized_evidence_artifact=artifact,
            build_trap_verdict=verdict,
        )


# ---------------------------------------------------------------------------
# 3. Bayesian Customer JTBD Belief Updater (Real-Time Roadmap Adaptation)
# ---------------------------------------------------------------------------


class CustomerBehaviorObservation(BaseModel):
    """Live telemetry observation of how customers interact with a workflow or workaround."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    topic_slug: str = Field(..., min_length=3)
    prior_importance: float = Field(..., ge=1.0, le=10.0)
    prior_satisfaction: float = Field(..., ge=1.0, le=10.0)
    prior_weight: float = Field(
        default=5.0,
        gt=0.0,
        description="Effective sample size (pseudo-count weight) of the prior survey/belief.",
    )
    observed_customer_sample_size: int = Field(..., gt=0)
    observed_workaround_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraction of users building manual workarounds (CSV exports, scripts, retries) for this job.",
    )
    observed_task_drop_off_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraction of users failing or abandoning the current workflow step.",
    )


class UpdatedJTBDBelief(BaseModel):
    """Posterior JTBD Importance, Satisfaction, and Ulwick Opportunity Score after observing real behavior."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    topic_slug: str = Field(..., min_length=3)
    prior_opportunity_score: float = Field(..., ge=1.0, le=19.0)
    posterior_importance: float = Field(..., ge=1.0, le=10.0)
    posterior_satisfaction: float = Field(..., ge=1.0, le=10.0)
    posterior_opportunity_score: float = Field(..., ge=1.0, le=19.0)
    opportunity_delta: float = Field(...)
    priority_escalated: bool = Field(
        ...,
        description="True when behavioral evidence pushes an underestimated job above the >= 10.0 opportunity threshold.",
    )


class BayesianJTBDBeliefUpdater:
    r"""Updates our JTBD Importance and Satisfaction estimates using empirical customer behavior
    (workaround rates and task drop-off rates) via conjugate normal-mean shrinkage:

    - High `observed_workaround_rate` is empirical proof of **high customer importance**
      (customers don't spend hours building manual spreadsheet workarounds for a job they don't care about):
      $$I_{\text{emp}} = 1.0 + 9.0 \cdot \text{observed\_workaround\_rate}$$
    - High `observed_task_drop_off_rate` is empirical proof of **low current satisfaction**:
      $$S_{\text{emp}} = 10.0 - 9.0 \cdot \text{observed\_task\_drop\_off\_rate}$$
    - Posterior beliefs combine prior survey estimates with empirical behavioral telemetry weighted
      by sample size $N$:
      $$\theta_{\text{post}} = \frac{w_0 \cdot \theta_{\text{prior}} + N \cdot \theta_{\text{emp}}}{w_0 + N}$$
    """

    def update_beliefs(self, obs: CustomerBehaviorObservation) -> UpdatedJTBDBelief:
        prior_opp = compute_ulwick_opportunity_score(
            obs.prior_importance, obs.prior_satisfaction
        )

        emp_importance = 1.0 + 9.0 * obs.observed_workaround_rate
        emp_satisfaction = 10.0 - 9.0 * obs.observed_task_drop_off_rate

        total_weight = obs.prior_weight + float(obs.observed_customer_sample_size)
        post_imp = round(
            (obs.prior_weight * obs.prior_importance + obs.observed_customer_sample_size * emp_importance)
            / total_weight,
            4,
        )
        post_sat = round(
            (obs.prior_weight * obs.prior_satisfaction + obs.observed_customer_sample_size * emp_satisfaction)
            / total_weight,
            4,
        )
        post_imp = max(1.0, min(10.0, post_imp))
        post_sat = max(1.0, min(10.0, post_sat))

        post_opp = compute_ulwick_opportunity_score(post_imp, post_sat)
        delta = round(post_opp - prior_opp, 4)
        escalated = (prior_opp < 10.0) and (post_opp >= 10.0)

        return UpdatedJTBDBelief(
            topic_slug=obs.topic_slug,
            prior_opportunity_score=prior_opp,
            posterior_importance=post_imp,
            posterior_satisfaction=post_sat,
            posterior_opportunity_score=post_opp,
            opportunity_delta=delta,
            priority_escalated=escalated,
        )
