"""Isolated Git Worktree Sandbox Manager (`platform/sandbox/`).

Provisions real isolated `git worktree` checkouts on inert `factory/*` branches so concurrent
Implementer stations and Arena candidates can modify repository files, run `pytest` and AST
ratchets, capture real `git diff` patches, and tear down worktrees cleanly without touching
the user's primary working tree.
"""

from platform.sandbox.worktree_manager import (
    GitWorktreeSandbox,
    WorktreeExecutionResult,
    WorktreeSession,
)

__all__ = [
    "GitWorktreeSandbox",
    "WorktreeExecutionResult",
    "WorktreeSession",
]
