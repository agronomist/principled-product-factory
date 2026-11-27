r"""State-Machine DAG Executor with Little's Law WIP Semaphore, Bellman Router, and SHA-256 Saga Rollbacks.

Implements the orchestration invariants of `principled-product-builder-v10`:
1. Little's Law ($L = \lambda W$) WIP Semaphore (`WIP_LIMIT = 5`):
   Bounds concurrent active workflows to 5 (Cruyff's Total Football positional spacing /
   The Soup Nazi's 5-person queue discipline).
2. Bellman-Style Complexity / Risk / Margin Router:
   Dynamically routes execution between `fast_implement` (single-path deterministic) and
   `parallel_fan_out` (multi-branch exploration) based on complexity, failure risk, EVOI,
   and unit contribution margin headroom.
3. Error-Signature SHA-256 Hashing & Saga Compensating Rollback + HITL Escalation:
   Hashes `(node_id, exception_type, normalized_message)` with SHA-256. Upon encountering a
   duplicate error signature on retry (George Costanza trying to parallel park the same
   impossible angle twice), immediately halts further retries, executes compensating actions
   in reverse topological order (Saga rollback), and generates a structured `HITLEscalationTicket`.
"""

from __future__ import annotations

import hashlib
import re
import threading
from collections.abc import Callable, Mapping
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Iterator

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

WIP_LIMIT: int = 5


class WIPLimitExceededError(RuntimeError):
    """Raised when concurrent DAG runs exceed Little's Law `WIP_LIMIT = 5`."""


class DuplicateErrorSignatureError(RuntimeError):
    """Raised when a retry produces an identical SHA-256 error signature."""


class RoutingMode(str, Enum):
    """Canonical Bellman execution routes."""

    FAST_IMPLEMENT = "fast_implement"
    PARALLEL_FAN_OUT = "parallel_fan_out"


class DAGExecutionStatus(str, Enum):
    """Terminal state-machine statuses for a DAG execution."""

    COMPLETED = "completed"
    ROLLED_BACK_AND_ESCALATED = "rolled_back_and_escalated"


def compute_error_signature_sha256(
    node_id: str,
    exc: BaseException | str,
    exc_type_name: str | None = None,
) -> str:
    """Compute a deterministic 64-char hex SHA-256 error signature.

    Normalizes volatile memory addresses (`0x...`) and whitespace so identical semantic
    failures always produce the exact same SHA-256 digest.
    """
    if isinstance(exc, BaseException):
        type_name = exc_type_name or type(exc).__name__
        raw_message = str(exc)
    else:
        type_name = exc_type_name or "RuntimeError"
        raw_message = exc

    normalized_msg = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", raw_message.strip())
    normalized_msg = re.sub(r"\s+", " ", normalized_msg)
    canonical = f"{node_id.strip()}|{type_name.strip()}|{normalized_msg}"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class BellmanStateVector(BaseModel):
    """Immutable state input for the Bellman complexity/risk/margin router."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    complexity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Task structural/domain complexity in [0.0, 1.0].",
    )
    risk: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Irreversibility / blast-radius risk in [0.0, 1.0].",
    )
    margin_headroom_usd: float = Field(
        ...,
        description="Available contribution margin headroom above min_margin in USD.",
    )
    evoi: float = Field(
        default=0.15,
        description="Expected Value of Information from parallel multi-path evaluation.",
    )


class BellmanRouteDecision(BaseModel):
    """Immutable decision emitted by `BellmanRouter`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    selected_route: RoutingMode = Field(...)
    expected_value_fast: float = Field(...)
    expected_value_fan_out: float = Field(...)
    rationale: str = Field(..., min_length=1)


