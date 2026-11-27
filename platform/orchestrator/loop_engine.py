"""Dynamic Loops, Arena Bakeoffs, Premise-Attacking Tracker, and Just-in-Time Workflow Synthesis.

Implements pstack's dynamic execution primitives (`figure-it-out`, `hillclimb`, `arena`,
`principle-attack-the-premise`, and `principle-sequence-verifiable-units`) on top of
`principled-product-factory`:

1. `PremiseTracker` (`principle-attack-the-premise`):
   Tracks failed fixes per evaluation gate. When 2 distinct fixes sharing an underlying
   premise fail the same gate, halts further fix attempts (`PremiseBlockedError`) until
   the shared premise is explicitly stated and tested directly via `record_premise_probe`.
2. `ScientificHillclimbLoop` (`figure-it-out` Phase C & `hillclimb`):
   Executes verifiable atomic brackets:
   `capture_baseline -> apply_hypothesis_mutation -> verify_predicate_and_margin -> keep_or_revert`.
   Every iteration logs an append-only row to `DecisionTrailLogger` (`/show-me-your-work`).
   `INCONCLUSIVE` or margin-failing mutations are reverted immediately.
3. `ArenaExecutor` (`/arena` for `parallel_fan_out`):
   Runs $N$ candidate generators in isolated output workspaces (`principle-separate-before-serializing-shared-state`),
   scores them via a cross-vendor judge against a hidden rubric, picks the cleanest base,
   and grafts the strongest elements from runner-up candidates into the base.
4. `DynamicWorkflowSynthesizer` (`/figure-it-out` Phase A & B):
   Synthesizes a typed `DAGWorkflowSpec` at runtime ordered by Information-Gain-per-Dollar
   ($\text{EVOI} / \text{Cost}$, riskiest-unknown-first), automatically inserting harness
   doctor/baseline steps before implementation nodes.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from platform.audit.decision_trail import DecisionOutcome, DecisionTrailLogger
from platform.orchestrator.dag_runner import WIP_LIMIT, DAGNodeSpec, DAGWorkflowSpec

TState = TypeVar("TState")
TArtifact = TypeVar("TArtifact")


class PremiseBlockedError(RuntimeError):
    """Raised when two fixes sharing a premise have failed the same gate and the premise has not been tested."""


class PremiseProbeRecord(BaseModel):
    """Immutable record of testing an underlying premise after 2 failed fixes on a gate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    gate_id: str = Field(..., min_length=1)
    stated_premise: str = Field(..., min_length=1)
    probe_observation: str = Field(..., min_length=1)
    premise_falsified: bool = Field(...)


class PremiseTracker:
    """Enforces `principle-attack-the-premise`:

    When two or more fixes that share one premise fail the same gate, blocks further fix
    attempts on that gate until the premise is written down and directly tested.
    """

    def __init__(self, failure_limit_before_premise_attack: int = 2) -> None:
        if failure_limit_before_premise_attack < 2:
            raise ValueError("failure_limit_before_premise_attack must be >= 2.")
        self._limit = failure_limit_before_premise_attack
        self._gate_failures: dict[str, list[str]] = {}
        self._probes: dict[str, list[PremiseProbeRecord]] = {}

    def consecutive_failures(self, gate_id: str) -> int:
        return len(self._gate_failures.get(gate_id, []))

    def is_premise_attack_required(self, gate_id: str) -> bool:
        return self.consecutive_failures(gate_id) >= self._limit

    def assert_can_attempt_fix(self, gate_id: str) -> None:
        """Raise `PremiseBlockedError` if >= 2 fixes failed `gate_id` without a premise probe."""
        if self.is_premise_attack_required(gate_id):
            failed_summaries = self._gate_failures[gate_id]
            raise PremiseBlockedError(
                f"principle-attack-the-premise triggered on gate '{gate_id}': "
                f"{len(failed_summaries)} fixes failed the same gate ({failed_summaries}). "
                "Stop writing fixes that assume the same premise—call record_premise_probe() first."
            )

    def record_fix_outcome(
        self,
        gate_id: str,
        fix_description: str,
        *,
        passed: bool,
    ) -> None:
        """Record a fix attempt on `gate_id` after verifying `assert_can_attempt_fix`."""
        self.assert_can_attempt_fix(gate_id)
        if passed:
            self._gate_failures[gate_id] = []
        else:
            self._gate_failures.setdefault(gate_id, []).append(fix_description)

    def record_premise_probe(
        self,
        *,
        gate_id: str,
        stated_premise: str,
        probe_fn: Callable[[], tuple[bool, str]],
    ) -> PremiseProbeRecord:
        """Execute a direct observation testing `stated_premise` and clear the premise block."""
        if not stated_premise.strip():
            raise ValueError("stated_premise must be non-empty.")
        falsified, observation = probe_fn()
        record = PremiseProbeRecord(
            gate_id=gate_id,
            stated_premise=stated_premise.strip(),
            probe_observation=observation.strip(),
            premise_falsified=falsified,
        )
        self._probes.setdefault(gate_id, []).append(record)
        # Reset consecutive fix counter now that the premise has been explicitly tested
        self._gate_failures[gate_id] = []
        return record


