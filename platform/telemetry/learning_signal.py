"""Idempotent learning signal logger and 4-Axis AI-Native Prioritization Scorecard.

Implements two foundational components of `principled-product-builder-v10`:
1. Zero-friction idempotent event logger capturing:
   `(input_state, system_output, user_correction_diff, verified_outcome)` tuples.
   Deduplicates replays deterministically via canonical SHA-256 content addressing.
2. 4-Axis AI-Native Prioritization Filter evaluating:
   - Axis 1: Workflow Elimination (`workflow_elimination`)
   - Axis 2: Flywheel Velocity (`flywheel_velocity`)
   - Axis 3: Deterministic Verifiability (`deterministic_verifiability`)
   - Axis 4: Unit Margin Resilience (`unit_margin_resilience`)
   Blocks "AI bolt-on theater" where EVOI <= 0 or deterministic rules suffice.

Design Contracts:
- Liskov Substitution Principle (LSP): `validate_preconditions` and `validate_postconditions`
  guarantee idempotency and monotonic ledger size.
- Parnas Information Hiding: Internal deduplication index (`_store`) is private and only
  accessible as immutable Pydantic v2 snapshots.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


def compute_correction_diff(
    system_output: dict[str, Any],
    user_final_state: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Compute a zero-friction structural diff between `system_output` and `user_final_state`.

    If `user_final_state` is None or identical to `system_output`, returns an empty dict
    (indicating zero user edits required—implicit positive flywheel signal).
    """
    if user_final_state is None:
        return {}
    diff: dict[str, dict[str, Any]] = {}
    all_keys = sorted(set(system_output.keys()) | set(user_final_state.keys()))
    for key in all_keys:
        sys_val = system_output.get(key)
        usr_val = user_final_state.get(key)
        if sys_val != usr_val:
            diff[key] = {"before": sys_val, "after": usr_val}
    return diff


class AINativeScorecardInput(BaseModel):
    """Input contract for the 4-Axis AI-Native Prioritization Filter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_id: str = Field(..., min_length=1)
    workflow_elimination: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Axis 1 [0, 1]: Collapses multi-step human drudgery into autonomous completion.",
    )
    flywheel_velocity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Axis 2 [0, 1]: Passively captures user_correction_diff tuples during normal usage.",
    )
    deterministic_verifiability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Axis 3 [0, 1]: Output is verifiable via Liskov postconditions or kappa >= 0.80 judges.",
    )
    unit_margin_resilience: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Axis 4 [0, 1]: Survives worst-case token/HITL costs and distills cleanly.",
    )
    evoi: float = Field(
        default=0.10,
        description="Expected Value of Information (USD or utility net of cost). Must be > 0.",
    )
    deterministic_rule_suffices: bool = Field(
        default=False,
        description="True if a simple SQL query, regex, or deterministic rule engine solves the job.",
    )
    min_axis_threshold: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        description="Minimum required score on every individual axis.",
    )
    min_composite_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum required arithmetic mean across all 4 axes.",
    )


class AINativeScorecardEvaluation(BaseModel):
    """Immutable evaluation result from the 4-Axis AI-Native Prioritization Filter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_id: str = Field(..., min_length=1)
    composite_score: float = Field(..., ge=0.0, le=1.0)
    min_axis_score: float = Field(..., ge=0.0, le=1.0)
    is_ai_bolt_on_theater: bool = Field(...)
    approved: bool = Field(...)
    blocking_reasons: tuple[str, ...] = Field(default_factory=tuple)
    verdict_metaphor: str = Field(..., min_length=1)


