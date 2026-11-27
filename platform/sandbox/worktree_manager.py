"""Real Git Worktree Sandbox Manager (`platform/sandbox/worktree_manager.py`).

Implements `pstack`'s `principle-separate-before-serializing-shared-state` and Vercel `eve`'s
sandbox isolation rules using real Git worktrees (`git worktree add` / `git worktree remove`):

1. **Inert-by-Construction Branch Validation**:
   Every worktree branch is validated via `validate_branch_name(branch_name, required_prefix="factory/")`
   before a single git command runs. Direct checkouts of `main`, `master`, `HEAD`, `refs/*`,
   or shell metacharacters are rejected immediately.
2. **Real Isolated Checkout (`git worktree add -B <factory/branch> <worktree_path> HEAD`)**:
   Spawns a real git worktree on disk so the Implementer station or Arena candidate can modify
   files, run `pytest` or `StructuralRatchetLinter`, and commit changes without touching the
   parent checkout.
3. **Real Diff & Commit Capture (`git status`, `git diff`, `git commit`)**:
   Stages changes inside the worktree, commits them to the `factory/*` branch, captures the
   changed file summary and unified patch diff (`git diff HEAD~1..HEAD`), and returns an
   immutable `WorktreeExecutionResult`.
4. **Deterministic Cleanup (`git worktree remove --force` & `git worktree prune`)**:
   Guarantees that temporary worktree directories are removed in a `finally` block while the
   committed `factory/*` git branch ref and captured diff evidence survive for the Reviewer
   station.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from pydantic import BaseModel, ConfigDict, Field

from platform.foreman.stations import validate_branch_name


class WorktreeSession(BaseModel):
    """Immutable metadata for an active isolated `git worktree` checkout."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_id: str = Field(..., min_length=1)
    branch_name: str = Field(..., min_length=1)
    worktree_path: str = Field(..., min_length=1)
    base_commit_sha: str = Field(..., min_length=7)


class WorktreeExecutionResult(BaseModel):
    """Immutable result of running an Implementer or Arena task inside a real Git worktree."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_id: str = Field(..., min_length=1)
    branch_name: str = Field(..., min_length=1)
    base_commit_sha: str = Field(..., min_length=7)
    head_commit_sha: str = Field(..., min_length=7)
    changed_files: dict[str, str] = Field(...)
    unified_diff: str = Field(...)
    verification_passed: bool = Field(...)
    verification_output: str = Field(..., min_length=1)
    worktree_cleaned_up: bool = Field(...)


class GitWorktreeSandbox:
    """Manages real isolated `git worktree` checkouts for Implementer stations and Arena runners."""

    def __init__(
        self,
        repo_root: Path,
        worktrees_root: Path,
        branch_prefix: str = "factory/",
    ) -> None:
        self._repo_root = Path(repo_root).resolve()
        self._worktrees_root = Path(worktrees_root).resolve()
        self._branch_prefix = branch_prefix

    def _run_git(self, args: list[str], cwd: Path | None = None) -> str:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd or self._repo_root),
            capture_output=True,
            text=True,
            timeout=15.0,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"git {' '.join(args)} failed (code {proc.returncode}): {proc.stderr.strip()}"
            )
        return proc.stdout.strip()

    @contextmanager
    def open_worktree(
        self,
        session_id: str,
        branch_name: str,
    ) -> Iterator[WorktreeSession]:
        """Provision a real `git worktree` on `branch_name` and remove the directory on exit."""
        branch_err = validate_branch_name(branch_name, required_prefix=self._branch_prefix)
        if branch_err is not None:
            raise PermissionError(f"Worktree branch validation failed: {branch_err}")

        self._worktrees_root.mkdir(parents=True, exist_ok=True)
        wt_path = self._worktrees_root / f"wt-{session_id}"
        if wt_path.exists():
            self._cleanup_worktree_path(wt_path)

        base_sha = self._run_git(["rev-parse", "HEAD"])
        self._run_git(["worktree", "add", "-B", branch_name, str(wt_path), base_sha])

        # Configure local committer identity inside the repository/worktree if not set
        self._run_git(["config", "user.name", "Principled Factory Bot"], cwd=wt_path)
        self._run_git(["config", "user.email", "factory-bot@principled.local"], cwd=wt_path)

        session = WorktreeSession(
            session_id=session_id,
            branch_name=branch_name,
            worktree_path=str(wt_path),
            base_commit_sha=base_sha,
        )
        try:
            yield session
        finally:
            self._cleanup_worktree_path(wt_path)

    def _cleanup_worktree_path(self, wt_path: Path) -> None:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(wt_path)],
            cwd=str(self._repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if wt_path.exists():
            shutil.rmtree(wt_path, ignore_errors=True)
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=str(self._repo_root),
            capture_output=True,
            text=True,
            check=False,
        )

    def execute_in_worktree(
        self,
        *,
        session_id: str,
        branch_name: str,
        commit_message: str,
        apply_changes_fn: Callable[[Path], dict[str, str]],
        verify_worktree_fn: Callable[[Path], tuple[bool, str]],
    ) -> WorktreeExecutionResult:
        """Provision a git worktree, run `apply_changes_fn(wt_path)`, run `verify_worktree_fn(wt_path)`,
        commit the change to `branch_name`, capture the real `git diff`, and tear down the worktree directory.
        """
        wt_dir_ref: Path | None = None
        with self.open_worktree(session_id=session_id, branch_name=branch_name) as session:
            wt_path = Path(session.worktree_path)
            wt_dir_ref = wt_path

            changed_summary = apply_changes_fn(wt_path)
            verified_ok, verify_out = verify_worktree_fn(wt_path)

            self._run_git(["add", "-A"], cwd=wt_path)
            status_porcelain = self._run_git(["status", "--porcelain"], cwd=wt_path)
            if status_porcelain:
                self._run_git(["commit", "-m", commit_message], cwd=wt_path)

            head_sha = self._run_git(["rev-parse", "HEAD"], cwd=wt_path)
            diff_patch = self._run_git(
                ["diff", session.base_commit_sha, head_sha], cwd=wt_path
            )

        cleaned = wt_dir_ref is not None and not wt_dir_ref.exists()
        return WorktreeExecutionResult(
            session_id=session_id,
            branch_name=branch_name,
            base_commit_sha=session.base_commit_sha,
            head_commit_sha=head_sha,
            changed_files=changed_summary,
            unified_diff=diff_patch,
            verification_passed=verified_ok,
            verification_output=verify_out,
            worktree_cleaned_up=cleaned,
        )
