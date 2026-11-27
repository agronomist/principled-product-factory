"""Live Application Control Harness & Feature Map Maintenance Engine.

Implements pstack's `/create-verification-skill` and `/maintain-verification-skill` invariants:
1. Five Mandatory Harness Primitives (`ControlHarnessContract`):
   - `launch(isolated_dir)`: Prepares an isolated scratch workspace/process from empty state.
   - `doctor()`: Read-only health check ("is this instance worth driving?").
   - `drive(journey_input)`: Exercises the real user-facing surface (e.g., subprocess CLI or HTTP).
   - `capture_evidence(output, evidence_dir)`: Persists observable proof artifacts to a durable
     location outside the ephemeral scratch dir.
   - `cleanup()`: Removes ephemeral scratch directories and spawned resources while strictly
     preserving `evidence_dir`.
2. Three Live-Pass Invariants (`/maintain-verification-skill` Step 4):
   - Invariant 1 (Mandatory Doctor Gate): Never `drive()` an instance that hasn't passed `doctor()`
     since launch or since its last failed drive. Attempting to call `drive()` when `_doctor_verified`
     is False raises `HarnessStateError`.
   - Invariant 2 (Evidence Survival Across Cleanup): `cleanup()` must never delete captured
     evidence; `run_verified_journey()` explicitly asserts `evidence_file.exists()` *after* `cleanup()`.
   - Invariant 3 (Zero Residue Outliving Drive): All temporary scratch files created in `launch()`
     are removed in `cleanup()`, even if `drive()` fails.
3. `FeatureMapAuditor` (`/maintain-verification-skill`):
   Audits a product's `features/README.md` and `features/*.md` files for the four required H2
   sections (`## Sub-features`, `## How to get to it (user POV)`, `## Driving it with`, `## Gotchas`)
   and classifies the pass outcome as `clean`, `changed`, or `blocked`.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

TJourneyInput = TypeVar("TJourneyInput")
TJourneyOutput = TypeVar("TJourneyOutput")


class HarnessStateError(RuntimeError):
    """Raised when a harness invariant is violated (e.g. driving without a fresh doctor check)."""


class DoctorCheckResult(BaseModel):
    """Immutable read-only health check result from `harness.doctor()`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    healthy: bool = Field(...)
    version_or_build: str = Field(..., min_length=1)
    isolated_scratch_dir: str = Field(..., min_length=1)
    details: str = Field(..., min_length=1)


class EvidenceArtifact(BaseModel):
    """Immutable record of durable verification proof that survives `cleanup()`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    journey_id: str = Field(..., min_length=1)
    evidence_path: str = Field(..., min_length=1)
    exit_code: int = Field(default=0)
    captured_payload: dict[str, Any] = Field(...)
    survived_cleanup: bool = Field(...)


class HarnessExecutionReport(BaseModel):
    """End-to-end execution report returned by `ControlHarnessContract.run_verified_journey`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    journey_id: str = Field(..., min_length=1)
    doctor_pre_drive: DoctorCheckResult = Field(...)
    evidence: EvidenceArtifact = Field(...)
    scratch_cleaned_up: bool = Field(...)
    evidence_survived_cleanup: bool = Field(...)
    passed: bool = Field(...)