class LoopVerdict(str, Enum):
    """Falsifiable predicate evaluation verdicts (`figure-it-out` Phase C)."""

    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    INCONCLUSIVE = "INCONCLUSIVE"


class HypothesisProposal(BaseModel, Generic[TState]):
    """A single atomic experiment proposed in a `ScientificHillclimbLoop`."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    iteration_id: str = Field(..., min_length=1)
    hypothesis: str = Field(..., min_length=1)
    target_gate_id: str = Field(default="primary_predicate", min_length=1)
    evidence_pointer: str = Field(..., min_length=1)
    mutate_fn: Callable[[TState], TState]
    premise_probe: Callable[[], tuple[bool, str]] | None = None
    stated_premise_if_blocked: str | None = None


class HillclimbIterationRecord(BaseModel):
    """Immutable audit record of one bracketed iteration in `ScientificHillclimbLoop`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    iteration_id: str = Field(..., min_length=1)
    hypothesis: str = Field(..., min_length=1)
    baseline_score: float = Field(...)
    candidate_score: float = Field(...)
    verdict: LoopVerdict = Field(...)
    kept: bool = Field(...)
    reverted: bool = Field(...)
    premise_probed: bool = Field(default=False)


class HillclimbRunResult(BaseModel, Generic[TState]):
    """Immutable postcondition result returned by `ScientificHillclimbLoop.run`."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    initial_score: float = Field(...)
    final_score: float = Field(...)
    final_state: TState = Field(...)
    goal_achieved: bool = Field(...)
    kept_iterations: tuple[str, ...] = Field(...)
    reverted_iterations: tuple[str, ...] = Field(...)
    history: tuple[HillclimbIterationRecord, ...] = Field(...)


class ScientificHillclimbLoop(Generic[TState]):
    """Implements pstack's `figure-it-out` Phase C and `hillclimb` loop:

    - Brackets every unit: `known-good baseline -> 1 hypothesis mutation -> measure predicate -> keep or revert`.
    - Never advances on `INCONCLUSIVE` or regression (`candidate_score <= current_score`).
    - Integrates `PremiseTracker` (`principle-attack-the-premise`) so 2 failed mutations on the
      same gate force a premise probe before further mutations.
    - Logs every decision to `DecisionTrailLogger` (`/show-me-your-work`).
    """

    def __init__(
        self,
        evaluator_fn: Callable[[TState], tuple[float, LoopVerdict]],
        trail_logger: DecisionTrailLogger,
        target_score: float = 0.90,
        premise_tracker: PremiseTracker | None = None,
    ) -> None:
        self._evaluator = evaluator_fn
        self._trail = trail_logger
        self._target_score = target_score
        self._premise_tracker = premise_tracker or PremiseTracker()

    @property
    def premise_tracker(self) -> PremiseTracker:
        return self._premise_tracker

    def run(
        self,
        initial_state: TState,
        proposals: Sequence[HypothesisProposal[TState]],
    ) -> HillclimbRunResult[TState]:
        """Run the scientific hypothesis loop across `proposals` until `target_score` is reached."""
        current_state = copy.deepcopy(initial_state)
        current_score, init_verdict = self._evaluator(current_state)
        initial_score = current_score

        self._trail.append_decision(
            phase="frame",
            decision=f"Captured pre-change baseline score={initial_score:.4f} (target={self._target_score:.4f})",
            why="Verify old value vs new value on real artifact before mutating state",
            evidence=proposals[0].evidence_pointer if proposals else "run-baseline",
            result=init_verdict.value,
        )

        kept_ids: list[str] = []
        reverted_ids: list[str] = []
        history: list[HillclimbIterationRecord] = []

        for prop in proposals:
            if current_score >= self._target_score:
                break

            premise_probed = False
            if self._premise_tracker.is_premise_attack_required(prop.target_gate_id):
                if prop.premise_probe is not None and prop.stated_premise_if_blocked:
                    probe_rec = self._premise_tracker.record_premise_probe(
                        gate_id=prop.target_gate_id,
                        stated_premise=prop.stated_premise_if_blocked,
                        probe_fn=prop.premise_probe,
                    )
                    premise_probed = True
                    self._trail.append_decision(
                        phase="attack-premise",
                        decision=f"Tested shared premise on '{prop.target_gate_id}': {probe_rec.stated_premise}",
                        why="Two prior fixes failed the same gate; tested premise directly before next fix",
                        evidence=prop.evidence_pointer,
                        result="VERIFIED" if probe_rec.premise_falsified else "NOT_VERIFIED",
                    )
                else:
                    # Will raise PremiseBlockedError
                    self._premise_tracker.assert_can_attempt_fix(prop.target_gate_id)

            snapshot_before = copy.deepcopy(current_state)
            baseline_before = current_score

            candidate_state = prop.mutate_fn(copy.deepcopy(current_state))
            candidate_score, verdict = self._evaluator(candidate_state)

            improved = (
                verdict == LoopVerdict.VERIFIED
                and (candidate_score > baseline_before + 1e-9)
            )

            if improved:
                self._premise_tracker.record_fix_outcome(
                    prop.target_gate_id, prop.hypothesis, passed=True
                )
                current_state = candidate_state
                current_score = candidate_score
                kept_ids.append(prop.iteration_id)
                self._trail.append_decision(
                    phase=f"loop-{prop.iteration_id}",
                    decision=f"KEPT {prop.hypothesis} ({baseline_before:.4f} -> {candidate_score:.4f})",
                    why="Mutation advanced falsifiable metric and passed verification gate",
                    evidence=prop.evidence_pointer,
                    result=DecisionOutcome.TESTS_GREEN,
                )
                history.append(
                    HillclimbIterationRecord(
                        iteration_id=prop.iteration_id,
                        hypothesis=prop.hypothesis,
                        baseline_score=baseline_before,
                        candidate_score=candidate_score,
                        verdict=verdict,
                        kept=True,
                        reverted=False,
                        premise_probed=premise_probed,
                    )
                )
            else:
                self._premise_tracker.record_fix_outcome(
                    prop.target_gate_id, prop.hypothesis, passed=False
                )
                # Hard revert to known-good bracket snapshot
                current_state = snapshot_before
                current_score = baseline_before
                reverted_ids.append(prop.iteration_id)
                self._trail.append_decision(
                    phase=f"loop-{prop.iteration_id}",
                    decision=f"REVERTED {prop.hypothesis} (candidate={candidate_score:.4f} vs baseline={baseline_before:.4f})",
                    why=f"Verdict was {verdict.value}; reverted to known-good bracket immediately",
                    evidence=prop.evidence_pointer,
                    result=DecisionOutcome.REVERTED,
                )
                history.append(
                    HillclimbIterationRecord(
                        iteration_id=prop.iteration_id,
                        hypothesis=prop.hypothesis,
                        baseline_score=baseline_before,
                        candidate_score=candidate_score,
                        verdict=verdict,
                        kept=False,
                        reverted=True,
                        premise_probed=premise_probed,
                    )
                )

        return HillclimbRunResult[TState](
            initial_score=initial_score,
            final_score=current_score,
            final_state=current_state,
            goal_achieved=(current_score >= self._target_score),
            kept_iterations=tuple(kept_ids),
            reverted_iterations=tuple(reverted_ids),
            history=tuple(history),
        )


# ---------------------------------------------------------------------------
# Arena Bakeoff Executor (`/arena`: Frame -> Fan Out -> Cross-Judge -> Pick -> Graft -> Verify)
# ---------------------------------------------------------------------------


class ArenaCandidateSpec(BaseModel, Generic[TArtifact]):
    """Specification for an isolated candidate runner in an `/arena` tournament."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    candidate_id: str = Field(..., min_length=1)
    model_slug: str = Field(..., min_length=1)
    generator_fn: Callable[[Path], TArtifact]
    strengths_tags: tuple[str, ...] = Field(default_factory=tuple)


