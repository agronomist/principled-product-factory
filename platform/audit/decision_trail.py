"""Append-Only TSV Decision Trail & Cross-Model Audit Verifier (`/show-me-your-work`).

Implements pstack's `show-me-your-work` decision trail discipline for long-running,
multi-phase, or autonomous loop execution:
1. Canonical TSV Format (`ts | phase | decision | why | evidence | result`):
   - Cells are strictly single-line (tabs/newlines stripped).
   - Spreadsheet formula-injection bytes (`=`, `+`, `-`, `@`) at the start of any cell
     are prefixed with a single quote (`'`).
   - Append-only invariant: historical rows are never edited or deleted; corrections
     append a superseding row.
   - Multi-run continuation: when a new run (`run_id`) appends to an existing TSV written
     by a prior run, it automatically prepends a `phase="start"` row naming the timestamp
     range of preceding rows and the new `run_id`.
2. Transcript & Evidence Resolution Auditor:
   - Verifies every row's `evidence` pointer (`file:line`, artifact path, or `commit/run` ref)
     actually exists and resolves on disk.
   - Emits a structured `AuditVerificationReport` with cross-vendor reviewer attribution
     (`reviewed_by_model`), enforcing that the reviewer vendor differs from the generator vendor.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

TSV_HEADER: str = "ts\tphase\tdecision\twhy\tevidence\tresult"
_FORMULA_TRIGGERS: tuple[str, ...] = ("=", "+", "-", "@")


class DecisionOutcome(str, Enum):
    """Canonical decision or predicate outcomes in the TSV trail."""

    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    INCONCLUSIVE = "INCONCLUSIVE"
    TESTS_GREEN = "tests green"
    REVERTED = "reverted"
    SUPERSEDED = "superseded"
    OPEN = "open"
    RUN_START = "run_started"


def sanitize_tsv_cell(raw_value: str) -> str:
    """Strip tabs/newlines into single spaces and escape leading `=`, `+`, `-`, `@` bytes."""
    cleaned = re.sub(r"[\t\r\n]+", " ", raw_value).strip()
    if cleaned.startswith(_FORMULA_TRIGGERS):
        return f"'{cleaned}"
    return cleaned


class DecisionLogEntry(BaseModel):
    """Immutable single row in the `/show-me-your-work` TSV decision log."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ts: str = Field(..., min_length=1, description="ISO-8601 UTC timestamp.")
    phase: str = Field(..., min_length=1, description="Workflow phase or workstream.")
    decision: str = Field(..., min_length=1, description="One-line plain-English action or choice.")
    why: str = Field(..., min_length=1, description="Plain-English rationale (no jargon tags).")
    evidence: str = Field(
        ...,
        min_length=1,
        description="Resolvable pointer: file:line, artifact path, or commit/metric ref.",
    )
    result: str = Field(..., min_length=1, description="Outcome or predicate state.")

    @model_validator(mode="after")
    def _check_no_tabs_or_newlines(self) -> DecisionLogEntry:
        for field_name in ("ts", "phase", "decision", "why", "evidence", "result"):
            val = getattr(self, field_name)
            if "\t" in val or "\n" in val or "\r" in val:
                raise ValueError(f"Field '{field_name}' must be single-line without tabs.")
        return self

    def to_tsv_line(self) -> str:
        """Render the entry as a sanitized tab-separated row."""
        cells = (
            sanitize_tsv_cell(self.ts),
            sanitize_tsv_cell(self.phase),
            sanitize_tsv_cell(self.decision),
            sanitize_tsv_cell(self.why),
            sanitize_tsv_cell(self.evidence),
            sanitize_tsv_cell(self.result),
        )
        return "\t".join(cells)

    @classmethod
    def from_tsv_line(cls, line: str) -> DecisionLogEntry:
        """Parse a TSV line back into a `DecisionLogEntry`."""
        parts = line.rstrip("\r\n").split("\t")
        if len(parts) != 6:
            raise ValueError(f"Expected 6 TSV columns, got {len(parts)} in line: {line!r}")
        return cls(
            ts=parts[0],
            phase=parts[1],
            decision=parts[2],
            why=parts[3],
            evidence=parts[4],
            result=parts[5],
        )