class ControlHarnessContract(ABC, Generic[TJourneyInput, TJourneyOutput]):
    """Abstract Liskov contract for all product verification harnesses (`/create-verification-skill`).

    Enforces the state machine:
    `launch() -> doctor() -> drive() -> capture_evidence() -> cleanup() -> verify_evidence_survived()`.
    """

    def __init__(self, scratch_root: Path, evidence_root: Path) -> None:
        self._scratch_root = scratch_root
        self._evidence_root = evidence_root
        self._launched: bool = False
        self._doctor_verified: bool = False
        self._active_scratch_dir: Path | None = None

    @property
    def is_launched(self) -> bool:
        return self._launched

    @property
    def is_doctor_verified(self) -> bool:
        return self._doctor_verified

    def launch(self, session_id: str = "default") -> Path:
        """Launch or provision an isolated instance from an empty scratch directory."""
        scratch_dir = self._scratch_root / f"harness-scratch-{session_id}"
        if scratch_dir.exists():
            shutil.rmtree(scratch_dir)
        scratch_dir.mkdir(parents=True, exist_ok=True)
        self._active_scratch_dir = scratch_dir
        self._launched = True
        self._doctor_verified = False  # Must run doctor() before driving!
        self._on_launch(scratch_dir)
        return scratch_dir

    def doctor(self) -> DoctorCheckResult:
        """Read-only health check answering: 'Is this instance worth driving?'"""
        if not self._launched or self._active_scratch_dir is None:
            raise HarnessStateError("Cannot run doctor() before launch().")
        res = self._on_doctor(self._active_scratch_dir)
        self._doctor_verified = res.healthy
        return res

    def drive(self, journey_input: TJourneyInput) -> TJourneyOutput:
        """Drive the application surface. Strictly requires a green `doctor()` check first."""
        if not self._launched or self._active_scratch_dir is None:
            raise HarnessStateError("Invariant violation: cannot drive() before launch().")
        if not self._doctor_verified:
            raise HarnessStateError(
                "Invariant 1 violation (/maintain-verification-skill): "
                "never drive an instance you haven't health-checked with doctor() since launch or last failure."
            )
        try:
            return self._on_drive(self._active_scratch_dir, journey_input)
        except Exception:
            # Any failed drive invalidates doctor status until re-checked or re-launched!
            self._doctor_verified = False
            raise

    def capture_evidence(
        self,
        journey_id: str,
        output: TJourneyOutput,
    ) -> Path:
        """Write proof artifacts to `self._evidence_root` (outside the ephemeral scratch directory)."""
        self._evidence_root.mkdir(parents=True, exist_ok=True)
        evidence_file = self._evidence_root / f"proof-{journey_id}.json"
        payload = self._serialize_evidence(output)
        evidence_file.write_text(
            json.dumps(payload, sort_keys=True, indent=2),
            encoding="utf-8",
        )
        return evidence_file

    def cleanup(self) -> bool:
        """Tear down the isolated instance and delete scratch residue, NEVER deleting evidence."""
        self._on_cleanup(self._active_scratch_dir)
        cleaned = False
        if self._active_scratch_dir is not None and self._active_scratch_dir.exists():
            shutil.rmtree(self._active_scratch_dir)
            cleaned = not self._active_scratch_dir.exists()
        else:
            cleaned = True
        self._launched = False
        self._doctor_verified = False
        return cleaned

    def run_verified_journey(
        self,
        journey_id: str,
        journey_input: TJourneyInput,
    ) -> HarnessExecutionReport:
        """Execute full `launch -> doctor -> drive -> capture_evidence -> cleanup` cycle and
        prove that evidence survives teardown.
        """
        scratch_dir = self.launch(session_id=journey_id)
        evidence_file: Path | None = None
        try:
            doc_res = self.doctor()
            if not doc_res.healthy:
                raise HarnessStateError(f"Doctor check failed: {doc_res.details}")
            raw_out = self.drive(journey_input)
            evidence_file = self.capture_evidence(journey_id, raw_out)
            serialized = self._serialize_evidence(raw_out)
        finally:
            scratch_cleaned = self.cleanup()

        if evidence_file is None or not evidence_file.is_file():
            raise HarnessStateError(
                "Invariant 2 violation (/create-verification-skill): "
                "cleanup ate the proof or evidence was not persisted!"
            )
        if scratch_dir.exists():
            raise HarnessStateError(
                "Invariant 3 violation (/maintain-verification-skill): "
                f"scratch directory {scratch_dir} outlived cleanup!"
            )

        artifact = EvidenceArtifact(
            journey_id=journey_id,
            evidence_path=str(evidence_file),
            exit_code=int(serialized.get("exit_code", 0)),
            captured_payload=serialized,
            survived_cleanup=True,
        )
        return HarnessExecutionReport(
            journey_id=journey_id,
            doctor_pre_drive=doc_res,
            evidence=artifact,
            scratch_cleaned_up=scratch_cleaned,
            evidence_survived_cleanup=True,
            passed=(artifact.exit_code == 0),
        )

    @abstractmethod
    def _on_launch(self, scratch_dir: Path) -> None:
        """Hook to initialize seed files or processes inside `scratch_dir`."""

    @abstractmethod
    def _on_doctor(self, scratch_dir: Path) -> DoctorCheckResult:
        """Hook to run read-only health verification."""

    @abstractmethod
    def _on_drive(self, scratch_dir: Path, journey_input: TJourneyInput) -> TJourneyOutput:
        """Hook to drive the application with `journey_input`."""

    @abstractmethod
    def _serialize_evidence(self, output: TJourneyOutput) -> dict[str, Any]:
        """Hook to serialize `output` into a JSON-compatible dictionary."""

    def _on_cleanup(self, scratch_dir: Path | None) -> None:
        """Optional hook for killing spawned PIDs before `scratch_dir` is deleted."""