class ArenaRubricScore(BaseModel):
    """Per-candidate criterion scores assigned by the cross-vendor judge."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_id: str = Field(..., min_length=1)
    model_slug: str = Field(..., min_length=1)
    isolated_workspace: str = Field(..., min_length=1)
    criterion_scores: dict[str, float] = Field(...)
    total_score: float = Field(...)
    api_surface_size: int = Field(
        default=1,
        ge=1,
        description="Smaller surface wins ties under Laziness Protocol.",
    )


class ArenaSynthesisResult(BaseModel, Generic[TArtifact]):
    """Immutable output from `ArenaExecutor.run_tournament`."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    synthesized_artifact: TArtifact = Field(...)
    winning_base_candidate_id: str = Field(..., min_length=1)
    judge_model_slug: str = Field(..., min_length=1)
    cross_vendor_judge_enforced: bool = Field(...)
    grafted_features: tuple[str, ...] = Field(...)
    candidate_scores: tuple[ArenaRubricScore, ...] = Field(...)
    verified: bool = Field(...)


class ArenaExecutor(Generic[TArtifact]):
    """Implements pstack's `/arena` skill:

    1. **Frame & Isolate**: Provisions a dedicated workspace directory (`worktree/candidate-<id>`)
       for each candidate (`principle-separate-before-serializing-shared-state`).
    2. **Fan Out**: Runs all $N$ candidates against the same prompt contract.
    3. **Cross-Judge**: Scores every candidate criterion-by-criterion using a judge model
       whose vendor family differs from the primary parent vendor.
    4. **Pick Base**: Picks the highest-scoring candidate (breaking ties via `principle-laziness-protocol`
       by choosing the smaller API surface).
    5. **Graft**: Folds the top unique strengths from losing candidates into the winning base.
    6. **Verify**: Runs a deterministic verification predicate on the grafted artifact.
    """

    def __init__(
        self,
        rubric_evaluators: Mapping[str, Callable[[TArtifact], float]],
        graft_fn: Callable[[TArtifact, Sequence[tuple[str, TArtifact]]], tuple[TArtifact, tuple[str, ...]]],
        verify_fn: Callable[[TArtifact], bool],
        parent_model_slug: str = "claude-opus-5-5-xhigh-fast",
        judge_model_slug: str = "gemini-4-neon-xhigh",
        surface_size_fn: Callable[[TArtifact], int] | None = None,
    ) -> None:
        if not (3 <= len(rubric_evaluators) <= 6):
            raise ValueError("Arena rubric requires 3 to 6 concrete gradeable criteria.")
        self._rubric = dict(rubric_evaluators)
        self._graft_fn = graft_fn
        self._verify_fn = verify_fn
        self._parent_model = parent_model_slug
        self._judge_model = judge_model_slug
        self._surface_fn = surface_size_fn or (lambda _: 1)

    def run_tournament(
        self,
        candidates: Sequence[ArenaCandidateSpec[TArtifact]],
        arena_root_dir: Path,
    ) -> ArenaSynthesisResult[TArtifact]:
        """Run the 6-phase `/arena` bakeoff and return the grafted, verified artifact."""
        if len(candidates) < 2:
            raise ValueError("Arena requires at least 2 candidates.")

        parent_vendor = self._parent_model.split("-", maxsplit=1)[0].lower()
        judge_vendor = self._judge_model.split("-", maxsplit=1)[0].lower()
        cross_vendor_ok = parent_vendor != judge_vendor
        if not cross_vendor_ok:
            raise ValueError(
                f"Arena cross-judge violation: judge ({self._judge_model}) cannot share vendor "
                f"with parent ({self._parent_model})."
            )

        artifacts_by_id: dict[str, TArtifact] = {}
        scores: list[ArenaRubricScore] = []

        # Phase B & C: Isolated Fan-Out + Criterion-by-Criterion Cross-Judge Scoring
        for cand in candidates:
            cand_dir = arena_root_dir / f"candidate-{cand.candidate_id}"
            cand_dir.mkdir(parents=True, exist_ok=True)
            artifact = cand.generator_fn(cand_dir)
            artifacts_by_id[cand.candidate_id] = artifact

            crit_scores: dict[str, float] = {}
            for crit_name, crit_fn in self._rubric.items():
                crit_scores[crit_name] = round(float(crit_fn(artifact)), 4)

            total = round(sum(crit_scores.values()) / len(crit_scores), 4)
            surface = self._surface_fn(artifact)
            scores.append(
                ArenaRubricScore(
                    candidate_id=cand.candidate_id,
                    model_slug=cand.model_slug,
                    isolated_workspace=str(cand_dir),
                    criterion_scores=crit_scores,
                    total_score=total,
                    api_surface_size=surface,
                )
            )

        # Phase D: Pick Base (highest total_score; ties broken by smaller api_surface_size per Laziness Protocol)
        ranked = sorted(
            scores,
            key=lambda s: (-s.total_score, s.api_surface_size, s.candidate_id),
        )
        winner_score = ranked[0]
        base_artifact = artifacts_by_id[winner_score.candidate_id]

        # Phase E: Graft strongest features from losing candidates into base
        losers: list[tuple[str, TArtifact]] = [
            (s.candidate_id, artifacts_by_id[s.candidate_id])
            for s in ranked[1:]
        ]
        synthesized, grafted_notes = self._graft_fn(base_artifact, losers)

        # Phase F: Verify synthesized artifact
        verified = self._verify_fn(synthesized)
        if not verified:
            raise RuntimeError("Arena Phase F verification failed on synthesized artifact.")

        return ArenaSynthesisResult[TArtifact](
            synthesized_artifact=synthesized,
            winning_base_candidate_id=winner_score.candidate_id,
            judge_model_slug=self._judge_model,
            cross_vendor_judge_enforced=cross_vendor_ok,
            grafted_features=tuple(grafted_notes),
            candidate_scores=tuple(ranked),
            verified=verified,
        )


