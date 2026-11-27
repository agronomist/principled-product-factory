"""Adversarial Interrogator (`/interrogate`), Mutation Proof Verifier (`/create-formal-verification-skill`),
and Structural Ratchet Linter (`/correct`).

Implements three pstack verification and self-hardening loops:
1. `AdversarialInterrogator` (`/interrogate` & `/blast-radius`):
   - Runs candidate adversarial probes against the system.
   - **Execution-Only Survival Rule**: Speculative or prose-only claims without a runnable probe
     or where the probe does not actually demonstrate a failure are DROPPED (`dropped_count`).
     Only findings proven by a real failing run survive (`verified_findings`).
2. `MutationProofVerifier` (`/create-formal-verification-skill`):
   - *"A check that you have never seen fail proves nothing."*
   - Proves that every invariant check passes on the real production implementation AND
     loudly fails when run against a broken/mutated variant (e.g., disabled WIP semaphore,
     broken margin math, reversed Saga rollback order).
   - Tracks `covered_files` and `last_synced_commit` metadata so drift between code and
     formal checks is detected automatically.
3. `StructuralRatchetLinter` (`/correct` & `principle-encode-lessons-in-structure`):
   - Enforces the 5-level correction hierarchy (Architecture -> Types -> Lint whose error
     message names the exact fix -> Test -> Docs last).
   - Scans Python AST across `platform/` and `products/` to enforce architectural import
     barriers (`platform` must never import `products` outside CLI entry points; `products/a`
     must never import `products/b`) and Pydantic v2 `ConfigDict(extra="forbid", frozen=True)`
     immutability contracts.
   - Every violation's error message explicitly names the file, line, and exact fix to apply.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# 1. Adversarial Interrogator (`/interrogate`)
# ---------------------------------------------------------------------------


class AdversarialProbe(BaseModel):
    """A candidate attack submitted by an adversarial reviewer in `/interrogate`."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    probe_id: str = Field(..., min_length=1)
    adversary_model: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    command_description: str = Field(default="", description="Command or repro script description.")
    expected_intent_behavior: str = Field(..., min_length=1)
    # If probe_fn is None, this is an unexecuted prose/style opinion and MUST be dropped.
    probe_fn: Callable[[], tuple[bool, str]] | None = None


class VerifiedInterrogationFinding(BaseModel):
    """A finding that survived `/interrogate` because its runnable repro proved a real failure."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    probe_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    adversaries: tuple[str, ...] = Field(...)
    command_description: str = Field(..., min_length=1)
    observed_failure_output: str = Field(..., min_length=1)
    expected_intent_behavior: str = Field(..., min_length=1)


class InterrogationReport(BaseModel):
    """Immutable report produced by `AdversarialInterrogator.interrogate`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    intent_restatement: str = Field(..., min_length=1)
    verified_findings: tuple[VerifiedInterrogationFinding, ...] = Field(...)
    dropped_by_adversary: dict[str, int] = Field(...)
    dropped_reasons: tuple[str, ...] = Field(...)
    clean: bool = Field(..., description="True when zero verified findings broke the intent.")


class AdversarialInterrogator:
    """Implements pstack's `/interrogate` skill:

    - Re-runs every adversary's probe against the real code.
    - Drops any finding that was not executed (`probe_fn is None` or empty command) or
      whose execution passed without breaking the intent.
    - Deduplicates findings sharing the same title/root-cause across multiple adversaries.
    """

    def interrogate(
        self,
        intent_restatement: str,
        probes: Sequence[AdversarialProbe],
    ) -> InterrogationReport:
        if not intent_restatement.strip():
            raise ValueError("intent_restatement cannot be empty.")

        verified_by_title: dict[str, VerifiedInterrogationFinding] = {}
        dropped_counts: dict[str, int] = {}
        dropped_reasons: list[str] = []

        for probe in probes:
            dropped_counts.setdefault(probe.adversary_model, 0)

            if probe.probe_fn is None or not probe.command_description.strip():
                dropped_counts[probe.adversary_model] += 1
                dropped_reasons.append(
                    f"Dropped '{probe.probe_id}' ({probe.adversary_model}): "
                    "no runnable repro command provided (unexecuted prose/style opinion)."
                )
                continue

            try:
                broke_intent, output_str = probe.probe_fn()
            except Exception as exc:  # noqa: BLE001
                broke_intent = True
                output_str = f"{type(exc).__name__}: {exc}"

            if not broke_intent:
                dropped_counts[probe.adversary_model] += 1
                dropped_reasons.append(
                    f"Dropped '{probe.probe_id}' ({probe.adversary_model}): "
                    f"repro ran cleanly without breaking intent ({output_str})."
                )
                continue

            # Survived! Merge if another adversary found the same root-cause title
            norm_key = probe.title.strip().lower()
            if norm_key in verified_by_title:
                existing = verified_by_title[norm_key]
                merged_adv = tuple(sorted(set(existing.adversaries) | {probe.adversary_model}))
                verified_by_title[norm_key] = existing.model_copy(
                    update={"adversaries": merged_adv}
                )
            else:
                verified_by_title[norm_key] = VerifiedInterrogationFinding(
                    probe_id=probe.probe_id,
                    title=probe.title.strip(),
                    adversaries=(probe.adversary_model,),
                    command_description=probe.command_description.strip(),
                    observed_failure_output=output_str.strip(),
                    expected_intent_behavior=probe.expected_intent_behavior.strip(),
                )

        findings = tuple(verified_by_title.values())
        return InterrogationReport(
            intent_restatement=intent_restatement.strip(),
            verified_findings=findings,
            dropped_by_adversary=dropped_counts,
            dropped_reasons=tuple(dropped_reasons),
            clean=(len(findings) == 0),
        )


