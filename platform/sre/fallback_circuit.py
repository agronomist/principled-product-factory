"""SRE Circuit Breaker, 3-Tier Graceful Degradation Router, and Automated BlamelessPostMortem Generator.

Implements the reliability invariants of `principled-product-builder-v10`:
1. 3-Tier Graceful Degradation Hierarchy:
   `primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`
   (Soccer metaphor: when the #10 playmaker is double-marked, cycle through the #8 box-to-box
   midfielder or clear safely to the sweeper keeper; Seinfeld metaphor: Jerry's backup routine).
2. Circuit Breaker State Machine (`CLOSED -> OPEN -> HALF_OPEN -> CLOSED`):
   Tracks per-tier failure streaks and automatically opens the circuit on repeated failures.
3. Shewhart +/- 3-Sigma Statistical Process Control Monitor & `BlamelessPostMortem`:
   Converts SEV incidents or Shewhart +/- 3-sigma breaches into minimized, deterministic
   regression JSON fixtures ready for Tier A/B verification.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping
from enum import Enum
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

TPayload = TypeVar("TPayload")
TResult = TypeVar("TResult")


class TierExhaustedError(RuntimeError):
    """Raised when all three SRE fallback tiers fail or have open circuit breakers."""


class FallbackTier(str, Enum):
    """Canonical 3-tier graceful degradation chain."""

    PRIMARY_FRONTIER_MODEL = "primary_frontier_model"
    SECONDARY_DISTILLED_MODEL = "secondary_distilled_model"
    TERTIARY_CACHED_DETERMINISTIC = "tertiary_cached_deterministic"

    @classmethod
    def ordered_chain(cls) -> tuple[FallbackTier, FallbackTier, FallbackTier]:
        return (
            cls.PRIMARY_FRONTIER_MODEL,
            cls.SECONDARY_DISTILLED_MODEL,
            cls.TERTIARY_CACHED_DETERMINISTIC,
        )


class CircuitState(str, Enum):
    """Standard circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerConfig(BaseModel):
    """Immutable configuration for `FallbackCircuit`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    failure_threshold: int = Field(
        default=2,
        ge=1,
        description="Consecutive failures before a tier's circuit trips from CLOSED to OPEN.",
    )
    recovery_timeout_seconds: float = Field(
        default=30.0,
        gt=0.0,
        description="Seconds before an OPEN circuit transitions to HALF_OPEN for a probe.",
    )
    shewhart_sigma_limit: float = Field(
        default=3.0,
        gt=0.0,
        description="Shewhart control chart sigma multiplier (canonical: 3.0).",
    )


class FallbackExecutionResult(BaseModel, Generic[TResult]):
    """Immutable postcondition contract emitted by `FallbackCircuit.execute`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    selected_tier: FallbackTier = Field(...)
    output: TResult = Field(...)
    attempted_tiers: tuple[FallbackTier, ...] = Field(...)
    degraded: bool = Field(
        ...,
        description="True if execution fell back from primary_frontier_model to secondary or tertiary.",
    )
    tier_errors: dict[str, str] = Field(default_factory=dict)
    metaphor_summary: str = Field(..., min_length=1)


class _TierHealthState:
    """Private Parnas-encapsulated mutable state for a single tier's circuit breaker."""

    def __init__(self) -> None:
        self.state: CircuitState = CircuitState.CLOSED
        self.consecutive_failures: int = 0
        self.opened_at_timestamp: float | None = None


