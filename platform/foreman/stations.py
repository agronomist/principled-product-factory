"""Foreman Station Pipeline & Security Boundary Substrate (`platform/foreman/stations.py`).

Synthesizes Vercel's `eve` / Foreman Software Factory architecture with `pstack` and
`principled-product-builder-v10`:

1. **Orchestrator-That-Routes-Not-Writes & Four Task-Mode Stations**:
   - `classifier` -> `analyst` -> `implementer` -> `reviewer` (+ optional `researcher`).
   - Stations run in isolated task mode (`outputSchema`-equivalent frozen Pydantic v2 contracts),
     inheriting zero conversation history from the orchestrator and never blocking on interactive
     approval cards.
   - Orchestrator disables self-delegation (`allow_self_delegation = False`) and never skips a station.
   - If `classifier` returns `needs_clarification = True`, the pipeline stops immediately
     (posting clarification questions and halting rather than stranding an unattended run).
   - **Independent Cross-Vendor Review & Bounded Revisions**:
     `reviewer` runs on a different model vendor than `implementer`, never sees the implementer's
     internal Chain-of-Thought reasoning (only the original work item, verbatim acceptance criteria,
     pushed branch diff, and handoff artifact IDs), and grades every acceptance criterion verbatim.
     `request_changes` loops are strictly bounded (`MAX_REVISION_ROUNDS = 2`).
2. **Pass-by-ID Handoff Artifact Store & Anti-Poisoning Factory Brain**:
   - Long research and analysis memos travel between stations by strict regex-validated ID
     (`ARTIFACT_ID_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"`) with zero dots or slashes,
     preventing path traversal (`../factory-brain/...`) and context bloat.
   - `FactoryBrain` key is derived via SHA-256 of the static `factory_repo` configuration
     (never from model input), and writes from `UNATTENDED_AUTONOMOUS` principals are denied
     outright so prompt-injected issue bodies cannot poison future runs.
3. **Caller-Class Authorization Matrix & Draft-PR Unattended Ceiling**:
   - Evaluates `(CallerPrincipalClass, ToolAction, tool_input)` before any external side effect.
   - Unattended runs (`labeled` issue trigger) are **denied** (never parked on an approval card)
     for non-draft PRs, factory brain writes, and off-thread comments.
   - `merge_pull_request` is structurally absent from the tool surface across all caller classes.
4. **Inert-by-Construction Git Branch Guard, Firewall Egress Broker & Bounded Red-CI Loop**:
   - `validate_branch_name` blocks `main`, `master`, `HEAD`, `refs/*`, `..`, `//`, and shell
     metacharacters, enforcing `factory/` branch prefixing.
   - `FirewallCredentialBroker` injects git credentials only as an egress header transform to
     `github.com` against the literal `https://github.com/<factory_repo>.git` URL, never exposing
     tokens inside the sandbox or trusting a model-writable `origin` remote.
   - `RedCIFixLoopGuard` permits automated CI repair only on `factory/*` branches and halts
     after at most 2 fix attempts.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Sequence
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from platform.discovery.build_trap_guard import (
    BuildTrapGate,
    BuildTrapVerdict,
    CustomerEvidenceArtifact,
)

ARTIFACT_ID_PATTERN: re.Pattern[str] = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BRANCH_NAME_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9._/-]+$")
PROTECTED_BRANCHES: frozenset[str] = frozenset({"main", "master", "production", "release"})
MAX_REVISION_ROUNDS: int = 2
MAX_CI_FIX_ATTEMPTS: int = 2
MAX_ARTIFACT_CHARS: int = 200_000


class StationName(str, Enum):
    """Canonical Foreman task-mode stations."""

    CLASSIFIER = "classifier"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    IMPLEMENTER = "implementer"
    REVIEWER = "reviewer"


class CallerPrincipalClass(str, Enum):
    """Caller trust classes stamped at webhook/session dispatch before the model sees input."""

    UNATTENDED_AUTONOMOUS = "unattended_autonomous"
    TRUSTED_INTERACTIVE = "trusted_interactive"
    DEV_TUI = "dev_tui"
    UNTRUSTED_PUBLIC = "untrusted_public"


class ApprovalDecisionType(str, Enum):
    """Authorization outcomes emitted by `ForemanApprovalPolicy`."""

    RUNS = "runs"
    USER_APPROVAL_REQUIRED = "user_approval_required"
    DENIED = "denied"
    NOT_IN_TOOL_SURFACE = "not_in_tool_surface"


class ApprovalStatus(BaseModel):
    """Immutable authorization decision for a tool invocation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    action: str = Field(..., min_length=1)
    caller_class: CallerPrincipalClass = Field(...)
    decision: ApprovalDecisionType = Field(...)
    reason: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# 1. Input-Aware Approval Policy Matrix (Draft-PR Unattended Ceiling)
# ---------------------------------------------------------------------------


