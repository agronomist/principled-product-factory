---
name: principle-clean-cutting-boards
description: Apply when concurrent line stations, Cook-Off contenders, or tasting loops run in parallel. Give each cook its own isolated git worktree cutting board or prep tub, and cap active orders on the ticket rail under Little's Law (WIP_LIMIT = 5).
---

# Principle: Clean Cutting Boards (Separate Before Serializing Shared State)

Never chop raw poultry and fresh herbs on the same cutting board. When concurrent line cooks might touch the same checkout, branch, or state file, eliminate the sharing first.

- Provision a dedicated `git worktree` cutting board (on an isolated `factory/<slug>` branch) or separate scratch prep tub for every concurrent station, Cook-Off contender, or live tasting run.
- Combine elements only at plating time (e.g., Cook-Off Phase E grafting).
- When a single shared resource is a true kitchen invariant (such as oven capacity or a shared SQLite walk-in ledger), bound active orders on the rail using **Little's Law** ($L = \lambda W$, `WIP_LIMIT = 5` — *Total Football pitch spacing / the strict 5-ticket counter queue*) and use ACID WAL mode (`PRAGMA journal_mode=WAL`).
