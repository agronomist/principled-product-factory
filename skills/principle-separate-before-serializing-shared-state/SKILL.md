---
name: principle-separate-before-serializing-shared-state
description: Apply when concurrent stations, Arena candidates, or loops run in parallel. Give each actor its own isolated git worktree or state file, and bound active concurrency under Little's Law (WIP_LIMIT = 5).
---

# Principle: Separate Before Serializing Shared State

When concurrent workers might touch the same checkout, branch, or state file, eliminate the sharing first.

- Provision a dedicated `git worktree` (on an isolated `factory/<slug>` branch) or separate scratch directory for every concurrent station, Arena candidate, or verification harness drive.
- Merge only where state is read (e.g., Arena Phase E grafting).
- When a single shared resource is a true invariant (such as downstream model/DB capacity or a shared SQLite database), bound concurrency using **Little's Law** ($L = \lambda W$, `WIP_LIMIT = 5` — *Cruyff Total Football spacing / The Soup Nazi's 5-person queue*) and use ACID WAL mode (`PRAGMA journal_mode=WAL`) rather than uncoordinated file writes.