class ForemanApprovalPolicy:
    """Enforces Eve/Foreman's input-aware authorization matrix across caller classes:

    - `merge_pull_request` is absent from the tool surface (`NOT_IN_TOOL_SURFACE`) for all callers.
    - `create_pull_request` with `draft=True` runs ungated for authorized callers, whereas
      `draft=False` or `mark_pr_ready` is `DENIED` on `UNATTENDED_AUTONOMOUS` runs (never parked!)
      and requires `USER_APPROVAL_REQUIRED` for interactive/TUI runs.
    - `write_factory_brain` is `DENIED` on `UNATTENDED_AUTONOMOUS` runs so prompt-injected issue
      bodies cannot poison durable repository memory.
    """

    def evaluate(
        self,
        caller_class: CallerPrincipalClass,
        action: str,
        tool_input: dict[str, Any] | None = None,
    ) -> ApprovalStatus:
        payload = tool_input or {}

        if caller_class == CallerPrincipalClass.UNTRUSTED_PUBLIC:
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.DENIED,
                reason="Untrusted public accounts cannot start sessions or invoke factory tools.",
            )

        if action == "merge_pull_request":
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.NOT_IN_TOOL_SURFACE,
                reason="Merging stays a human act; merge_pull_request is absent from the factory tool surface.",
            )

        if action == "create_pull_request":
            is_draft = payload.get("draft") is True
            if is_draft:
                return ApprovalStatus(
                    action=action,
                    caller_class=caller_class,
                    decision=ApprovalDecisionType.RUNS,
                    reason="Draft pull requests cannot merge and are the safe unattended ceiling.",
                )
            return self._ship_policy(caller_class, action)

        if action == "mark_pr_ready":
            return self._ship_policy(caller_class, action)

        if action == "write_factory_brain":
            if caller_class == CallerPrincipalClass.UNATTENDED_AUTONOMOUS:
                return ApprovalStatus(
                    action=action,
                    caller_class=caller_class,
                    decision=ApprovalDecisionType.DENIED,
                    reason="Unattended runs are denied factory brain writes to prevent prompt-injection memory poisoning.",
                )
            if caller_class == CallerPrincipalClass.DEV_TUI:
                return ApprovalStatus(
                    action=action,
                    caller_class=caller_class,
                    decision=ApprovalDecisionType.USER_APPROVAL_REQUIRED,
                    reason="Dev TUI is untrusted by default; factory brain writes wait on an approval card.",
                )
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.RUNS,
                reason="Trusted interactive session permitted to update factory brain.",
            )

        if action == "comment_off_thread" or action == "write_linear":
            if caller_class == CallerPrincipalClass.UNATTENDED_AUTONOMOUS:
                return ApprovalStatus(
                    action=action,
                    caller_class=caller_class,
                    decision=ApprovalDecisionType.DENIED,
                    reason="Unattended runs cannot fan out writes to Linear or off-thread issues.",
                )
            if caller_class == CallerPrincipalClass.DEV_TUI and action == "comment_off_thread":
                return ApprovalStatus(
                    action=action,
                    caller_class=caller_class,
                    decision=ApprovalDecisionType.USER_APPROVAL_REQUIRED,
                    reason="Dev TUI off-thread comments wait for user approval.",
                )
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.RUNS,
                reason="Permitted for trusted interactive session.",
            )

        if action in ("apply_or_remove_labels", "comment_intake_issue"):
            if caller_class == CallerPrincipalClass.DEV_TUI:
                return ApprovalStatus(
                    action=action,
                    caller_class=caller_class,
                    decision=ApprovalDecisionType.USER_APPROVAL_REQUIRED,
                    reason="Dev TUI writes to GitHub wait for local user approval.",
                )
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.RUNS,
                reason="Reversible triage on intake issue permitted.",
            )

        if action == "close_or_reopen_issue":
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.RUNS,
                reason="Closing or reopening an issue is reversible triage and runs ungated for authorized sessions.",
            )

        if action == "clear_user_preferences":
            if caller_class == CallerPrincipalClass.UNATTENDED_AUTONOMOUS:
                return ApprovalStatus(
                    action=action,
                    caller_class=caller_class,
                    decision=ApprovalDecisionType.DENIED,
                    reason="Unattended runs cannot clear user preferences.",
                )
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.USER_APPROVAL_REQUIRED,
                reason="Clearing user preferences is irreversible and requires user approval.",
            )

        # Deny/approval-by-default for any unlisted write tool
        if caller_class == CallerPrincipalClass.UNATTENDED_AUTONOMOUS:
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.DENIED,
                reason=f"Unlisted tool '{action}' denied by default on unattended autonomous run.",
            )
        return ApprovalStatus(
            action=action,
            caller_class=caller_class,
            decision=ApprovalDecisionType.USER_APPROVAL_REQUIRED,
            reason=f"Unlisted tool '{action}' requires user approval by default.",
        )

    @staticmethod
    def _ship_policy(caller_class: CallerPrincipalClass, action: str) -> ApprovalStatus:
        if caller_class == CallerPrincipalClass.UNATTENDED_AUTONOMOUS:
            return ApprovalStatus(
                action=action,
                caller_class=caller_class,
                decision=ApprovalDecisionType.DENIED,
                reason="Unattended factory runs stop at a draft pull request; a person marks it ready.",
            )
        return ApprovalStatus(
            action=action,
            caller_class=caller_class,
            decision=ApprovalDecisionType.USER_APPROVAL_REQUIRED,
            reason="Shipping actions park for human approval.",
        )