# ---------------------------------------------------------------------------
# Just-in-Time Workflow Synthesizer (`/figure-it-out` Phase A & B)
# ---------------------------------------------------------------------------


class SynthesizedTaskNodeInput(BaseModel):
    """Candidate task step to be compiled into a dynamic DAG ordered by riskiest-unknown-first."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    node_id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    skill_ref: str = Field(..., min_length=1)
    compensating_action: str = Field(..., min_length=1)
    evoi_usd: float = Field(..., ge=0.0, description="Expected Value of Information in USD.")
    estimated_cost_usd: float = Field(..., gt=0.0, description="Expected execution cost in USD.")
    failure_probability: float = Field(..., ge=0.0, le=1.0)
    is_harness_verification: bool = Field(default=False)

    @property
    def risk_adjusted_info_density(self) -> float:
        r"""Compute riskiest-unknown-first priority score: $(\text{EVOI} \times (1 + P_{\text{fail}})) / \text{Cost}$."""
        return (self.evoi_usd * (1.0 + self.failure_probability)) / self.estimated_cost_usd


class DynamicWorkflowSynthesizer:
    """Synthesizes a `DAGWorkflowSpec` at runtime following `/figure-it-out` Phase B:

    1. Places verification harness / baseline capture nodes FIRST (`principle-foundational-thinking`).
    2. Orders exploratory/implementation nodes by **Riskiest-Unknown-First**
       (highest `risk_adjusted_info_density` first, so cheap high-EVOI falsification probes
       run before expensive buildout steps).
    3. Wires sequential dependencies and Saga compensating actions automatically.
    """

    def synthesize(
        self,
        workflow_id: str,
        lifecycle_stage: str,
        candidate_steps: Sequence[SynthesizedTaskNodeInput],
    ) -> DAGWorkflowSpec:
        if not candidate_steps:
            raise ValueError("candidate_steps cannot be empty.")

        # Separate harness/scaffold nodes (must run first) from domain steps
        harness_steps = [s for s in candidate_steps if s.is_harness_verification]
        domain_steps = [s for s in candidate_steps if not s.is_harness_verification]

        # Sort domain steps by risk_adjusted_info_density descending (riskiest-unknown-first)
        sorted_domain = sorted(
            domain_steps,
            key=lambda s: (-s.risk_adjusted_info_density, s.node_id),
        )
        ordered_inputs = list(harness_steps) + sorted_domain

        dag_nodes: list[DAGNodeSpec] = []
        prev_node_id: str | None = None
        for step in ordered_inputs:
            deps = (prev_node_id,) if prev_node_id is not None else ()
            dag_nodes.append(
                DAGNodeSpec(
                    node_id=step.node_id,
                    description=step.description,
                    dependencies=deps,
                    skill_ref=step.skill_ref,
                    compensating_action=step.compensating_action,
                )
            )
            prev_node_id = step.node_id

        return DAGWorkflowSpec(
            workflow_id=workflow_id,
            lifecycle_stage=lifecycle_stage,
            wip_limit=WIP_LIMIT,
            nodes=tuple(dag_nodes),
        )