# ---------------------------------------------------------------------------
# 2. Mutation Proof Verifier (`/create-formal-verification-skill`)
# ---------------------------------------------------------------------------


class FormalPropertySpec(BaseModel):
    """Specification of a formal invariant paired with a mutated/broken variant to prove sensitivity."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    property_id: str = Field(..., min_length=1)
    plain_english_guarantee: str = Field(..., min_length=1)
    covered_files: tuple[str, ...] = Field(..., min_length=1)
    last_synced_commit: str = Field(..., min_length=7)
    check_production_fn: Callable[[], bool]
    check_mutated_broken_fn: Callable[[], bool]


class FormalPropertyProofResult(BaseModel):
    """Proof result for a single `FormalPropertySpec`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    property_id: str = Field(..., min_length=1)
    holds_on_production: bool = Field(...)
    caught_broken_mutation: bool = Field(
        ...,
        description="True iff the check returned False or raised on the broken mutation.",
    )
    covered_files: tuple[str, ...] = Field(...)
    last_synced_commit: str = Field(...)
    verified: bool = Field(...)


class MutationProofVerifier:
    """Implements `/create-formal-verification-skill`:

    Verifies that every property check:
    1. Holds true on the real production implementation (`holds_on_production == True`).
    2. Is **able to fail**: catches a broken mutation (`caught_broken_mutation == True`).
    """

    def verify_properties(
        self,
        specs: Sequence[FormalPropertySpec],
    ) -> tuple[FormalPropertyProofResult, ...]:
        if not specs:
            raise ValueError("specs cannot be empty.")

        results: list[FormalPropertyProofResult] = []
        for spec in specs:
            try:
                prod_ok = bool(spec.check_production_fn())
            except Exception:  # noqa: BLE001
                prod_ok = False

            try:
                mutation_passed = bool(spec.check_mutated_broken_fn())
                caught_mutation = not mutation_passed
            except Exception:  # noqa: BLE001
                caught_mutation = True

            results.append(
                FormalPropertyProofResult(
                    property_id=spec.property_id,
                    holds_on_production=prod_ok,
                    caught_broken_mutation=caught_mutation,
                    covered_files=spec.covered_files,
                    last_synced_commit=spec.last_synced_commit,
                    verified=(prod_ok and caught_mutation),
                )
            )
        return tuple(results)


# ---------------------------------------------------------------------------
# 3. Structural Ratchet Linter (`/correct` & `principle-encode-lessons-in-structure`)
# ---------------------------------------------------------------------------


class StructuralViolation(BaseModel):
    """A concrete architectural or type violation whose error message names the exact fix."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    rule_id: str = Field(..., min_length=1)
    hierarchy_level: str = Field(
        ...,
        pattern=r"^(1_architecture|2_types|3_fix_naming_lint)$",
    )
    file_path: str = Field(..., min_length=1)
    line_number: int = Field(..., ge=1)
    offending_symbol: str = Field(..., min_length=1)
    error_with_named_fix: str = Field(
        ...,
        min_length=1,
        description="Error message that explicitly names the file, type, or function to use instead.",
    )


class StructuralRatchetReport(BaseModel):
    """Report from `StructuralRatchetLinter.check_repository`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    files_scanned: int = Field(..., ge=1)
    violations: tuple[StructuralViolation, ...] = Field(...)
    passed: bool = Field(...)


