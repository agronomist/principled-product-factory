---
name: principle-attack-the-premise
description: Apply when two fixes that share one premise fail the same gate, or when a retry produces a duplicate SHA-256 error signature. Stop writing fixes, write the shared premise down, and test it directly; on duplicate error signatures, halt retries immediately and run Saga rollback.
---

# Principle: Attack the Premise

When two or more fixes that share one premise fail the same gate, suspect the premise, not the fixes.

- Write down the single sentence every failed fix assumed.
- Design and run a read-only observation probe that would come out differently if that premise were false **before** writing fix #3.
- **Duplicate Error-Signature Halt**: When a node retry produces an identical SHA-256 error signature (`SHA256(node_id | exception_type | normalized_message)` — *George Costanza parallel parking the same impossible angle twice*), halt retries immediately, execute reverse-topological Saga compensating rollbacks, and escalate.