class BellmanRouter:
    """Bellman optimality router choosing between `fast_implement` and `parallel_fan_out`."""

    def __init__(
        self,
        complexity_threshold: float = 0.65,
        risk_threshold: float = 0.60,
        min_margin_headroom_usd: float = 0.10,
    ) -> None:
        self._complexity_threshold = complexity_threshold
        self._risk_threshold = risk_threshold
        self._min_margin_headroom = min_margin_headroom_usd

    def route(self, state: BellmanStateVector) -> BellmanRouteDecision:
        """Compute optimal execution route via Bellman value comparison."""
        # Fast single-path utility: low cost, penalizes high complexity/risk
        v_fast = 1.0 - (0.45 * state.complexity + 0.45 * state.risk)

        # Parallel fan-out utility: mitigates complexity/risk via ensemble + EVOI, costs margin headroom
        fan_out_cost_penalty = 0.15 if state.margin_headroom_usd >= self._min_margin_headroom else 0.90
        v_fan_out = (
            0.85
            + (0.35 * state.complexity + 0.35 * state.risk + 0.50 * max(0.0, state.evoi))
            - fan_out_cost_penalty
        )

        high_uncertainty = (
            state.complexity >= self._complexity_threshold
            or state.risk >= self._risk_threshold
        )
        can_afford_fan_out = (
            state.margin_headroom_usd >= self._min_margin_headroom and state.evoi > 0.0
        )

        if high_uncertainty and can_afford_fan_out and v_fan_out >= v_fast:
            selected = RoutingMode.PARALLEL_FAN_OUT
            rationale = (
                f"Bellman router selected 'parallel_fan_out': high complexity/risk "
                f"({state.complexity:.2f}/{state.risk:.2f}) with sufficient margin headroom "
                f"(${state.margin_headroom_usd:.4f} >= ${self._min_margin_headroom:.4f}) and EVOI={state.evoi:.3f}."
            )
        else:
            selected = RoutingMode.FAST_IMPLEMENT
            rationale = (
                f"Bellman router selected 'fast_implement': single-path execution maximizes net value "
                f"(V_fast={v_fast:.3f} vs V_fan_out={v_fan_out:.3f}, headroom=${state.margin_headroom_usd:.4f})."
            )

        return BellmanRouteDecision(
            selected_route=selected,
            expected_value_fast=round(v_fast, 4),
            expected_value_fan_out=round(v_fan_out, 4),
            rationale=rationale,
        )