# ---------------------------------------------------------------------------
# 2. Pass-by-ID Handoff Artifact Store & Anti-Poisoning Factory Brain
# ---------------------------------------------------------------------------


def resolve_artifact_key(artifact_id: str) -> str | None:
    """Validate `artifact_id` against `^[a-z0-9]+(?:-[a-z0-9]+)*$` (no dots or slashes).

    Returns `"artifacts/<artifact_id>.md"` if valid, or `None` if invalid (indistinguishable
    from not-found so path-traversal probes learn nothing).
    """
    if not ARTIFACT_ID_PATTERN.fullmatch(artifact_id):
        return None
    return f"artifacts/{artifact_id}.md"


class HandoffArtifactStore:
    """Pass-by-ID store for long station documents (up to 200,000 chars) so memos never bloat
    the orchestrator's context window.

    - Saves never overwrite and mint a deterministic/unique suffixed slug (`<prefix>-<hash6>`).
    - Reads validate the ID against `ARTIFACT_ID_PATTERN` (blocking `../` traversal).
    - When `sqlite_store` is supplied, artifacts are durably persisted to disk in SQLite WAL mode.
    """

    def __init__(self, sqlite_store: Any | None = None) -> None:
        self._blobs: dict[str, str] = {}
        self._counter: int = 0
        self._sqlite_store = sqlite_store

    def save_artifact(self, slug_prefix: str, content: str) -> str:
        """Mint an immutable suffixed artifact ID and store `content` under `artifacts/<id>.md`."""
        clean_prefix = re.sub(r"[^a-z0-9-]+", "-", slug_prefix.lower()).strip("-")
        clean_prefix = re.sub(r"-+", "-", clean_prefix) or "memo"
        if len(content) > MAX_ARTIFACT_CHARS:
            raise ValueError(
                f"Artifact content length {len(content)} exceeds MAX_ARTIFACT_CHARS={MAX_ARTIFACT_CHARS}."
            )
        self._counter += 1
        digest_suffix = hashlib.sha256(
            f"{clean_prefix}:{self._counter}:{content}".encode("utf-8")
        ).hexdigest()[:6]
        artifact_id = f"{clean_prefix}-{digest_suffix}"
        key = resolve_artifact_key(artifact_id)
        if key is None:
            raise ValueError(f"Generated invalid artifact_id: {artifact_id!r}")
        if key in self._blobs:
            raise RuntimeError("Immutable artifact collision.")
        if self._sqlite_store is not None:
            self._sqlite_store.save_artifact_row(key, content)
        self._blobs[key] = content
        return artifact_id

    def read_artifact(self, artifact_id: str) -> str | None:
        """Read an artifact by ID. Invalid or traversal IDs return `None` (same as missing)."""
        key = resolve_artifact_key(artifact_id)
        if key is None:
            return None
        if key in self._blobs:
            return self._blobs[key]
        if self._sqlite_store is not None:
            persisted = self._sqlite_store.read_artifact_row(key)
            if persisted is not None:
                self._blobs[key] = persisted
                return persisted
        return None