class AINativeScorecardValidator:
    """Enforces the 4-Axis AI-Native Prioritization Filter and blocks AI bolt-on theater."""

    def validate_preconditions(self, payload: AINativeScorecardInput) -> None:
        for field_name in (
            "workflow_elimination",
            "flywheel_velocity",
            "deterministic_verifiability",
            "unit_margin_resilience",
            "evoi",
        ):
            val = getattr(payload, field_name)
            if not math.isfinite(val):
                raise ValueError(f"Precondition failed: {field_name} must be finite.")

    def evaluate(self, payload: AINativeScorecardInput) -> AINativeScorecardEvaluation:
        self.validate_preconditions(payload)

        axes = (
            payload.workflow_elimination,
            payload.flywheel_velocity,
            payload.deterministic_verifiability,
            payload.unit_margin_resilience,
        )
        composite = sum(axes) / 4.0
        min_axis = min(axes)
        reasons: list[str] = []

        if payload.evoi <= 0.0:
            reasons.append(f"EVOI <= 0 ({payload.evoi:.4f}): purchasing model inference yields zero decision gain.")
        if payload.deterministic_rule_suffices:
            reasons.append(
                "Deterministic rule suffices: using an LLM here is AI bolt-on theater (doing step-overs in your own penalty box)."
            )
        if (min_axis + 1e-12) < payload.min_axis_threshold:
            reasons.append(
                f"Minimum axis score {min_axis:.2f} falls below threshold {payload.min_axis_threshold:.2f}."
            )
        if (composite + 1e-12) < payload.min_composite_threshold:
            reasons.append(
                f"Composite 4-axis score {composite:.2f} falls below threshold {payload.min_composite_threshold:.2f}."
            )

        is_theater = (
            payload.evoi <= 0.0
            or payload.deterministic_rule_suffices
            or len(reasons) > 0
        )
        approved = not is_theater

        if approved:
            metaphor = (
                "Total Football Attack: High EVOI workflow elimination with passive flywheel telemetry "
                "and resilient unit margin."
            )
        else:
            metaphor = (
                "Blocked (The Urban Sombrero / Penalty-Box Step-Overs): Rejecting AI bolt-on theater "
                "in favor of deterministic rules or higher-EVOI bets."
            )

        result = AINativeScorecardEvaluation(
            feature_id=payload.feature_id,
            composite_score=composite,
            min_axis_score=min_axis,
            is_ai_bolt_on_theater=is_theater,
            approved=approved,
            blocking_reasons=tuple(reasons),
            verdict_metaphor=metaphor,
        )
        self.validate_postconditions(payload, result)
        return result

    def validate_postconditions(
        self, payload: AINativeScorecardInput, result: AINativeScorecardEvaluation
    ) -> None:
        if (payload.evoi <= 0.0 or payload.deterministic_rule_suffices) and result.approved:
            raise RuntimeError("Postcondition breach: AI bolt-on theater must never be approved.")
        if result.approved == result.is_ai_bolt_on_theater:
            raise RuntimeError("Postcondition breach: approved and is_ai_bolt_on_theater must be complements.")