class SubprocessCLIHarness(ControlHarnessContract[list[str], dict[str, Any]]):
    """Concrete verification harness that drives a Python CLI entry point in an isolated subprocess."""

    def __init__(
        self,
        repo_root: Path,
        module_or_script: str,
        scratch_root: Path,
        evidence_root: Path,
    ) -> None:
        super().__init__(scratch_root=scratch_root, evidence_root=evidence_root)
        self._repo_root = repo_root
        self._target = module_or_script

    def _on_launch(self, scratch_dir: Path) -> None:
        marker = scratch_dir / "session_ready.json"
        marker.write_text(
            json.dumps({"target": self._target, "repo_root": str(self._repo_root)}),
            encoding="utf-8",
        )

    def _on_doctor(self, scratch_dir: Path) -> DoctorCheckResult:
        marker = scratch_dir / "session_ready.json"
        target_path = self._repo_root / self._target
        healthy = marker.is_file() and target_path.is_file()
        return DoctorCheckResult(
            healthy=healthy,
            version_or_build="v11.0.0",
            isolated_scratch_dir=str(scratch_dir),
            details=(
                f"Ready: CLI script {target_path.name} verified and isolated scratch marker present."
                if healthy
                else f"Missing marker or target script at {target_path}"
            ),
        )

    def _on_drive(self, scratch_dir: Path, journey_input: list[str]) -> dict[str, Any]:
        script_path = str(self._repo_root / self._target)
        cmd = [sys.executable, script_path, *journey_input]
        env = {
            **os.environ,
            "PYTHONPATH": str(self._repo_root),
            "HARNESS_SCRATCH_DIR": str(scratch_dir),
        }
        proc = subprocess.run(
            cmd,
            cwd=str(self._repo_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=15.0,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"CLI journey failed with exit code {proc.returncode}: {proc.stderr.strip()}"
            )
        parsed_stdout: Any
        try:
            parsed_stdout = json.loads(proc.stdout)
        except json.JSONDecodeError:
            parsed_stdout = {"raw_stdout": proc.stdout.strip()}

        return {
            "command": cmd,
            "exit_code": proc.returncode,
            "output": parsed_stdout,
        }

    def _serialize_evidence(self, output: dict[str, Any]) -> dict[str, Any]:
        return output


# ---------------------------------------------------------------------------
# Feature Map Auditor (`/maintain-verification-skill`)
# ---------------------------------------------------------------------------


class FeatureSpecStatus(BaseModel):
    """Audit result for a single `features/<feature>.md` specification."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    feature_file: str = Field(..., min_length=1)
    has_sub_features_h2: bool = Field(...)
    has_user_pov_h2: bool = Field(...)
    has_driving_h2: bool = Field(...)
    has_gotchas_h2: bool = Field(...)
    indexed_in_readme: bool = Field(...)
    valid: bool = Field(...)


class FeatureMapAuditReport(BaseModel):
    """Aggregate report from `FeatureMapAuditor.audit_feature_map`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    features_dir: str = Field(..., min_length=1)
    outcome: str = Field(
        ...,
        pattern=r"^(clean|changed|blocked)$",
        description="Canonical /maintain-verification-skill outcome: clean, changed, or blocked.",
    )
    feature_statuses: tuple[FeatureSpecStatus, ...] = Field(...)
    drift_findings: tuple[str, ...] = Field(default_factory=tuple)
    passed: bool = Field(...)


class FeatureMapAuditor:
    """Audits a product's `features/` directory for pstack `/create-verification-skill` compliance:

    Checks:
    1. `features/README.md` exists and indexes every sibling feature `.md` file.
    2. Each feature file contains the four mandatory H2 headings:
       - `## Sub-features`
       - `## How to get to it (user POV)`
       - `## Driving it with` (prefix match)
       - `## Gotchas`
    """

    def audit_feature_map(self, features_dir: Path) -> FeatureMapAuditReport:
        readme_path = features_dir / "README.md"
        if not readme_path.is_file():
            return FeatureMapAuditReport(
                features_dir=str(features_dir),
                outcome="blocked",
                feature_statuses=(),
                drift_findings=("Missing features/README.md index file.",),
                passed=False,
            )

        readme_text = readme_path.read_text(encoding="utf-8")
        feature_files = sorted(
            p for p in features_dir.glob("*.md") if p.name != "README.md"
        )
        if not feature_files:
            return FeatureMapAuditReport(
                features_dir=str(features_dir),
                outcome="blocked",
                feature_statuses=(),
                drift_findings=("No feature specification files found in features/.",),
                passed=False,
            )

        statuses: list[FeatureSpecStatus] = []
        drift: list[str] = []

        for fpath in feature_files:
            content = fpath.read_text(encoding="utf-8")
            has_sub = "## Sub-features" in content
            has_pov = "## How to get to it (user POV)" in content
            has_drive = "## Driving it with" in content
            has_gotchas = "## Gotchas" in content
            in_readme = fpath.name in readme_text

            valid = has_sub and has_pov and has_drive and has_gotchas and in_readme
            if not valid:
                drift.append(
                    f"Feature file '{fpath.name}' failed structure/index check "
                    f"(sub={has_sub}, pov={has_pov}, drive={has_drive}, gotchas={has_gotchas}, indexed={in_readme})."
                )
            statuses.append(
                FeatureSpecStatus(
                    feature_file=fpath.name,
                    has_sub_features_h2=has_sub,
                    has_user_pov_h2=has_pov,
                    has_driving_h2=has_drive,
                    has_gotchas_h2=has_gotchas,
                    indexed_in_readme=in_readme,
                    valid=valid,
                )
            )

        all_valid = len(drift) == 0
        return FeatureMapAuditReport(
            features_dir=str(features_dir),
            outcome="clean" if all_valid else "changed",
            feature_statuses=tuple(statuses),
            drift_findings=tuple(drift),
            passed=all_valid,
        )