class DAGNodeSpec(BaseModel):
    """Typed specification for a single node in a workflow DAG."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    node_id: str = Field(..., min_length=1)
    description: str = Field(default="", description="Human-readable node purpose.")
    dependencies: tuple[str, ...] = Field(default_factory=tuple)
    skill_ref: str = Field(..., min_length=1)
    compensating_action: str = Field(..., min_length=1)
    timeout_ms: int = Field(default=2000, gt=0)
    max_retries: int = Field(default=2, ge=0)


class DAGWorkflowSpec(BaseModel):
    """Typed specification for a complete multi-node DAG workflow loaded from YAML."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str = Field(..., min_length=1)
    version: str = Field(default="10.0.0", min_length=1)
    lifecycle_stage: str = Field(default="Stage_B", pattern=r"^Stage_[ABC]$")
    wip_limit: int = Field(default=WIP_LIMIT, ge=1, le=WIP_LIMIT)
    margin_policy: dict[str, float] = Field(default_factory=dict)
    sre_fallback_chain: dict[str, Any] = Field(default_factory=dict)
    routing_policy: dict[str, Any] = Field(default_factory=dict)
    nodes: tuple[DAGNodeSpec, ...] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _validate_acyclic_topology(self) -> DAGWorkflowSpec:
        node_map = {n.node_id: n for n in self.nodes}
        if len(node_map) != len(self.nodes):
            raise ValueError("Duplicate node_id detected in DAGWorkflowSpec.")
        for node in self.nodes:
            for dep in node.dependencies:
                if dep not in node_map:
                    raise ValueError(
                        f"Node '{node.node_id}' depends on unknown node '{dep}'."
                    )
        # Verify topological sort exists (Kahn's algorithm)
        _ = self.topological_order()
        return self

    def topological_order(self) -> tuple[DAGNodeSpec, ...]:
        """Return nodes in deterministic topological execution order."""
        node_map = {n.node_id: n for n in self.nodes}
        in_degree: dict[str, int] = {n.node_id: len(n.dependencies) for n in self.nodes}
        dependents: dict[str, list[str]] = {n.node_id: [] for n in self.nodes}
        for n in self.nodes:
            for dep in n.dependencies:
                dependents[dep].append(n.node_id)

        ready = [n.node_id for n in self.nodes if in_degree[n.node_id] == 0]
        ordered: list[DAGNodeSpec] = []

        while ready:
            current_id = ready.pop(0)
            ordered.append(node_map[current_id])
            for child_id in dependents[current_id]:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    ready.append(child_id)

        if len(ordered) != len(self.nodes):
            raise ValueError("Cycle detected in DAGWorkflowSpec.")
        return tuple(ordered)

    def topological_waves(self) -> tuple[tuple[DAGNodeSpec, ...], ...]:
        """Partition DAG nodes into concurrent execution waves where all dependencies of wave $k$
        are satisfied by waves $< k$.
        """
        node_map = {n.node_id: n for n in self.nodes}
        in_degree: dict[str, int] = {n.node_id: len(n.dependencies) for n in self.nodes}
        dependents: dict[str, list[str]] = {n.node_id: [] for n in self.nodes}
        for n in self.nodes:
            for dep in n.dependencies:
                dependents[dep].append(n.node_id)

        current_wave_ids = [n.node_id for n in self.nodes if in_degree[n.node_id] == 0]
        waves: list[tuple[DAGNodeSpec, ...]] = []
        visited_count = 0

        while current_wave_ids:
            wave_specs = tuple(node_map[nid] for nid in current_wave_ids)
            waves.append(wave_specs)
            visited_count += len(wave_specs)
            next_wave_ids: list[str] = []
            for nid in current_wave_ids:
                for child_id in dependents[nid]:
                    in_degree[child_id] -= 1
                    if in_degree[child_id] == 0:
                        next_wave_ids.append(child_id)
            current_wave_ids = next_wave_ids

        if visited_count != len(self.nodes):
            raise ValueError("Cycle detected in DAGWorkflowSpec.")
        return tuple(waves)


class HITLEscalationTicket(BaseModel):
    """Structured Human-In-The-Loop escalation payload emitted after a Saga rollback."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ticket_id: str = Field(..., min_length=1)
    workflow_id: str = Field(..., min_length=1)
    failed_node_id: str = Field(..., min_length=1)
    error_signature_sha256: str = Field(..., min_length=64, max_length=64)
    duplicate_signature_halted: bool = Field(...)
    attempts_made: int = Field(..., ge=1)
    compensating_actions_executed: tuple[str, ...] = Field(...)
    error_message: str = Field(..., min_length=1)
    metaphor_explanation: str = Field(..., min_length=1)


class DAGExecutionResult(BaseModel):
    """Immutable postcondition result returned by `DAGRunner.execute`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str = Field(..., min_length=1)
    status: DAGExecutionStatus = Field(...)
    route_decision: BellmanRouteDecision = Field(...)
    completed_nodes: tuple[str, ...] = Field(...)
    compensated_nodes: tuple[str, ...] = Field(default_factory=tuple)
    compensating_actions_run: tuple[str, ...] = Field(default_factory=tuple)
    node_outputs: dict[str, Any] = Field(default_factory=dict)
    node_attempt_counts: dict[str, int] = Field(default_factory=dict)
    observed_error_signatures: tuple[str, ...] = Field(default_factory=tuple)
    hitl_ticket: HITLEscalationTicket | None = Field(default=None)