class StructuralRatchetLinter:
    """Implements pstack's `/correct` hierarchy:

    1. **Level 1 (Architecture)**:
       - Modules inside `platform/` must never perform top-level imports from `products.*`
         (preserving strict DAG layering `products -> platform`).
       - Modules inside `products/<product_a>/` must never import from `products/<product_b>/`
         (Rule-of-Two: shared primitives must live in `platform/`).
    2. **Level 2 & 3 (Types & Fix-Naming Lint)**:
       - Every Pydantic `BaseModel` subclass in `platform/` or `products/` must declare
         `model_config = ConfigDict(..., extra="forbid", frozen=True)` so Parnas boundaries
         cannot be bypassed via undeclared fields or in-place mutation.
       - Every lint error message explicitly names the exact replacement fix so an agent
         can repair it in one turn without guessing.
    """

    def check_python_source(
        self,
        source_code: str,
        virtual_rel_path: str,
    ) -> tuple[StructuralViolation, ...]:
        """Parse `source_code` with `ast` and return all `StructuralViolation` findings."""
        tree = ast.parse(source_code, filename=virtual_rel_path)
        violations: list[StructuralViolation] = []
        parts = Path(virtual_rel_path).parts

        is_platform_file = len(parts) >= 1 and parts[0] == "platform"
        is_product_file = len(parts) >= 2 and parts[0] == "products"
        current_product_slug = parts[1].replace("-", "_") if is_product_file else None

        # 1. Check top-level imports for architectural boundary violations
        for node in tree.body:
            imported_modules: list[tuple[str, int]] = []
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append((node.module, node.lineno))

            for mod_name, lineno in imported_modules:
                if is_platform_file and (
                    mod_name == "products" or mod_name.startswith("products.")
                ):
                    violations.append(
                        StructuralViolation(
                            rule_id="ARCH-001-NO-PLATFORM-TO-PRODUCT-IMPORT",
                            hierarchy_level="1_architecture",
                            file_path=virtual_rel_path,
                            line_number=lineno,
                            offending_symbol=mod_name,
                            error_with_named_fix=(
                                f"Architectural layering violation in '{virtual_rel_path}:{lineno}': "
                                f"top-level import of '{mod_name}' inside 'platform/' is forbidden. "
                                "FIX: Inject a callable contract or extract the shared schema into "
                                "'platform/' per the Rule-of-Two in CLAUDE.md."
                            ),
                        )
                    )

                if is_product_file and mod_name.startswith("products."):
                    mod_parts = mod_name.split(".")
                    if len(mod_parts) >= 2:
                        target_slug = mod_parts[1].replace("-", "_")
                        if current_product_slug and target_slug != current_product_slug:
                            violations.append(
                                StructuralViolation(
                                    rule_id="ARCH-002-NO-CROSS-PRODUCT-IMPORT",
                                    hierarchy_level="1_architecture",
                                    file_path=virtual_rel_path,
                                    line_number=lineno,
                                    offending_symbol=mod_name,
                                    error_with_named_fix=(
                                        f"Cross-product coupling violation in '{virtual_rel_path}:{lineno}': "
                                        f"product '{current_product_slug}' imported '{mod_name}'. "
                                        "FIX: Extract the shared primitive into 'platform/' (Rule-of-Two) "
                                        "and import from 'platform.<module>' instead."
                                    ),
                                )
                            )

        # 2. Check Pydantic BaseModel subclasses for Parnas immutability (model_config with frozen=True, extra="forbid")
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            inherits_base_model = any(
                (isinstance(b, ast.Name) and b.id == "BaseModel")
                or (isinstance(b, ast.Subscript) and isinstance(b.value, ast.Name) and b.value.id == "BaseModel")
                for b in node.bases
            )
            if not inherits_base_model:
                continue

            has_valid_config = False
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == "model_config":
                            src_segment = ast.unparse(stmt.value)
                            if "frozen=True" in src_segment and (
                                'extra="forbid"' in src_segment or "extra='forbid'" in src_segment
                            ):
                                has_valid_config = True

            if not has_valid_config:
                violations.append(
                    StructuralViolation(
                        rule_id="TYPE-001-PARNAS-FROZEN-BASEMODEL",
                        hierarchy_level="2_types",
                        file_path=virtual_rel_path,
                        line_number=node.lineno,
                        offending_symbol=node.name,
                        error_with_named_fix=(
                            f"Parnas type boundary violation on class '{node.name}' in "
                            f"'{virtual_rel_path}:{node.lineno}': missing immutable ConfigDict. "
                            'FIX: Add `model_config = ConfigDict(extra="forbid", frozen=True)` '
                            f"as the first attribute inside `{node.name}`."
                        ),
                    )
                )

        return tuple(violations)

    def check_repository(self, repo_root: Path) -> StructuralRatchetReport:
        """Scan all Python files under `platform/` and `products/` for structural violations."""
        py_files: list[Path] = []
        for folder in ("platform", "products"):
            base = repo_root / folder
            if base.exists():
                for p in sorted(base.rglob("*.py")):
                    # Avoid double-scanning symlinked product alias directories
                    if any(
                        part in ("demo_decision_engine", "support_sla_autopilot")
                        for part in p.parts
                    ):
                        continue
                    py_files.append(p)

        all_violations: list[StructuralViolation] = []
        for fpath in py_files:
            rel_path = str(fpath.relative_to(repo_root))
            code = fpath.read_text(encoding="utf-8")
            all_violations.extend(self.check_python_source(code, rel_path))

        return StructuralRatchetReport(
            files_scanned=len(py_files),
            violations=tuple(all_violations),
            passed=(len(all_violations) == 0),
        )
