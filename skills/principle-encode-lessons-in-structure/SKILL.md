---
name: principle-encode-lessons-in-structure
description: Apply when you catch yourself writing the same instruction twice or fixing a recurring mistake class. Encode the lesson structurally using the 5-level hierarchy (Architecture -> Types -> Lint whose error names the fix -> Test -> Docs last).
---

# Principle: Encode Lessons in Structure

When an agent or developer makes the same mistake twice, prose instructions are the symptom, not the cure (*nothing fails when an agent skips a paragraph of docs*).

- Climb to the highest level in the `/correct` hierarchy:
  1. **Architecture** (make the bad state or import impossible, e.g., Rule-of-Two extraction into `platform/`).
  2. **Types** (immutable schemas with `extra="forbid", frozen=True` and regex-anchored IDs).
  3. **Lint with Fix-Naming Error** (an executable check whose failure message explicitly writes `FIX: <exact replacement>`).
  4. **Behavioral Test** (asserting user-observable outcomes).
  5. **Docs Last** (only for pure judgment calls).