class FactoryBrain:
    """Durable repository memory whose storage key is derived strictly from `SHA256(factory_repo)`
    at initialization (never from model input) and whose writes are gated by `ForemanApprovalPolicy`.
    """

    def __init__(
        self,
        factory_repo: str,
        approval_policy: ForemanApprovalPolicy | None = None,
        sqlite_store: Any | None = None,
    ) -> None:
        if not re.fullmatch(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", factory_repo.strip()):
            raise ValueError(
                f"FACTORY_REPO is required at load time as 'owner/repo', got {factory_repo!r}."
            )
        self._factory_repo = factory_repo.strip()
        self._policy = approval_policy or ForemanApprovalPolicy()
        repo_hash = hashlib.sha256(self._factory_repo.encode("utf-8")).hexdigest()
        self._brain_key = f"factory-brain/{repo_hash}.md"
        self._sqlite_store = sqlite_store
        self._notes: list[str] = (
            list(self._sqlite_store.read_brain_notes(self._brain_key))
            if self._sqlite_store is not None
            else []
        )

    @property
    def factory_repo(self) -> str:
        return self._factory_repo

    @property
    def brain_key(self) -> str:
        """Storage key derived purely from `FACTORY_REPO`, immune to model input redirection."""
        return self._brain_key

    def read_brain(self) -> str:
        """Open to every run at grounding time."""
        if self._sqlite_store is not None:
            self._notes = list(self._sqlite_store.read_brain_notes(self._brain_key))
        return "\n".join(self._notes)

    def write_brain(
        self,
        caller_class: CallerPrincipalClass,
        note: str,
        *,
        user_approved: bool = False,
    ) -> ApprovalStatus:
        """Append a durable note to the factory brain if and only if authorized by `factoryBrainPolicy`."""
        status = self._policy.evaluate(caller_class, "write_factory_brain")
        if status.decision == ApprovalDecisionType.DENIED:
            raise PermissionError(status.reason)
        if status.decision == ApprovalDecisionType.USER_APPROVAL_REQUIRED and not user_approved:
            return status
        if note.strip():
            clean_note = note.strip()
            if self._sqlite_store is not None:
                self._sqlite_store.append_brain_note(self._brain_key, clean_note)
            self._notes.append(clean_note)
        return status


# ---------------------------------------------------------------------------
# 3. Inert-by-Construction Git Branch Guard, Firewall Egress Broker & Red-CI Guard
# ---------------------------------------------------------------------------


def validate_branch_name(
    branch: str,
    required_prefix: str = "factory/",
) -> str | None:
    """Validate that a git branch push is inert by construction.

    Returns `None` when valid, or a descriptive error string when rejected.
    Refuses `main`, `master`, `HEAD`, `refs/*`, `..`, `//`, shell metacharacters,
    and branches missing `required_prefix`.
    """
    if not BRANCH_NAME_PATTERN.fullmatch(branch) or ".." in branch or "//" in branch:
        return f'"{branch}" is not a valid branch name.'
    if branch.startswith("refs/") or branch == "HEAD":
        return f'"{branch}" is not a plain branch name. Pass the branch name without a refs/ prefix.'
    if branch in PROTECTED_BRANCHES or branch.removeprefix(required_prefix) in PROTECTED_BRANCHES:
        return f"Direct pushes to {branch} are not allowed. Push a feature branch and open a pull request."
    if not branch.startswith(required_prefix):
        return f'Branch "{branch}" must start with required factory prefix "{required_prefix}".'
    return None


class SandboxEgressPolicy(BaseModel):
    """Firewall network egress transform injecting GitHub installation token outside the sandbox."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    canonical_git_url: str = Field(..., min_length=1)
    allowed_host: str = Field(default="github.com")
    injected_authorization_header: str = Field(..., min_length=1)
    token_exposed_inside_sandbox: bool = Field(default=False)


class FirewallCredentialBroker:
    """Brokers Git credentials at the sandbox firewall boundary:

    - Targets the literal `https://github.com/<FACTORY_REPO>.git` URL, never the model-writable
      `origin` remote inside the sandbox.
    - Injects the `Authorization: Basic ...` header at the network egress layer and drops it
      in a `finally` block so the raw installation token never enters sandbox memory/env.
    """

    def __init__(self, factory_repo: str) -> None:
        if not re.fullmatch(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", factory_repo.strip()):
            raise ValueError(f"Invalid factory_repo: {factory_repo!r}")
        self._factory_repo = factory_repo.strip()

    @property
    def canonical_remote_url(self) -> str:
        return f"https://github.com/{self._factory_repo}.git"

    def build_egress_policy(
        self,
        installation_token: str,
        requested_remote: str | None = None,
    ) -> SandboxEgressPolicy:
        if requested_remote is not None and requested_remote != self.canonical_remote_url:
            raise PermissionError(
                f"Refusing to broker credentials to model-writable remote '{requested_remote}'. "
                f"Git operations must target literal '{self.canonical_remote_url}'."
            )
        if not installation_token.strip():
            raise ValueError("installation_token cannot be empty.")
        # Compute deterministic redacted header representation
        token_digest = hashlib.sha256(installation_token.encode("utf-8")).hexdigest()[:12]
        return SandboxEgressPolicy(
            canonical_git_url=self.canonical_remote_url,
            allowed_host="github.com",
            injected_authorization_header=f"Basic x-access-token:<brokered-at-firewall:{token_digest}>",
            token_exposed_inside_sandbox=False,
        )


class RedCIFixLoopGuard:
    """Guards unattended red-CI repair loops:

    - Only touches branches starting with `FACTORY_BRANCH_PREFIX` (`factory/`), never human branches.
    - Caps automated repair at `MAX_CI_FIX_ATTEMPTS = 2` so the factory never loops endlessly
      on a failure it doesn't understand.
    """

    def __init__(
        self,
        branch_prefix: str = "factory/",
        max_attempts: int = MAX_CI_FIX_ATTEMPTS,
    ) -> None:
        self._prefix = branch_prefix
        self._max_attempts = max_attempts

    def can_attempt_ci_fix(
        self,
        branch_name: str,
        prior_fix_attempt_comments: int,
    ) -> tuple[bool, str]:
        branch_err = validate_branch_name(branch_name, required_prefix=self._prefix)
        if branch_err is not None:
            return (
                False,
                f"Refused red-CI fix: branch '{branch_name}' is not a valid '{self._prefix}*' branch ({branch_err}).",
            )
        if prior_fix_attempt_comments >= self._max_attempts:
            return (
                False,
                f"Halted red-CI loop on '{branch_name}': reached max {self._max_attempts} fix attempts "
                f"(observed {prior_fix_attempt_comments}). Waiting for human diagnosis.",
            )
        return (
            True,
            f"Approved red-CI fix attempt {prior_fix_attempt_comments + 1}/{self._max_attempts} on '{branch_name}'.",
        )


# ---------------------------------------------------------------------------
# 4. Task-Mode Station Schemas (`Classifier -> Analyst -> Implementer -> Reviewer`)
# ---------------------------------------------------------------------------


class WorkItemIntake(BaseModel):
    """Inbound work item from GitHub Issue, @mention, Linear Agent Session, or Dev TUI."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    caller_class: CallerPrincipalClass = Field(
        default=CallerPrincipalClass.UNATTENDED_AUTONOMOUS
    )
    requester_name: str = Field(default="maintainer", min_length=1)
    needs_external_research: bool = Field(default=False)
    customer_evidence: CustomerEvidenceArtifact | None = Field(
        default=None,
        description=(
            "Empirical customer value & commitment evidence. Required when "
            "classifier classifies work_type as 'feature' so the factory never "
            "falls into the Build Trap ('someone at some point will like it')."
        ),
    )


