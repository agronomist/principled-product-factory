---
name: sharpen-the-knives
description: Self-hardening kitchen structural ratchet skill. Finds accident classes line cooks repeat in the repository and makes each one impossible using a 5-level hierarchy (1. Kitchen Layout/Architecture -> 2. Labeled Containers/Types -> 3. Alarm that names the exact fix/Lint -> 4. Taste Test -> 5. Wall Sign/Docs last), proving each check fails on a real past accident. Use for /sharpen-the-knives.
---

# Sharpen the Knives — Structural Ratchet (`/sharpen-the-knives`)

Assume every future line cook is working a Saturday-night rush, sees only the station they walked up to, copies the nearest prep tub, and takes the fastest shortcut that plates. When the Head Chef corrects a mistake or a kitchen accident happens twice, **redesign the station so the next cook cannot make that mistake.**

## 1. Fix Each Accident Class at the Highest Level That Works

Always climb as high up this 5-level hierarchy as possible:

1. **Level 1 — Eliminate it with Kitchen Layout (Architecture)**:
   - Give each prep stock one owner and each task one supported path.
   - Enforce topological station isolation (`platform/` central commissary never imports from `products/`; `products/a` never imports from `products/b`; self-delegation is disabled).
   - Throw out spoiled ingredients and legacy wrappers a hurried cook might copy.
2. **Level 2 — Enforce it with Labeled Containers (Types)**:
   - Make illegal states unrepresentable (`frozen=True, extra="forbid"` schemas, exhaustive enums, prep-note IDs validated by anchored regex `^[a-z0-9]+(?:-[a-z0-9]+)*$`).
3. **Level 3 — Enforce it with an Alarm Whose Error Message Names the Exact Fix (Lint)**:
   - If a bad recipe or broken skill still parses, add a fast check (`skills/head-chef-mode/scripts/validate-skills.sh` or AST linter) whose error output explicitly writes:
     `ERROR: <what broke>. FIX: <exact file, function, or attribute to use instead>.`
4. **Level 4 — Taste the Observable Dish (Test)**:
   - Write a behavioral test or formal HACCP property check that fails when guest-visible behavior breaks and passes when internal prep refactors.
5. **Level 5 — Put Up a Wall Sign Last (Docs)**:
   - Prose rules are only for judgment calls that cannot be encoded structurally. *Nothing stops a rush-hour fire when a cook skips a laminated sign on the wall.*

## 2. Prove the Alarm Rings on the Real Accident

An alarm you have never heard ring proves nothing (`/haccp-statechart`).
1. Introduce (or replay) the real broken state.
2. Run the check and confirm it **fails loudly** with the fix-naming error message.
3. Restore the fix and confirm the check passes (`0` exit code).

## 3. Maintain the Health-Code Table in `CLAUDE.md`

Pair every rule in `CLAUDE.md` with the exact script, schema, or playbook that enforces it.
