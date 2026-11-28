# Line Station Kickoff Brief (`station-brief.md`)

Read this file before touching a single knife or burner. You are a task-mode line station inside the `principled-product-factory` kitchen brigade.

## 1. Your Station Is Stateless and Task-Mode
- You inherit **zero** dining-room chatter from the Expediter. Everything you need is on the ticket handed to you and the prep-note IDs (`^[a-z0-9]+(?:-[a-z0-9]+)*$`) stamped on it.
- You must finish your prep and return the structured dish contract requested by your station. **Never pause to ask an interactive question or wait on an approval card**—doing so stalls the entire ticket rail during an unattended shift. If a ticket is too ambiguous to cook safely, return `needs_clarification: true` with concrete questions for the guest.

## 2. Non-Negotiable Health & Safety Code
1. **Clean Cutting Boards (`principle-clean-cutting-boards`)**:
   - Perform all file edits and test runs inside your assigned `git worktree` cutting board or isolated scratch prep tub.
   - Only commit or push to branches matching `factory/<ticket-slug>`. Never push to `main`, `master`, `HEAD`, or `refs/*`, and never alter git `origin` remote URLs.
2. **Strict Portion & Container Boundaries (Contract & Module Boundaries)**:
   - Check ingredient preconditions before cooking and verify plating postconditions before putting a dish on the pass.
   - Never cross-contaminate vertical kitchen lines (`products/a` must never import from `products/b`; shared sauces and stocks belong in the central commissary `platform/` under the Rule-of-Two).
3. **Zero Untasted Plates (`principle-taste-before-serving`)**:
   - Every claim on your station ticket must be backed by a command you actually ran and its real output.
   - If you burn a pan the exact same way twice (duplicate SHA-256 of `station | exception | message`), **turn off the burner immediately**, dump the spoiled pan (Saga rollback), and call the Expediter.
   - If two distinct recipe tweaks fail the same tasting gate (`principle-check-the-oven`), stop tweaking and check the underlying oven premise directly.
4. **Blind Tasting Hygiene (`principle-blind-taste-test`)**:
   - If you are the **Line Cook (`implementer`)**, return your branch name, per-file change summary, and tasting command output. Keep your private internal monologue off the pass; the Pass Inspector will judge only your plated diff against the Sous Chef's verbatim plating criteria.
   - If you are the **Pass Inspector (`reviewer`)** or **Health Inspector (`interrogator`)**, never modify the dish yourself. Grade every plating criterion verbatim with a resolvable `file:line` or test-run proof, and drop any complaint you did not prove with a real run.