class ClassifierOutput(BaseModel):
    """Structured task-mode `outputSchema` returned by the `classifier` station."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    work_type: str = Field(..., pattern=r"^(bug|feature|refactor|perf|chore)$")
    priority: str = Field(..., pattern=r"^(P0|P1|P2|P3)$")
    complexity: float = Field(..., ge=0.0, le=1.0)
    affected_area: str = Field(..., min_length=1)
    repo_labels: tuple[str, ...] = Field(...)
    actionable: bool = Field(...)
    needs_clarification: bool = Field(...)
    clarification_questions: tuple[str, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _validate_clarification_consistency(self) -> ClassifierOutput:
        if self.needs_clarification and not self.clarification_questions:
            raise ValueError(
                "needs_clarification=True requires at least one clarification question."
            )
        if self.needs_clarification and self.actionable:
            raise ValueError("Work item cannot be both actionable and needs_clarification.")
        return self


class ResearcherOutput(BaseModel):
    """Structured task-mode `outputSchema` returned by the optional `researcher` station."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    findings_summary: str = Field(..., min_length=1)
    confidence_level: float = Field(..., ge=0.0, le=1.0)
    open_gaps: tuple[str, ...] = Field(default_factory=tuple)
    memo_artifact_id: str = Field(..., min_length=1)


class AnalystOutput(BaseModel):
    """Structured task-mode `outputSchema` returned by the `analyst` station."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    approach_summary: str = Field(..., min_length=1)
    ordered_steps: tuple[str, ...] = Field(..., min_length=1)
    acceptance_criteria: tuple[str, ...] = Field(
        ...,
        min_length=1,
        description="Verbatim contract that the reviewer grades the implementation against.",
    )
    risks: tuple[str, ...] = Field(default_factory=tuple)
    analysis_artifact_id: str = Field(..., min_length=1)


class ImplementerBrief(BaseModel):
    """Self-contained brief handed to `implementer` (runs in a fresh session with zero orchestrator history)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    work_item: WorkItemIntake = Field(...)
    classification: ClassifierOutput = Field(...)
    plan: AnalystOutput = Field(...)
    research_artifact_id: str | None = Field(default=None)
    factory_brain_notes: str = Field(default="")
    revision_round: int = Field(default=0, ge=0, le=MAX_REVISION_ROUNDS)
    prior_reviewer_blocking_findings: tuple[str, ...] = Field(default_factory=tuple)


class ImplementerOutput(BaseModel):
    """Structured task-mode `outputSchema` returned by the `implementer` station."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    branch_name: str = Field(..., min_length=1)
    changed_files_summary: dict[str, str] = Field(..., min_length=1)
    verification_passed: bool = Field(...)
    verification_command_output: str = Field(..., min_length=1)
    # Note: internal_reasoning is stripped by Foreman before building ReviewerBrief!
    internal_reasoning: str = Field(
        default="",
        description="Implementer's private chain-of-thought; NEVER forwarded to ReviewerBrief.",
    )


class ReviewerBrief(BaseModel):
    """Self-contained brief handed to `reviewer`.

    Enforces Rule 1 of Eve/Foreman: *"The review is independent. The reviewer never sees
    the implementer's reasoning, only the pushed branch."*
    Notice `internal_reasoning` is structurally absent from `ReviewerBrief`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    work_item: WorkItemIntake = Field(...)
    acceptance_criteria: tuple[str, ...] = Field(..., min_length=1)
    analysis_artifact_id: str = Field(..., min_length=1)
    branch_name: str = Field(..., min_length=1)
    changed_files_summary: dict[str, str] = Field(..., min_length=1)
    verification_command_output: str = Field(..., min_length=1)
    revision_round: int = Field(default=0, ge=0, le=MAX_REVISION_ROUNDS)