class NodeExecutionHandler(BaseModel):
    """Binds a forward execution callable and an idempotent Saga compensating callable for a node."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    forward: Callable[[dict[str, Any]], dict[str, Any]]
    compensate: Callable[[dict[str, Any]], None] | None = None


class _LittleLawWIPController:
    """Thread-safe Little's Law WIP semaphore enforcing at most `wip_limit` active runs."""

    def __init__(self, wip_limit: int = WIP_LIMIT) -> None:
        if not (1 <= wip_limit <= WIP_LIMIT):
            raise ValueError(f"wip_limit must be in [1, {WIP_LIMIT}], got {wip_limit}.")
        self._wip_limit = wip_limit
        self._lock = threading.Lock()
        self._active_count = 0
        self._peak_count = 0

    @property
    def wip_limit(self) -> int:
        return self._wip_limit

    @property
    def active_count(self) -> int:
        with self._lock:
            return self._active_count

    @property
    def peak_count(self) -> int:
        with self._lock:
            return self._peak_count

    @contextmanager
    def acquire_slot(self) -> Iterator[int]:
        """Acquire a WIP slot without blocking; raise `WIPLimitExceededError` if at capacity."""
        with self._lock:
            if self._active_count >= self._wip_limit:
                raise WIPLimitExceededError(
                    f"Little's Law WIP cap breached (Cruyff spacing / Soup Nazi queue limit): "
                    f"active_wip={self._active_count} >= WIP_LIMIT={self._wip_limit}."
                )
            self._active_count += 1
            if self._active_count > self._peak_count:
                self._peak_count = self._active_count
            current_active = self._active_count
        try:
            yield current_active
        finally:
            with self._lock:
                self._active_count -= 1


