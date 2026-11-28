---
name: haccp-statechart
description: Formally verify critical kitchen state machines, concurrency limits (WIP_LIMIT = 5), retry loops, Saga pan-dumping, and 3-tier pantry circuit breakers where ordinary tests rarely reach. Proves checks fail on a spoiled mutation, tracks last_synced_commit, and draws shortest-path Mermaid statecharts for any hazard violation. Use for /haccp-statechart.
---

# HACCP Formal Verification & Statechart (`/haccp-statechart`)

In commercial kitchens, **HACCP (Hazard Analysis Critical Control Points)** formally proves that food never sits in the temperature danger zone across any sequence of prep steps. In software, tests only check the paths someone thought to write; formal verification checks **every possible interleaving of states** up to a stated bound.

## 1. Pick the Critical Control Point Where a Bug Costs the Most
Target the state machines where race conditions or bad state transitions cause catastrophic outages or margin bleed:
- Little's Law WIP semaphore (`WIP_LIMIT = 5`).
- 3-tier pantry circuit breaker transitions (`CLOSED -> OPEN -> HALF_OPEN -> CLOSED`).
- Duplicate SHA-256 burn-signature detection and reverse-topological Saga rollbacks.
- Foreman bounded refire loops (`MAX_REVISION_ROUNDS = 2`).

## 2. What Makes a HACCP Verification Valid
1. **True to the Real Code**: Every state and transition in the model maps 1-to-1 to a real function and state field in the repository.
2. **Able to Fail (Mutation Proof)**: *A check you have never seen fail proves nothing.* Run the property verifier against a broken/mutated variant (e.g., off-by-one WIP limit or reversed Saga compensation order) and confirm it catches the hazard loud and fast.
3. **Commit-Synced Drift Tracking**: Record `covered_files` and `last_synced_commit` inside the verification spec. Whenever `git diff <last_synced_commit>..HEAD` touches a covered file, flag that the formal model must be re-verified.

## 3. Render a Mermaid Statechart of Every State & Counterexample
Always include a `mermaid` `stateDiagram-v2` showing the verified state transitions—and if any invariant breaks, highlight the **shortest counterexample path** from initial state to the hazard state in plain words.