class LearningSignalTuple(BaseModel):
    """Canonical zero-friction 4-tuple:
    `(input_state, system_output, user_correction_diff, verified_outcome)`
    plus optional AI-Native Scorecard metadata.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    product_id: str = Field(default="demo-decision-engine", min_length=1)
    workflow_run_id: str = Field(..., min_length=1)
    input_state: dict[str, Any] = Field(
        ...,
        description="Normalized domain input state observed by the skill.",
    )
    system_output: dict[str, Any] = Field(
        ...,
        description="Structured output emitted by the system prior to any user edit.",
    )
    user_correction_diff: dict[str, Any] = Field(
        default_factory=dict,
        description="Zero-friction passive delta between system_output and user final state.",
    )
    verified_outcome: dict[str, Any] = Field(
        ...,
        description="Ground-truth postcondition or downstream settlement verification.",
    )
    scorecard: AINativeScorecardInput | None = Field(
        default=None,
        description="Optional 4-axis AI-native prioritization scorecard input.",
    )

    @model_validator(mode="after")
    def _validate_non_empty_states(self) -> LearningSignalTuple:
        if not self.input_state:
            raise ValueError("input_state cannot be empty.")
        if not self.system_output:
            raise ValueError("system_output cannot be empty.")
        if not self.verified_outcome:
            raise ValueError("verified_outcome cannot be empty.")
        return self

    def as_four_tuple(
        self,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Return the exact `(input_state, system_output, user_correction_diff, verified_outcome)` tuple."""
        return (
            self.input_state,
            self.system_output,
            self.user_correction_diff,
            self.verified_outcome,
        )

    def compute_idempotency_key(self) -> str:
        """Compute deterministic SHA-256 hash over the canonical JSON representation of the 4-tuple."""
        canonical_payload = {
            "product_id": self.product_id,
            "workflow_run_id": self.workflow_run_id,
            "input_state": self.input_state,
            "system_output": self.system_output,
            "user_correction_diff": self.user_correction_diff,
            "verified_outcome": self.verified_outcome,
        }
        serialized = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class LearningSignalRecord(BaseModel):
    """Immutable persisted record produced by `IdempotentLearningLogger`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    idempotency_key: str = Field(..., min_length=64, max_length=64)
    recorded_at_utc: str = Field(..., min_length=1)
    signal: LearningSignalTuple = Field(...)
    implicit_acceptance: bool = Field(
        ...,
        description="True when user_correction_diff is empty (zero edits needed).",
    )
    scorecard_evaluation: AINativeScorecardEvaluation | None = Field(default=None)
    was_deduplicated_replay: bool = Field(default=False)


class IdempotentLearningLogger:
    r"""Parnas-encapsulated idempotent event logger for passive flywheel learning tuples.

    Guarantees that logging the same `LearningSignalTuple` $N \ge 1$ times amid network retries
    or crash-recovery loops produces exact idempotency: the ledger stores exactly one entry
    and returns the original record with `was_deduplicated_replay=True` on subsequent calls.

    When initialized with `sqlite_store: SQLiteWALStore`, all events are durably persisted
    in ACID SQLite WAL transactions so deduplication and ledger state survive process restarts.
    """

    def __init__(self, sqlite_store: Any | None = None) -> None:
        self._records_by_key: dict[str, LearningSignalRecord] = {}
        self._scorecard_validator = AINativeScorecardValidator()
        self._sqlite_store = sqlite_store
        if self._sqlite_store is not None:
            for row in self._sqlite_store.list_learning_signals():
                loaded = LearningSignalRecord.model_validate_json(row.payload_json)
                self._records_by_key[row.idempotency_key] = loaded

    def validate_preconditions(self, signal: LearningSignalTuple) -> None:
        if not signal.input_state or not signal.system_output or not signal.verified_outcome:
            raise ValueError("Precondition failed: learning signal tuple contains empty components.")

    def log_event(self, signal: LearningSignalTuple) -> LearningSignalRecord:
        """Idempotently record a `(input_state, system_output, user_correction_diff, verified_outcome)` tuple."""
        self.validate_preconditions(signal)
        prior_count = len(self._records_by_key)
        key = signal.compute_idempotency_key()

        if key in self._records_by_key:
            existing = self._records_by_key[key]
            replay_record = existing.model_copy(update={"was_deduplicated_replay": True})
            self.validate_postconditions(signal, replay_record, prior_count, is_replay=True)
            return replay_record

        scorecard_eval = (
            self._scorecard_validator.evaluate(signal.scorecard)
            if signal.scorecard is not None
            else None
        )

        record = LearningSignalRecord(
            idempotency_key=key,
            recorded_at_utc=datetime.now(timezone.utc).isoformat(),
            signal=signal,
            implicit_acceptance=(len(signal.user_correction_diff) == 0),
            scorecard_evaluation=scorecard_eval,
            was_deduplicated_replay=False,
        )

        if self._sqlite_store is not None:
            stored_row, was_replay = self._sqlite_store.insert_or_get_learning_signal(
                idempotency_key=key,
                recorded_at_utc=record.recorded_at_utc,
                product_id=signal.product_id,
                workflow_run_id=signal.workflow_run_id,
                payload_dict=record.model_dump(mode="json"),
            )
            if was_replay:
                persisted = LearningSignalRecord.model_validate_json(stored_row.payload_json)
                self._records_by_key[key] = persisted
                replay_rec = persisted.model_copy(update={"was_deduplicated_replay": True})
                return replay_rec

        self._records_by_key[key] = record
        self.validate_postconditions(signal, record, prior_count, is_replay=False)
        return record

    def validate_postconditions(
        self,
        signal: LearningSignalTuple,
        record: LearningSignalRecord,
        prior_count: int,
        *,
        is_replay: bool,
    ) -> None:
        current_count = len(self._records_by_key)
        if is_replay and current_count != prior_count:
            raise RuntimeError("Postcondition breach: idempotent replay mutated ledger size.")
        if not is_replay and current_count != prior_count + 1:
            raise RuntimeError("Postcondition breach: new event failed to increment ledger size by 1.")
        if record.signal.as_four_tuple() != signal.as_four_tuple():
            raise RuntimeError("Postcondition breach: stored 4-tuple does not match input 4-tuple.")

    @property
    def total_unique_events(self) -> int:
        """Number of unique deduplicated learning tuples in the ledger."""
        return len(self._records_by_key)

    def snapshot_ledger(self) -> tuple[LearningSignalRecord, ...]:
        """Return an immutable snapshot of all unique recorded learning events."""
        return tuple(self._records_by_key.values())
