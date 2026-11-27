# Playbook: Ticket to the Pass (`ticket-to-pass.md`)

Use this playbook when an order arrives from GitHub (`factory` label or `@mention`), a Linear ticket, or the user asks to turn a ticket into a plated Draft Pull Request.

## Todo List Steps (Copy into Todo Tool First)

1. **Check the Master Recipe Book & Stamp Guest Trust (`kitchen-brigade`)**:
   - Read the Master Recipe Book (`factory-brain/<sha256(repo)>.md`) for kitchen quirks, tasting gotchas, and recurring inspection findings.
   - Stamp the caller's trust class (`unattended_autonomous`, `trusted_interactive`, or `dev_tui`).
   - Log a `frame` row to `decisions.tsv` via [`../../prep-log/SKILL.md`](../../prep-log/SKILL.md).
2. **Station 1 — Host Triage (`kitchen-brigade`)**:
   - Spawn `host_triage` (`classifier`) starting with `Read <path>/station-brief.md before anything else.`
   - Classify `work_type` (`bug | feature | refactor | perf | chore`), `priority`, `complexity`, `affected_area`, and `needs_clarification`.
   - **86 Rule**: If `needs_clarification == true`, post the questions on the intake ticket and **halt immediately**. Never leave an unattended stove lit waiting for an answer.
3. **No-Empty-Calories & Food-Cost Gates (`no-empty-calories` + `food-cost-guard`)**:
   - If `work_type == "feature"`, run [`../../no-empty-calories/SKILL.md`](../../no-empty-calories/SKILL.md). Verify Ulwick JTBD Opportunity Score $\ge 10.0$ and real guest skin-in-the-game (*The Mom Test*). Block if speculative (*"diners at some point might order it"*).
   - Run [`../../food-cost-guard/SKILL.md`](../../food-cost-guard/SKILL.md) to confirm unit contribution margin $\ge M_{\min}$ and $\text{EVOI} > \text{Cost}$.
4. **Station 2 — Sous Chef Planner (+ Optional Forager) (`kitchen-brigade` + `mise-en-place`)**:
   - If external ingredients (upstream bugs, library versions) are needed, spawn `forager_researcher` first and save its memo as a pass-by-ID prep note (`^[a-z0-9]+(?:-[a-z0-9]+)*$`).
   - Spawn `sous_chef_planner` (`analyst`) against a live checkout to produce ordered prep steps, risks, **verbatim plating criteria**, and an analysis prep-note ID.
   - If the change crosses module boundaries, run [`../../mise-en-place/SKILL.md`](../../mise-en-place/SKILL.md) to lock in types and signatures first. If it's a contested One-Way Door, run [`../../cook-off/SKILL.md`](../../cook-off/SKILL.md).
5. **Station 3 — Line Cook (`kitchen-brigade`)**:
   - Provision an isolated `git worktree` cutting board on branch `factory/<ticket-id>` (`principle-clean-cutting-boards`).
   - Spawn `line_cook_implementer` with the self-contained ticket brief (order verbatim + prep-note ID + plating criteria).
   - Inside the worktree, run [`../../cross-contamination/SKILL.md`](../../cross-contamination/SKILL.md) and the project's tasting harness ([`../../taste-the-dish/SKILL.md`](../../taste-the-dish/SKILL.md)). Commit to `factory/<ticket-id>`.
6. **Station 4 — Blind Pass Inspector (`kitchen-brigade` + `health-inspector`)**:
   - Spawn `pass_inspector` (`reviewer`) on a **different model vendor** than `line_cook_implementer` (`principle-blind-taste-test`).
   - Pass only the ticket, verbatim plating criteria, prep-note ID, pushed `factory/<ticket-id>` diff, and tasting output—**never** the Line Cook's internal monologue.
   - On `request_changes` (refire), route findings back to a fresh Line Cook and re-taste, capped at **at most 2 refires** (`MAX_REVISION_ROUNDS = 2`). If the plate still fails after 2 refires, 86 the ticket and report unresolved findings without opening a PR.
7. **Plate Draft PR at the Pass & Audit the Prep Log**:
   - When `pass_inspector` returns `approve`, open a **Draft Pull Request** (`draft: true`, per `principle-plate-at-the-pass`), written through [`../../plain-english-menu/SKILL.md`](../../plain-english-menu/SKILL.md).
   - Audit `decisions.tsv` against the transcript with a cross-vendor taster (`prep-log`) and include the `Attention` block in the final handoff.
