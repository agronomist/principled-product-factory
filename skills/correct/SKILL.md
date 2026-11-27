---
name: correct
description: Self-hardening structural ratchet skill. Finds mistake classes agents repeat in the repository and makes each one impossible using a 5-level hierarchy (1. Architecture -> 2. Types -> 3. Lint whose error message names the exact fix -> 4. Test -> 5. Docs last), proving each check fails on a real past mistake. Use for /correct.
---

# Correct — Structural Ratchet (`/correct`)

Assume every future contributor is an agent that sees only the file it opened, copies the nearest example, and takes the shortest path that passes. When an operator corrects a mistake or an incident occurs twice, **change the repository so the next agent cannot make that mistake.**

## 1. Fix Each Mistake Class at the Highest Level That Works

Always climb as high up this 5-level hierarchy as possible:

1. **Level 1 — Eliminate it with Architecture**:
   - Give each piece of state one owner and each task one supported path.
   - Enforce topological isolation (`platform/` never imports from `products/`; `products/a` never imports from `products/b`; self-delegation is disabled via `disableTool()`).
   - Delete dead code and legacy wrappers an agent might copy (`principle-subtract-before-you-add`).
2. **Level 2 — Enforce it with Types**:
   - Make illegal states unrepresentable (`frozen=True, extra="forbid"` schemas, exhaustive enums, branded IDs validated by anchored regex `^[a-z0-9]+(?:-[a-z0-9]+)*$`).
3. **Level 3 — Enforce it with a Lint Whose Error Message Names the Exact Fix**:
   - If bad code or a broken skill still parses, add a fast check (`skills/factory-mode/scripts/validate-skills.sh` or AST linter) whose error output explicitly writes:
     `ERROR: <what broke>. FIX: <exact file, function, or attribute to use instead>.`
4. **Level 4 — Test the Observable Behavior**:
   - Write a behavioral test or formal property check that fails when user-visible behavior breaks and passes when internals refactor.
5. **Level 5 — Write Docs or Agent Rules Last**:
   - Prose instructions are only for judgment calls that cannot be encoded structurally. *Nothing fails when an agent skips a paragraph of docs.*

## 2. Prove the Check Fails on the Real Mistake

A check you have never seen fail proves nothing (`/create-formal-verification-skill`).
1. Introduce (or replay) the real broken state.
2. Run the check and confirm it **fails loudly** with the fix-naming error message.
3. Restore the fix and confirm the check passes (`0` exit code).

## 3. Maintain the Rule-to-Enforcer Table in `CLAUDE.md`

Pair every rule in `CLAUDE.md` with the exact script, schema, or structural gate that enforces it. If a rule is in `CLAUDE.md` with no structural enforcer and gets violated again, upgrade it to Level 1–3 in the same commit.
