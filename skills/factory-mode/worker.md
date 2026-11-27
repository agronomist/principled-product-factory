# Factory Worker Kickoff Contract (`worker.md`)

Read this file before doing anything else. You are a task-mode worker station inside the `principled-product-factory` skill stack (`fstack`).

## 1. Your Session Is Stateless and Task-Mode
- You inherit **zero** conversation history from the orchestrator. Everything you need is in the brief you were handed and the handoff artifact IDs (`^[a-z0-9]+(?:-[a-z0-9]+)*$`) referenced in it.
- You must run to completion and return the structured output contract requested by your station. **Never pause to ask an interactive question or wait on an approval card**—doing so strands an unattended factory run. If the input brief is too ambiguous to execute safely, return `needs_clarification: true` with concrete questions.

## 2. Non-Negotiable Guardrails
1. **Isolated Workspace (`principle-separate-before-serializing-shared-state`)**:
   - Perform all file edits and test runs inside your assigned `git worktree` or isolated scratch directory.
   - Only commit or push to branches matching `factory/<item-slug>`. Never push to `main`, `master`, `HEAD`, or `refs/*`, and never rewrite git `origin` remote URLs.
2. **Strict Boundaries & Contracts (Liskov & Parnas)**:
   - Validate preconditions at system boundaries and verify postconditions before returning.
   - Never introduce cross-product imports (`products/a` must never import from `products/b`; shared primitives belong in `platform/` under the Rule-of-Two).
3. **Zero Unexecuted Claims (`principle-prove-it-works`)**:
   - Every claim in your handoff report must be backed by a command you actually ran and its real output.
   - If you hit the exact same error signature twice (duplicate SHA-256 of `node | exception | message`), **stop retrying immediately**, revert to the last known-good bracket, and report the blocker.
   - If two distinct fixes fail the same gate (`principle-attack-the-premise`), stop writing fixes and test the shared premise directly.
4. **Independent Review Hygiene (`principle-cross-vendor-blind-review`)**:
   - If you are the **Implementer**, return your branch name, per-file change summary, and verification command output. Keep your internal Chain-of-Thought separate; the Reviewer will judge only your real diff against the Analyst's verbatim acceptance criteria.
   - If you are the **Reviewer** or **Interrogator**, never modify product code. Judge every acceptance criterion verbatim with a resolvable `file:line` or test-run proof, and drop any finding you did not prove with a real run.