class DAGRunner:
    """State-machine DAG executor enforcing Little's Law (`WIP_LIMIT = 5`), Bellman routing,
    real `timeout_ms` deadline enforcement, parallel wave execution, and SHA-256 duplicate
    error-signature Saga rollbacks.
    """

    def __init__(
        self,
        workflow_spec: DAGWorkflowSpec,
        node_handlers: Mapping[str, NodeExecutionHandler] | None = None,
        wip_limit: int = WIP_LIMIT,
    ) -> None:
        effective_wip = min(wip_limit, workflow_spec.wip_limit, WIP_LIMIT)
        self._spec = workflow_spec
        self._wip_controller = _LittleLawWIPController(wip_limit=effective_wip)
        routing_cfg = workflow_spec.routing_policy
        self._router = BellmanRouter(
            complexity_threshold=float(routing_cfg.get("complexity_threshold", 0.65)),
            risk_threshold=float(routing_cfg.get("risk_threshold", 0.60)),
            min_margin_headroom_usd=float(routing_cfg.get("min_margin_headroom_usd", 0.10)),
        )
        self._handlers: dict[str, NodeExecutionHandler] = dict(node_handlers or {})

    @property
    def wip_limit(self) -> int:
        return self._wip_controller.wip_limit

    @property
    def active_wip(self) -> int:
        return self._wip_controller.active_count

    @property
    def peak_wip(self) -> int:
        return self._wip_controller.peak_count

    def register_node_handler(self, node_id: str, handler: NodeExecutionHandler) -> None:
        """Register or override a node execution handler and its Saga compensating callback."""
        self._handlers[node_id] = handler

    @contextmanager
    def reserve_wip_slot(self) -> Iterator[int]:
        """Public context manager for testing or reserving a Little's Law WIP slot."""
        with self._wip_controller.acquire_slot() as active:
            yield active

    @staticmethod
    def _invoke_with_timeout(
        fn: Callable[[dict[str, Any]], dict[str, Any]],
        ctx_snapshot: dict[str, Any],
        timeout_ms: int,
        node_id: str,
    ) -> dict[str, Any]:
        """Execute `fn(ctx_snapshot)` with a real wall-clock timeout (`timeout_ms`)."""
        timeout_sec = max(0.001, timeout_ms / 1000.0)
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(fn, ctx_snapshot)
        try:
            return future.result(timeout=timeout_sec)
        except FuturesTimeoutError as exc:
            pool.shutdown(wait=False, cancel_futures=True)
            raise TimeoutError(
                f"Node '{node_id}' exceeded timeout_ms={timeout_ms}ms deadline."
            ) from exc
        finally:
            pool.shutdown(wait=False)

    def _execute_single_node(
        self,
        node_spec: DAGNodeSpec,
        context_snapshot: dict[str, Any],
    ) -> tuple[bool, dict[str, Any] | None, int, list[str], Exception | None, str, bool]:
        """Run a single DAG node with `timeout_ms` enforcement and SHA-256 duplicate-error halt."""
        handler = self._handlers.get(node_spec.node_id)
        if handler is None:
            handler = NodeExecutionHandler(
                forward=lambda _ctx, nid=node_spec.node_id: {"node_id": nid, "ok": True}
            )

        seen_node_signatures: set[str] = set()
        max_attempts = 1 + node_spec.max_retries
        attempts = 0
        node_sigs: list[str] = []
        last_exc: Exception | None = None
        last_sig: str = ""
        halted_on_duplicate = False

        while attempts < max_attempts:
            attempts += 1
            try:
                out = self._invoke_with_timeout(
                    handler.forward,
                    context_snapshot,
                    node_spec.timeout_ms,
                    node_spec.node_id,
                )
                return (True, out, attempts, node_sigs, None, "", False)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                sig = compute_error_signature_sha256(node_spec.node_id, exc)
                last_sig = sig
                node_sigs.append(sig)
                if sig in seen_node_signatures:
                    halted_on_duplicate = True
                    break
                seen_node_signatures.add(sig)

        return (
            False,
            None,
            attempts,
            node_sigs,
            last_exc,
            last_sig,
            halted_on_duplicate,
        )

    def execute(
        self,
        initial_context: dict[str, Any],
        bellman_state: BellmanStateVector | None = None,
    ) -> DAGExecutionResult:
        """Execute the DAG workflow under Little's Law WIP protection, enforcing `timeout_ms`,
        parallel wave execution (when `PARALLEL_FAN_OUT` is active and a wave has $>1$ ready nodes),
        and Saga rollback guarantees.
        """
        state_vec = bellman_state or BellmanStateVector(
            complexity=float(initial_context.get("complexity", 0.35)),
            risk=float(initial_context.get("risk", 0.25)),
            margin_headroom_usd=float(initial_context.get("margin_headroom_usd", 0.30)),
            evoi=float(initial_context.get("evoi", 0.20)),
        )
        route_decision = self._router.route(state_vec)

        with self._wip_controller.acquire_slot():
            context: dict[str, Any] = dict(initial_context)
            context["_bellman_route"] = route_decision.selected_route.value

            completed_specs: list[DAGNodeSpec] = []
            node_outputs: dict[str, Any] = {}
            node_attempts: dict[str, int] = {}
            all_signatures: list[str] = []

            for wave in self._spec.topological_waves():
                # Execute independent nodes in the wave concurrently when >1 node is ready
                if len(wave) > 1 and route_decision.selected_route == RoutingMode.PARALLEL_FAN_OUT:
                    max_workers = min(len(wave), self.wip_limit)
                    with ThreadPoolExecutor(max_workers=max_workers) as wave_pool:
                        futures = [
                            (
                                node_spec,
                                wave_pool.submit(
                                    self._execute_single_node,
                                    node_spec,
                                    dict(context),
                                ),
                            )
                            for node_spec in wave
                        ]
                        wave_outcomes = [(ns, fut.result()) for ns, fut in futures]
                else:
                    wave_outcomes = [
                        (node_spec, self._execute_single_node(node_spec, context))
                        for node_spec in wave
                    ]

                for node_spec, (
                    node_succeeded,
                    out,
                    attempts,
                    node_sigs,
                    last_exc,
                    last_sig,
                    halted_on_duplicate,
                ) in wave_outcomes:
                    node_attempts[node_spec.node_id] = attempts
                    all_signatures.extend(node_sigs)

                    if node_succeeded and out is not None:
                        node_outputs[node_spec.node_id] = out
                        context[node_spec.node_id] = out
                        completed_specs.append(node_spec)
                    else:
                        # Execute Saga compensating rollback in reverse topological order
                        compensated_nodes: list[str] = []
                        compensating_actions_run: list[str] = []

                        for done_spec in reversed(completed_specs):
                            done_handler = self._handlers.get(done_spec.node_id)
                            if done_handler is not None and done_handler.compensate is not None:
                                done_handler.compensate(context)
                            compensated_nodes.append(done_spec.node_id)
                            compensating_actions_run.append(done_spec.compensating_action)

                        err_msg = (
                            f"{type(last_exc).__name__}: {last_exc}"
                            if last_exc
                            else "UnknownError"
                        )
                        ticket = HITLEscalationTicket(
                            ticket_id=f"hitl-{self._spec.workflow_id}-{last_sig[:10]}",
                            workflow_id=self._spec.workflow_id,
                            failed_node_id=node_spec.node_id,
                            error_signature_sha256=last_sig,
                            duplicate_signature_halted=halted_on_duplicate,
                            attempts_made=attempts,
                            compensating_actions_executed=tuple(compensating_actions_run),
                            error_message=err_msg,
                            metaphor_explanation=(
                                "George Costanza parallel-parking halt: duplicate SHA-256 error signature "
                                f"({last_sig[:12]}...) detected on attempt {attempts}. Halted pointless retries, "
                                f"backed the car out via Saga compensating actions {compensating_actions_run}, "
                                "and escalated to HITL."
                            ),
                        )
                        result = DAGExecutionResult(
                            workflow_id=self._spec.workflow_id,
                            status=DAGExecutionStatus.ROLLED_BACK_AND_ESCALATED,
                            route_decision=route_decision,
                            completed_nodes=tuple(s.node_id for s in completed_specs),
                            compensated_nodes=tuple(compensated_nodes),
                            compensating_actions_run=tuple(compensating_actions_run),
                            node_outputs=node_outputs,
                            node_attempt_counts=node_attempts,
                            observed_error_signatures=tuple(all_signatures),
                            hitl_ticket=ticket,
                        )
                        self._validate_postconditions(result)
                        return result

            result = DAGExecutionResult(
                workflow_id=self._spec.workflow_id,
                status=DAGExecutionStatus.COMPLETED,
                route_decision=route_decision,
                completed_nodes=tuple(s.node_id for s in completed_specs),
                compensated_nodes=(),
                compensating_actions_run=(),
                node_outputs=node_outputs,
                node_attempt_counts=node_attempts,
                observed_error_signatures=tuple(all_signatures),
                hitl_ticket=None,
            )
            self._validate_postconditions(result)
            return result

    def _validate_postconditions(self, result: DAGExecutionResult) -> None:
        if result.status == DAGExecutionStatus.COMPLETED:
            if result.hitl_ticket is not None:
                raise RuntimeError("Postcondition breach: COMPLETED run must not have an HITL ticket.")
            if len(result.completed_nodes) != len(self._spec.nodes):
                raise RuntimeError("Postcondition breach: COMPLETED run did not complete all nodes.")
        else:
            if result.hitl_ticket is None:
                raise RuntimeError("Postcondition breach: ROLLED_BACK run must emit an HITL ticket.")
            # Verify reverse topological compensation order
            expected_reverse = tuple(reversed(result.completed_nodes))
            if result.compensated_nodes != expected_reverse:
                raise RuntimeError(
                    f"Postcondition breach: Saga rollback order {result.compensated_nodes} "
                    f"does not match reverse completion order {expected_reverse}."
                )


def load_dag_workflow_yaml(yaml_path: Path | str) -> DAGWorkflowSpec:
    """Load and validate a `DAGWorkflowSpec` from a YAML file."""
    path = Path(yaml_path)
    raw_data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw_data, dict):
        raise ValueError(f"Expected YAML mapping in {path}, got {type(raw_data).__name__}.")
    return DAGWorkflowSpec.model_validate(raw_data)