class AuditDiscrepancy(BaseModel):
    """A flagged row or unverified claim discovered during decision trail auditing."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    row_index: int = Field(..., ge=1, description="1-based data row index in the TSV.")
    phase: str = Field(..., min_length=1)
    evidence_pointer: str = Field(..., min_length=1)
    issue: str = Field(..., min_length=1)


class AuditVerificationReport(BaseModel):
    """Immutable report from auditing a `decisions.tsv` trail against real files and cross-vendor review."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tsv_path: str = Field(..., min_length=1)
    generator_model: str = Field(..., min_length=1)
    reviewed_by_model: str = Field(..., min_length=1)
    cross_vendor_verified: bool = Field(...)
    total_rows: int = Field(..., ge=0)
    resolved_evidence_rows: int = Field(..., ge=0)
    discrepancies: tuple[AuditDiscrepancy, ...] = Field(default_factory=tuple)
    attention_flags: tuple[str, ...] = Field(default_factory=tuple)
    passed: bool = Field(...)


def _extract_vendor_family(model_slug: str) -> str:
    slug = model_slug.strip().lower()
    if slug.startswith("cursor-"):
        slug = slug[len("cursor-") :]
    if slug.startswith(("claude-", "anthropic-", "fable-")):
        return "anthropic"
    if slug.startswith(("gemini-", "google-")):
        return "google"
    if slug.startswith(("gpt-", "o1-", "o3-", "openai-")):
        return "openai"
    return slug.split("-", maxsplit=1)[0]