class CriterionVerdict(BaseModel):
    """Pass/fail judgment with concrete evidence for one verbatim acceptance criterion."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    criterion: str = Field(..., min_length=1)
    passed: bool = Field(...)
    evidence: str = Field(..., min_length=1)


class ReviewVerdictType(str, Enum):
    """Canonical verdicts returned by the `reviewer` station."""

    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"


class ReviewerOutput(BaseModel):
    """Structured task-mode `outputSchema` returned by the `reviewer` station."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    verdict: ReviewVerdictType = Field(...)
    criteria_results: tuple[CriterionVerdict, ...] = Field(..., min_length=1)
    blocking_findings: tuple[str, ...] = Field(default_factory=tuple)
    suggestions: tuple[str, ...] = Field(default_factory=tuple)
    summary: str = Field(..., min_length=1)


class ForemanPipelineStatus(str, Enum):
    """Terminal statuses for a Foreman pipeline run."""

    DRAFT_PR_OPENED = "draft_pr_opened"
    HALTED_NEEDS_CLARIFICATION = "halted_needs_clarification"
    HALTED_BUILD_TRAP_NO_CUSTOMER_VALUE = "halted_build_trap_no_customer_value"
    HALTED_REVIEW_REJECTED = "halted_review_rejected"
    HALTED_MAX_REVISIONS_EXCEEDED = "halted_max_revisions_exceeded"


class ForemanPipelineResult(BaseModel):
    """Immutable postcondition result returned by `ForemanOrchestrator.run_pipeline`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    item_id: str = Field(..., min_length=1)
    status: ForemanPipelineStatus = Field(...)
    stations_visited: tuple[StationName, ...] = Field(...)
    classification: ClassifierOutput = Field(...)
    build_trap_verdict: BuildTrapVerdict | None = Field(default=None)
    research: ResearcherOutput | None = Field(default=None)
    analysis: AnalystOutput | None = Field(default=None)
    final_implementation: ImplementerOutput | None = Field(default=None)
    final_review: ReviewerOutput | None = Field(default=None)
    revision_rounds_used: int = Field(default=0, ge=0, le=MAX_REVISION_ROUNDS)
    draft_pr_url: str | None = Field(default=None)
    pr_approval_status: ApprovalStatus | None = Field(default=None)
    clarification_comment_posted: tuple[str, ...] = Field(default_factory=tuple)
    unresolved_blocking_findings: tuple[str, ...] = Field(default_factory=tuple)


class StationModelConfig(BaseModel):
    """Centralized model mapping (`agent/lib/models.ts` equivalent) enforcing cross-vendor review."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    orchestrator: str = Field(default="openai/gpt-5.6-terra-fast")
    classifier: str = Field(default="openai/gpt-5.6-terra-fast")
    researcher: str = Field(default="openai/gpt-5.6-terra-fast")
    analyst: str = Field(default="openai/gpt-5.6-terra-fast")
    implementer: str = Field(default="anthropic/claude-fable-5")
    reviewer: str = Field(default="openai/gpt-5.6-terra-fast")

    @model_validator(mode="after")
    def _enforce_cross_vendor_implementer_and_reviewer(self) -> StationModelConfig:
        impl_vendor = self.implementer.split("/", maxsplit=1)[0].split("-", maxsplit=1)[0].lower()
        rev_vendor = self.reviewer.split("/", maxsplit=1)[0].split("-", maxsplit=1)[0].lower()
        if impl_vendor == rev_vendor:
            raise ValueError(
                f"Independent review violation: implementer ({self.implementer}) and reviewer "
                f"({self.reviewer}) must run on different model vendors, got '{impl_vendor}'."
            )
        return self


