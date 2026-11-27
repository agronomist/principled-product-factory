---
name: principle-kitchen-muscle-memory
description: Apply when you catch yourself giving the same correction twice or fixing a recurring kitchen accident. Encode the lesson into kitchen muscle memory using the 5-level hierarchy (1. Kitchen Layout/Architecture -> 2. Labeled Containers/Types -> 3. Alarm that names the fix/Lint -> 4. Taste Test -> 5. Wall Sign/Docs last).
---

# Principle: Kitchen Muscle Memory (Encode Lessons in Structure)

When a line cook makes the same mistake twice during a rush, putting up another laminated sign on the wall is the symptom, not the cure (*nobody reads wall signs during a Saturday-night rush*).

- Climb to the highest level in the `/sharpen-the-knives` hierarchy:
  1. **Kitchen Layout (Architecture)** — Make the wrong reach or cross-line import impossible (e.g., Rule-of-Two extraction into the central commissary `platform/`).
  2. **Labeled Containers (Types)** — Immutable schemas (`extra="forbid", frozen=True`) and regex-anchored prep-note IDs.
  3. **Alarm with Fix-Naming Error (Lint)** — An executable check whose failure message explicitly writes `FIX: <exact replacement>`.
  4. **Taste Test (Behavioral Test)** — Asserting diner-observable outcomes.
  5. **Wall Sign Last (Docs)** — Only for pure culinary judgment calls.