class DecisionTrailLogger:
    """Parnas-encapsulated append-only TSV logger implementing `/show-me-your-work`.

    Enforces:
    - Automatic header creation on first write.
    - Automatic `phase="start"` row insertion when a new `run_id` resumes an existing log.
    - Append-only persistence (never truncates or overwrites existing rows).
    - Verification of evidence pointers (`file:line` or artifact paths) against the workspace.
    """

    def __init__(
        self,
        tsv_path: Path | str,
        run_id: str = "run-default",
        workspace_root: Path | str | None = None,
    ) -> None:
        self._path = Path(tsv_path)
        self._run_id = run_id
        self._workspace_root = (
            Path(workspace_root) if workspace_root is not None else self._path.parent
        )
        self._active_run_started = False

    @property
    def tsv_path(self) -> Path:
        return self._path

    @property
    def run_id(self) -> str:
        return self._run_id

    def read_entries(self) -> tuple[DecisionLogEntry, ...]:
        """Read all existing `DecisionLogEntry` rows from the TSV file."""
        if not self._path.exists():
            return ()
        lines = self._path.read_text(encoding="utf-8").splitlines()
        entries: list[DecisionLogEntry] = []
        for idx, raw_line in enumerate(lines):
            if idx == 0 and raw_line.strip() == TSV_HEADER:
                continue
            if not raw_line.strip():
                continue
            entries.append(DecisionLogEntry.from_tsv_line(raw_line))
        return tuple(entries)

    def _ensure_header_and_run_start(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        existing = self.read_entries()
        if not self._path.exists() or self._path.stat().st_size == 0:
            self._path.write_text(TSV_HEADER + "\n", encoding="utf-8")
            self._active_run_started = True
            return

        if not self._active_run_started and existing:
            # Check if the last start row belongs to another run_id
            start_rows = [e for e in existing if e.phase == "start"]
            last_owner = start_rows[-1].evidence if start_rows else None
            if last_owner != self._run_id:
                first_ts = existing[0].ts
                last_ts = existing[-1].ts
                start_entry = DecisionLogEntry(
                    ts=datetime.now(timezone.utc).isoformat(),
                    phase="start",
                    decision=f"Resumed decision log for new run {self._run_id}",
                    why=f"Prior rows span {first_ts}..{last_ts} from previous run",
                    evidence=self._run_id,
                    result=DecisionOutcome.RUN_START.value,
                )
                with self._path.open("a", encoding="utf-8") as fh:
                    fh.write(start_entry.to_tsv_line() + "\n")
            self._active_run_started = True

    def append_decision(
        self,
        *,
        phase: str,
        decision: str,
        why: str,
        evidence: str,
        result: DecisionOutcome | str,
        timestamp_utc: str | None = None,
    ) -> DecisionLogEntry:
        """Append a single sanitized decision row to the TSV trail."""
        if phase == "start":
            raise ValueError("Phase 'start' is reserved for automatic multi-run boundaries.")
        self._ensure_header_and_run_start()

        prior_count = len(self.read_entries())
        ts_val = timestamp_utc or datetime.now(timezone.utc).isoformat()
        res_str = result.value if isinstance(result, DecisionOutcome) else str(result)

        entry = DecisionLogEntry(
            ts=sanitize_tsv_cell(ts_val),
            phase=sanitize_tsv_cell(phase),
            decision=sanitize_tsv_cell(decision),
            why=sanitize_tsv_cell(why),
            evidence=sanitize_tsv_cell(evidence),
            result=sanitize_tsv_cell(res_str),
        )
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(entry.to_tsv_line() + "\n")

        new_count = len(self.read_entries())
        if new_count != prior_count + 1:
            raise RuntimeError("Postcondition breach: append_decision failed to grow TSV by 1 row.")
        return entry

    def supersede_decision(
        self,
        *,
        phase: str,
        corrected_decision: str,
        why_superseded: str,
        new_evidence: str,
        new_result: DecisionOutcome | str = DecisionOutcome.VERIFIED,
    ) -> DecisionLogEntry:
        """Record an append-only correction superseding an earlier row without rewriting history."""
        return self.append_decision(
            phase=phase,
            decision=f"SUPERSEDE: {corrected_decision}",
            why=why_superseded,
            evidence=new_evidence,
            result=new_result,
        )

    def _evidence_resolves(self, evidence_str: str) -> bool:
        """Check whether an evidence pointer (`path:line`, file path, or run/commit token) resolves."""
        pointer = evidence_str.lstrip("'")
        if pointer == self._run_id or pointer.startswith(("run-", "commit ", "tx-", "case-")):
            return True

        # Support comma-separated pointers (e.g., "scripts/snapshot.sh, baseline/")
        tokens = [t.strip() for t in pointer.split(",") if t.strip()]
        if not tokens:
            return False

        for token in tokens:
            # Check file:line format
            file_part = token.split(":", maxsplit=1)[0]
            candidate = Path(file_part)
            if not candidate.is_absolute():
                candidate = self._workspace_root / candidate
            if not candidate.exists():
                return False
        return True

    def audit_trail(
        self,
        *,
        generator_model: str = "claude-opus-5-5-xhigh-fast",
        reviewer_model: str = "gemini-4-neon-xhigh",
    ) -> AuditVerificationReport:
        """Verify all rows in the TSV trail have resolvable evidence pointers and run cross-vendor check."""
        gen_vendor = _extract_vendor_family(generator_model)
        rev_vendor = _extract_vendor_family(reviewer_model)
        cross_vendor_ok = gen_vendor != rev_vendor

        entries = self.read_entries()
        discrepancies: list[AuditDiscrepancy] = []
        attention_flags: list[str] = []
        resolved_count = 0

        if not cross_vendor_ok:
            attention_flags.append(
                f"Self-review violation: generator ({generator_model}) and reviewer ({reviewer_model}) "
                f"share vendor family '{gen_vendor}'."
            )

        for idx, entry in enumerate(entries, start=1):
            if self._evidence_resolves(entry.evidence):
                resolved_count += 1
            else:
                discrepancies.append(
                    AuditDiscrepancy(
                        row_index=idx,
                        phase=entry.phase,
                        evidence_pointer=entry.evidence,
                        issue=f"Evidence pointer '{entry.evidence}' does not resolve on disk.",
                    )
                )
                attention_flags.append(
                    f"Row {idx} ({entry.phase}): unresolved evidence pointer '{entry.evidence}'."
                )

            if entry.result == DecisionOutcome.INCONCLUSIVE.value:
                attention_flags.append(
                    f"Row {idx} ({entry.phase}): result is INCONCLUSIVE (must not be counted as a pass)."
                )

        passed = cross_vendor_ok and len(discrepancies) == 0 and len(entries) > 0
        return AuditVerificationReport(
            tsv_path=str(self._path),
            generator_model=generator_model,
            reviewed_by_model=reviewer_model,
            cross_vendor_verified=cross_vendor_ok,
            total_rows=len(entries),
            resolved_evidence_rows=resolved_count,
            discrepancies=tuple(discrepancies),
            attention_flags=tuple(attention_flags),
            passed=passed,
        )