class ForemanOrchestrator:
    """Foreman: The orchestrator that routes, not writes.

    Enforces Eve's core architectural rules plus the Anti-Build-Trap Customer Value Gate:
    1. **No Self-Delegation**: `allow_self_delegation = False`; all work routes through the
       4 declared task-mode stations in strict order (`classifier -> analyst -> implementer -> reviewer`).
    2. **Stop for Clarification**: When `classifier` returns `needs_clarification=True`,
       stops immediately and posts the questions rather than leaving an unattended run waiting.
    3. **Anti-Build-Trap Customer Value Gate**: When `classifier` classifies a work item as a
       `feature` (or whenever `customer_evidence` is attached), `BuildTrapGate` verifies that
       the item solves an underserved customer job (Ulwick Opportunity Score >= 10.0) backed
       by real customer skin-in-the-game (never "someone at some point will like it").
    4. **Pass-by-ID Handoff Artifacts**: Analyst and researcher memos are saved in
       `HandoffArtifactStore` and passed by validated ID (`^[a-z0-9]+(?:-[a-z0-9]+)*$`).
    5. **Independent Cross-Vendor Review**: `ReviewerBrief` omits `implementer.internal_reasoning`,
       runs on a different model vendor than `implementer`, and checks every acceptance
       criterion verbatim.
    6. **Bounded Revisions**: Loops `request_changes -> implementer -> reviewer` at most
       `MAX_REVISION_ROUNDS = 2` times; if still unapproved, halts the line without opening a PR.
    7. **Draft-PR Unattended Ceiling**: Opens a `draft=True` pull request on an inert
       `factory/*` branch verified by `validate_branch_name`.
    """

    def __init__(
        self,
        factory_brain: FactoryBrain,
        artifact_store: HandoffArtifactStore,
        classifier_fn: Callable[[WorkItemIntake, str], ClassifierOutput],
        analyst_fn: Callable[[WorkItemIntake, ClassifierOutput, HandoffArtifactStore, str | None], AnalystOutput],
        implementer_fn: Callable[[ImplementerBrief, HandoffArtifactStore], ImplementerOutput],
        reviewer_fn: Callable[[ReviewerBrief, HandoffArtifactStore], ReviewerOutput],
        researcher_fn: Callable[[WorkItemIntake, HandoffArtifactStore], ResearcherOutput] | None = None,
        models: StationModelConfig | None = None,
        approval_policy: ForemanApprovalPolicy | None = None,
        build_trap_gate: BuildTrapGate | None = None,
        branch_prefix: str = "factory/",
    ) -> None:
        self._brain = factory_brain
        self._artifacts = artifact_store
        self._classifier_fn = classifier_fn
        self._analyst_fn = analyst_fn
        self._implementer_fn = implementer_fn
        self._reviewer_fn = reviewer_fn
        self._researcher_fn = researcher_fn
        self._models = models or StationModelConfig()
        self._policy = approval_policy or ForemanApprovalPolicy()
        self._build_trap_gate = build_trap_gate or BuildTrapGate()
        self._branch_prefix = branch_prefix
        self._allow_self_delegation: bool = False

    @property
    def allow_self_delegation(self) -> bool:
        return self._allow_self_delegation

    @property
    def models(self) -> StationModelConfig:
        return self._models

    def delegate_to_self(self) -> None:
        """Structural guard matching Eve's `disableTool()` on the root agent tool."""
        raise PermissionError(
            "Self-delegation is disabled (`disableTool()`): Foreman is a routing layer, not a fifth station. "
            "All work must route through classifier, analyst, implementer, and reviewer."
        )

    def run_pipeline(self, work_item: WorkItemIntake) -> ForemanPipelineResult:
        """Route `work_item` through the 4 task-mode stations in strict order."""
        brain_notes = self._brain.read_brain()
        visited: list[StationName] = []

        # Station 1: Classifier (Always runs first; never skipped)
        visited.append(StationName.CLASSIFIER)
        classification = self._classifier_fn(work_item, brain_notes)

        if classification.needs_clarification:
            return ForemanPipelineResult(
                item_id=work_item.item_id,
                status=ForemanPipelineStatus.HALTED_NEEDS_CLARIFICATION,
                stations_visited=tuple(visited),
                classification=classification,
                clarification_comment_posted=classification.clarification_questions,
            )

        # Anti-Build-Trap Gate: Features MUST prove real customer value & skin-in-the-game
        bt_verdict: BuildTrapVerdict | None = None
        if classification.work_type == "feature" or work_item.customer_evidence is not None:
            if work_item.customer_evidence is None:
                return ForemanPipelineResult(
                    item_id=work_item.item_id,
                    status=ForemanPipelineStatus.HALTED_BUILD_TRAP_NO_CUSTOMER_VALUE,
                    stations_visited=tuple(visited),
                    classification=classification,
                    unresolved_blocking_findings=(
                        "Build Trap Guard: Feature requests require a CustomerEvidenceArtifact "
                        "(JTBD Opportunity Score >= 10.0 and real customer skin-in-the-game, "
                        "never 'someone at some point will like it').",
                    ),
                )
            bt_verdict = self._build_trap_gate.evaluate(work_item.customer_evidence)
            if not (
                bt_verdict.approved_for_production_build
                or bt_verdict.approved_for_discovery_probe
            ):
                return ForemanPipelineResult(
                    item_id=work_item.item_id,
                    status=ForemanPipelineStatus.HALTED_BUILD_TRAP_NO_CUSTOMER_VALUE,
                    stations_visited=tuple(visited),
                    classification=classification,
                    build_trap_verdict=bt_verdict,
                    unresolved_blocking_findings=bt_verdict.blocking_reasons,
                )

        # Optional Researcher station when external facts are required
        research_out: ResearcherOutput | None = None
        if work_item.needs_external_research and self._researcher_fn is not None:
            visited.append(StationName.RESEARCHER)
            research_out = self._researcher_fn(work_item, self._artifacts)
            if self._artifacts.read_artifact(research_out.memo_artifact_id) is None:
                raise RuntimeError(
                    f"Researcher handoff artifact '{research_out.memo_artifact_id}' missing or invalid ID."
                )

        # Station 2: Analyst (Writes verbatim acceptance criteria and saves detail memo by ID)
        visited.append(StationName.ANALYST)
        analysis = self._analyst_fn(
            work_item,
            classification,
            self._artifacts,
            research_out.memo_artifact_id if research_out else None,
        )
        if self._artifacts.read_artifact(analysis.analysis_artifact_id) is None:
            raise RuntimeError(
                f"Analyst handoff artifact '{analysis.analysis_artifact_id}' missing or invalid ID."
            )

        # Station 3 & 4: Implementer <-> Reviewer bounded revision loop (at most MAX_REVISION_ROUNDS = 2)
        revision_round = 0
        prior_blocking: tuple[str, ...] = ()
        impl_out: ImplementerOutput | None = None
        rev_out: ReviewerOutput | None = None

        while True:
            visited.append(StationName.IMPLEMENTER)
            impl_brief = ImplementerBrief(
                work_item=work_item,
                classification=classification,
                plan=analysis,
                research_artifact_id=research_out.memo_artifact_id if research_out else None,
                factory_brain_notes=brain_notes,
                revision_round=revision_round,
                prior_reviewer_blocking_findings=prior_blocking,
            )
            impl_out = self._implementer_fn(impl_brief, self._artifacts)

            # Enforce inert-by-construction git branch validation before review
            branch_err = validate_branch_name(
                impl_out.branch_name, required_prefix=self._branch_prefix
            )
            if branch_err is not None:
                raise PermissionError(f"Implementer branch rejected by sandbox guard: {branch_err}")

            # Station 4: Independent Cross-Vendor Reviewer (never receives impl_out.internal_reasoning!)
            visited.append(StationName.REVIEWER)
            rev_brief = ReviewerBrief(
                work_item=work_item,
                acceptance_criteria=analysis.acceptance_criteria,
                analysis_artifact_id=analysis.analysis_artifact_id,
                branch_name=impl_out.branch_name,
                changed_files_summary=impl_out.changed_files_summary,
                verification_command_output=impl_out.verification_command_output,
                revision_round=revision_round,
            )
            rev_out = self._reviewer_fn(rev_brief, self._artifacts)
            self._validate_verbatim_criteria_coverage(analysis.acceptance_criteria, rev_out)

            if rev_out.verdict == ReviewVerdictType.APPROVE:
                break

            if rev_out.verdict == ReviewVerdictType.REJECT:
                return ForemanPipelineResult(
                    item_id=work_item.item_id,
                    status=ForemanPipelineStatus.HALTED_REVIEW_REJECTED,
                    stations_visited=tuple(visited),
                    classification=classification,
                    build_trap_verdict=bt_verdict,
                    research=research_out,
                    analysis=analysis,
                    final_implementation=impl_out,
                    final_review=rev_out,
                    revision_rounds_used=revision_round,
                    unresolved_blocking_findings=rev_out.blocking_findings,
                )

            # ReviewVerdictType.REQUEST_CHANGES: check bounded revision ceiling
            if revision_round >= MAX_REVISION_ROUNDS:
                return ForemanPipelineResult(
                    item_id=work_item.item_id,
                    status=ForemanPipelineStatus.HALTED_MAX_REVISIONS_EXCEEDED,
                    stations_visited=tuple(visited),
                    classification=classification,
                    build_trap_verdict=bt_verdict,
                    research=research_out,
                    analysis=analysis,
                    final_implementation=impl_out,
                    final_review=rev_out,
                    revision_rounds_used=revision_round,
                    unresolved_blocking_findings=rev_out.blocking_findings,
                )

            revision_round += 1
            prior_blocking = rev_out.blocking_findings

        # Reviewer approved! Open a draft pull request (the unattended ceiling)
        pr_approval = self._policy.evaluate(
            work_item.caller_class,
            "create_pull_request",
            {"draft": True, "head": impl_out.branch_name},
        )
        if pr_approval.decision != ApprovalDecisionType.RUNS:
            raise PermissionError(f"Draft PR creation blocked: {pr_approval.reason}")

        draft_pr_url = (
            f"https://github.com/{self._brain.factory_repo}/pull/draft-{work_item.item_id}"
        )
        return ForemanPipelineResult(
            item_id=work_item.item_id,
            status=ForemanPipelineStatus.DRAFT_PR_OPENED,
            stations_visited=tuple(visited),
            classification=classification,
            build_trap_verdict=bt_verdict,
            research=research_out,
            analysis=analysis,
            final_implementation=impl_out,
            final_review=rev_out,
            revision_rounds_used=revision_round,
            draft_pr_url=draft_pr_url,
            pr_approval_status=pr_approval,
        )

    @staticmethod
    def _validate_verbatim_criteria_coverage(
        expected_criteria: Sequence[str],
        review: ReviewerOutput,
    ) -> None:
        judged = [c.criterion for c in review.criteria_results]
        if tuple(judged) != tuple(expected_criteria):
            raise RuntimeError(
                f"Reviewer contract breach: acceptance criteria must be judged verbatim. "
                f"Expected {list(expected_criteria)}, got {judged}."
            )
        if review.verdict == ReviewVerdictType.APPROVE and not all(
            c.passed for c in review.criteria_results
        ):
            raise RuntimeError(
                "Reviewer contract breach: cannot return APPROVE when an acceptance criterion failed."
            )