class FallbackCircuit(Generic[TPayload, TResult]):
    """Circuit breaker and 3-tier graceful degradation router:
    `primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`

    Guarantees Liskov preconditions (all three canonical tiers registered) and postconditions
    (output comes from the highest healthy tier in the chain, and failed tiers increment
    their failure counters or trip to `CircuitState.OPEN`).
    """

    def __init__(
        self,
        handlers: Mapping[FallbackTier, Callable[[TPayload], TResult]],
        config: CircuitBreakerConfig | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._config = config or CircuitBreakerConfig()
        self._clock = clock or (lambda: 0.0)
        missing = [t for t in FallbackTier.ordered_chain() if t not in handlers]
        if missing:
            raise ValueError(f"FallbackCircuit requires all 3 canonical tiers; missing: {missing}")
        self._handlers: dict[FallbackTier, Callable[[TPayload], TResult]] = dict(handlers)
        self._health: dict[FallbackTier, _TierHealthState] = {
            tier: _TierHealthState() for tier in FallbackTier.ordered_chain()
        }

    def tier_state(self, tier: FallbackTier) -> CircuitState:
        """Inspect current circuit breaker state for a tier without exposing internal mutable state."""
        health = self._health[tier]
        if health.state == CircuitState.OPEN and health.opened_at_timestamp is not None:
            elapsed = self._clock() - health.opened_at_timestamp
            if elapsed >= self._config.recovery_timeout_seconds:
                health.state = CircuitState.HALF_OPEN
        return health.state

    def consecutive_failures(self, tier: FallbackTier) -> int:
        """Return consecutive failure count for a given tier."""
        return self._health[tier].consecutive_failures

    def force_trip(self, tier: FallbackTier) -> None:
        """Explicitly open a tier's circuit breaker (e.g., via external health check or kill-switch)."""
        health = self._health[tier]
        health.state = CircuitState.OPEN
        health.consecutive_failures = max(
            health.consecutive_failures, self._config.failure_threshold
        )
        health.opened_at_timestamp = self._clock()

    def reset_tier(self, tier: FallbackTier) -> None:
        """Reset a tier's circuit breaker back to CLOSED."""
        health = self._health[tier]
        health.state = CircuitState.CLOSED
        health.consecutive_failures = 0
        health.opened_at_timestamp = None

    def _record_success(self, tier: FallbackTier) -> None:
        self.reset_tier(tier)

    def _record_failure(self, tier: FallbackTier) -> None:
        health = self._health[tier]
        health.consecutive_failures += 1
        if (
            health.state == CircuitState.HALF_OPEN
            or health.consecutive_failures >= self._config.failure_threshold
        ):
            health.state = CircuitState.OPEN
            health.opened_at_timestamp = self._clock()

    def execute(
        self,
        payload: TPayload,
        *,
        start_tier: FallbackTier = FallbackTier.PRIMARY_FRONTIER_MODEL,
    ) -> FallbackExecutionResult[TResult]:
        """Execute `payload` starting at `start_tier` and degrading gracefully across the chain."""
        full_chain = FallbackTier.ordered_chain()
        start_idx = full_chain.index(start_tier)
        candidate_tiers = full_chain[start_idx:]

        attempted: list[FallbackTier] = []
        tier_errors: dict[str, str] = {}

        for tier in candidate_tiers:
            current_state = self.tier_state(tier)
            if current_state == CircuitState.OPEN:
                tier_errors[tier.value] = "CircuitState.OPEN (fast-fail)"
                continue

            attempted.append(tier)
            handler = self._handlers[tier]
            try:
                output = handler(payload)
                self._record_success(tier)
                degraded = tier != FallbackTier.PRIMARY_FRONTIER_MODEL
                if tier == FallbackTier.PRIMARY_FRONTIER_MODEL:
                    metaphor = (
                        "Primary playmaker (#10 frontier model) completed the through-ball cleanly."
                    )
                elif tier == FallbackTier.SECONDARY_DISTILLED_MODEL:
                    metaphor = (
                        "Playmaker double-marked; pivoted cleanly through the #8 box-to-box midfielder "
                        "(secondary_distilled_model)."
                    )
                else:
                    metaphor = (
                        "High press forced a safe back-pass to the sweeper keeper / Jerry's proven backup "
                        "routine (tertiary_cached_deterministic) to preserve a clean sheet."
                    )

                result = FallbackExecutionResult[TResult](
                    selected_tier=tier,
                    output=output,
                    attempted_tiers=tuple(attempted),
                    degraded=degraded,
                    tier_errors=tier_errors,
                    metaphor_summary=metaphor,
                )
                self._validate_postconditions(result, candidate_tiers)
                return result
            except Exception as exc:  # noqa: BLE001
                self._record_failure(tier)
                tier_errors[tier.value] = f"{type(exc).__name__}: {exc}"

        raise TierExhaustedError(
            f"All available SRE fallback tiers exhausted. Errors: {json.dumps(tier_errors, sort_keys=True)}"
        )

    def _validate_postconditions(
        self,
        result: FallbackExecutionResult[TResult],
        candidate_tiers: tuple[FallbackTier, ...],
    ) -> None:
        if result.selected_tier not in candidate_tiers:
            raise RuntimeError("Postcondition breach: selected_tier was not in candidate_tiers.")
        if (result.selected_tier != FallbackTier.PRIMARY_FRONTIER_MODEL) != result.degraded:
            raise RuntimeError("Postcondition breach: degraded flag inconsistent with selected_tier.")


class ShewhartMonitor(BaseModel):
    """Shewhart +/- 3-Sigma Statistical Process Control Evaluator."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_name: str = Field(..., min_length=1)
    baseline_mean: float = Field(...)
    baseline_std: float = Field(..., gt=0.0)
    sigma_multiplier: float = Field(default=3.0, gt=0.0)

    @property
    def upper_control_limit(self) -> float:
        return self.baseline_mean + (self.sigma_multiplier * self.baseline_std)

    @property
    def lower_control_limit(self) -> float:
        return self.baseline_mean - (self.sigma_multiplier * self.baseline_std)

    def compute_z_score(self, observed_value: float) -> float:
        if not math.isfinite(observed_value):
            raise ValueError("observed_value must be finite.")
        return (observed_value - self.baseline_mean) / self.baseline_std

    def is_breach(self, observed_value: float) -> bool:
        """Return True if `observed_value` lies outside `[mean - 3*sigma, mean + 3*sigma]`."""
        return abs(self.compute_z_score(observed_value)) > (self.sigma_multiplier + 1e-12)


class IncidentEvent(BaseModel):
    """Input contract representing a SEV incident or a Shewhart +/- 3-sigma breach."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    incident_id: str = Field(..., min_length=1)
    severity: str = Field(
        default="SEV-2",
        pattern=r"^(SEV-[123]|SHEWHART_3SIGMA)$",
        description="Severity classification: SEV-1, SEV-2, SEV-3, or SHEWHART_3SIGMA.",
    )
    product_id: str = Field(default="demo-decision-engine", min_length=1)
    node_id: str = Field(..., min_length=1)
    metric_name: str = Field(default="latency_ms", min_length=1)
    observed_value: float = Field(...)
    baseline_mean: float = Field(default=100.0)
    baseline_std: float = Field(default=15.0, gt=0.0)
    sigma_limit: float = Field(default=3.0, gt=0.0)
    raw_input_payload: dict[str, Any] = Field(
        ...,
        description="Raw payload present when the incident or 3-sigma excursion occurred.",
    )
    failure_exception_type: str = Field(default="ShewhartControlLimitBreach", min_length=1)
    failure_message: str = Field(..., min_length=1)
    expected_safe_fallback_tier: FallbackTier = Field(
        default=FallbackTier.TERTIARY_CACHED_DETERMINISTIC
    )

    @model_validator(mode="after")
    def _validate_finite_metrics(self) -> IncidentEvent:
        for name in ("observed_value", "baseline_mean", "baseline_std", "sigma_limit"):
            if not math.isfinite(getattr(self, name)):
                raise ValueError(f"{name} must be finite.")
        return self


class RegressionFixture(BaseModel):
    """Minimized, deterministic regression JSON fixture generated by `BlamelessPostMortem`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    fixture_id: str = Field(..., min_length=1)
    incident_id: str = Field(..., min_length=1)
    severity: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    node_id: str = Field(..., min_length=1)
    error_signature_sha256: str = Field(..., min_length=64, max_length=64)
    shewhart_z_score: float = Field(...)
    is_three_sigma_breach: bool = Field(...)
    minimized_input_payload: dict[str, Any] = Field(...)
    expected_invariant_assertion: dict[str, Any] = Field(...)
    blameless_root_cause_summary: str = Field(..., min_length=1)

    def to_deterministic_json(self) -> str:
        """Serialize the regression fixture to canonical sorted-key JSON."""
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2)


class BlamelessPostMortem:
    """Automated generator converting SEV incidents or Shewhart +/- 3-sigma breaches
    into minimized, deterministic JSON regression fixtures.

    Implements payload delta-minimization: strips noisy metadata, volatile timestamps,
    and large debug blobs while preserving minimal failure-inducing fields.
    """

    _VOLATILE_NOISE_KEYS: frozenset[str] = frozenset(
        {
            "debug_trace",
            "raw_html_dump",
            "ephemeral_session_token",
            "timestamp_ns",
            "unstructured_log_blob",
            "_internal_scratch",
        }
    )

    def __init__(self, max_string_length: int = 120) -> None:
        if max_string_length < 16:
            raise ValueError("max_string_length must be >= 16.")
        self._max_str_len = max_string_length

    def minimize_payload(self, raw_payload: dict[str, Any]) -> dict[str, Any]:
        """Deterministically shrink `raw_payload` to its minimal failure-reproducing core."""
        minimized: dict[str, Any] = {}
        for key in sorted(raw_payload.keys()):
            if key in self._VOLATILE_NOISE_KEYS or key.startswith("_debug"):
                continue
            val = raw_payload[key]
            if isinstance(val, str) and len(val) > self._max_str_len:
                minimized[key] = val[: self._max_str_len]
            elif isinstance(val, list) and len(val) > 5:
                minimized[key] = val[:5]
            elif isinstance(val, dict):
                nested = self.minimize_payload(val)
                if nested:
                    minimized[key] = nested
            else:
                minimized[key] = val
        # Guarantee at least one key survives even if input had only volatile keys
        if not minimized and raw_payload:
            first_key = sorted(raw_payload.keys())[0]
            minimized[first_key] = raw_payload[first_key]
        return minimized

    def generate_fixture(
        self,
        incident: IncidentEvent,
        output_path: Path | None = None,
    ) -> RegressionFixture:
        """Compile an `IncidentEvent` (SEV or Shewhart +/- 3-sigma breach) into a `RegressionFixture`."""
        monitor = ShewhartMonitor(
            metric_name=incident.metric_name,
            baseline_mean=incident.baseline_mean,
            baseline_std=incident.baseline_std,
            sigma_multiplier=incident.sigma_limit,
        )
        z_score = monitor.compute_z_score(incident.observed_value)
        is_breach = monitor.is_breach(incident.observed_value)

        if not is_breach and not incident.severity.startswith("SEV-"):
            raise ValueError(
                f"Event {incident.incident_id} is neither a SEV incident nor a "
                f"+/- {incident.sigma_limit}-sigma breach (z={z_score:.2f})."
            )

        minimized_payload = self.minimize_payload(incident.raw_input_payload)
        sig_material = f"{incident.node_id}|{incident.failure_exception_type}|{incident.failure_message.strip()}"
        error_sig = hashlib.sha256(sig_material.encode("utf-8")).hexdigest()
        fixture_id = f"reg-{incident.incident_id}-{error_sig[:12]}"

        expected_assertion = {
            "must_not_raise": incident.failure_exception_type,
            "required_fallback_tier": incident.expected_safe_fallback_tier.value,
            "metric_upper_control_limit": round(monitor.upper_control_limit, 4),
            "metric_lower_control_limit": round(monitor.lower_control_limit, 4),
        }

        summary = (
            f"Blameless post-mortem for {incident.incident_id} ({incident.severity}) on node "
            f"'{incident.node_id}': metric '{incident.metric_name}' observed={incident.observed_value:.2f} "
            f"(z={z_score:+.2f} sigma vs baseline {incident.baseline_mean:.2f}+/-{incident.baseline_std:.2f}). "
            f"Compiled into minimized regression fixture '{fixture_id}' enforcing graceful fallback to "
            f"'{incident.expected_safe_fallback_tier.value}'."
        )

        fixture = RegressionFixture(
            fixture_id=fixture_id,
            incident_id=incident.incident_id,
            severity=incident.severity,
            product_id=incident.product_id,
            node_id=incident.node_id,
            error_signature_sha256=error_sig,
            shewhart_z_score=round(z_score, 4),
            is_three_sigma_breach=is_breach,
            minimized_input_payload=minimized_payload,
            expected_invariant_assertion=expected_assertion,
            blameless_root_cause_summary=summary,
        )

        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(fixture.to_deterministic_json(), encoding="utf-8")

        return fixture
