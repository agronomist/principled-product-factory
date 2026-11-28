# Playbook: Ticket to the Pass (`ticket-to-pass.md`)

Use this playbook when an order arrives from GitHub (`factory` label or `@mention`), a Linear ticket, or the user asks to turn a ticket into a plated Draft Pull Request.

## Todo List Steps (Copy into Todo Tool First)

1. **4:30 PM Pre-Shift Walk-In Check & Master Recipe Book (`pre-shift-lineup` + `kitchen-brigade`)**:
   - Run `bash skills/head-chef-mode/scripts/pre-shift-check.sh` ([`../../pre-shift-lineup/SKILL.md`](../../pre-shift-lineup/SKILL.md)) to verify `main` is clean, check active `factory/*` cutting boards (`WIP <= 5`), and scan for spoiled `FIFO-DATE-DOT` containers.
   - Read the Master Recipe Book (`factory-brain/<sha256(repo)>.md`) for kitchen quirks, tasting gotchas, and recurring inspection findings.
   - Stamp the caller's trust class (`unattended_autonomous`, `trusted_interactive`, or `dev_tui`) and log a `frame` row to `decisions.tsv` via [`../../prep-log/SKILL.md`](../../prep-log/SKILL.md).
2. **Station 1 — Host Triage & Purple-Board Allergy Check (`kitchen-brigade` + `allergy-alert`)**:
   - Spawn `host_triage` (`classifier`) starting with `Read <path>/station-brief.md before anything else.`
   - Classify `work_type` (`bug | feature | refactor | perf | chore`), `priority`, `complexity`, `affected_area`, `purple_board_allergy`, `amuse_bouche_candidate`, and `needs_clarification`.
   - **Purple-Board Allergy Rule ([`../../allergy-alert/SKILL.md`](../../allergy-alert/SKILL.md))**: If `purple_board_allergy == true` (Auth, Multi-Tenant SQL Isolation, Billing, Secrets/Crypto, PII, or Destructive Migrations), forbid `fast_implement` shortcuts and mandate negative exploit criteria + `clean-station.sh --allergy`.
   - **86 Rule**: If `needs_clarification == true`, post the questions on the intake ticket and **halt immediately**. Never leave an unattended stove lit waiting for an answer.
3. **No-Empty-Calories, Food-Cost & Amuse-Bouche Gates (`no-empty-calories` + `food-cost-guard` + `amuse-bouche`)**:
   - If `work_type == "feature"`, run [`../../no-empty-calories/SKILL.md`](../../no-empty-calories/SKILL.md). Verify Ulwick JTBD Opportunity Score $\ge 10.0$ and real guest skin-in-the-game (*The Mom Test*). Block if speculative (*"diners at some point might order it"*).
   - Run [`../../food-cost-guard/SKILL.md`](../../food-cost-guard/SKILL.md) to confirm unit contribution margin $\ge M_{\min}$ and $\text{EVOI} > \text{Cost}$.
   - If `amuse_bouche_candidate == true` (`Stage A` 0-to-1 user-facing feature), serve a 5-minute single-bite prototype via [`../../amuse-bouche/SKILL.md`](../../amuse-bouche/SKILL.md) before authorizing full database plumbing.
4. **Station 2 — Sous Chef Planner (+ Optional Forager) (`kitchen-brigade` + `mise-en-place`)**:
   - If external ingredients (upstream bugs, library versions) are needed, spawn `forager_researcher` first and save its memo as a pass-by-ID prep note (`^[a-z0-9]+(?:-[a-z0-9]+)*$`).
   - Spawn `sous_chef_planner` (`analyst`) against a live checkout to produce ordered prep steps, risks, **verbatim plating criteria** (including negative allergen criteria when `purple_board_allergy == true`), and an analysis prep-note ID.
   - If the change crosses module boundaries, run [`../../mise-en-place/SKILL.md`](../../mise-en-place/SKILL.md) to lock in types and signatures first. If it's a contested One-Way Door, run [`../../cook-off/SKILL.md`](../../cook-off/SKILL.md) (or [`../../stage-tryout/SKILL.md`](../../stage-tryout/SKILL.md) when auditioning a new model or dependency).
5. **Station 3 — Line Cook & "Clean As You Go" (`kitchen-brigade` + `fifo-walk-in`)**:
   - Provision an isolated `git worktree` cutting board via `bash skills/head-chef-mode/scripts/spawn-worktree.sh <ticket-id>` (`principle-clean-cutting-boards`).
   - Spawn `line_cook_implementer` with the self-contained ticket brief (order verbatim + prep-note ID + plating criteria).
   - Label any temporary feature flag or shim with a green tape `FIFO-DATE-DOT` comment ([`../../fifo-walk-in/SKILL.md`](../../fifo-walk-in/SKILL.md)).
   - Inside the worktree, run [`../../cross-contamination/SKILL.md`](../../cross-contamination/SKILL.md), the project's tasting harness ([`../../taste-the-dish/SKILL.md`](../../taste-the-dish/SKILL.md)), and wipe the board with `bash skills/head-chef-mode/scripts/clean-station.sh --allergy`. Commit to `factory/<ticket-id>`.
6. **Station 4 — Blind Pass Inspector (`kitchen-brigade` + `health-inspector`)**:
   - Generate the reasoning-stripped blind tasting packet via `bash skills/head-chef-mode/scripts/cross-vendor-taste.sh`.
   - Spawn `pass_inspector` (`reviewer`) on a **different model vendor** than `line_cook_implementer` (`principle-blind-taste-test`).
   - Pass only the ticket, verbatim plating criteria, prep-note ID, pushed `factory/<ticket-id>` diff, and tasting output—**never** the Line Cook's internal monologue.
   - On `request_changes` (refire), route findings back to a fresh Line Cook and re-taste, capped at **at most 2 refires** (`MAX_REVISION_ROUNDS = 2`). If the plate still fails after 2 refires, 86 the ticket, bus the worktree (`spawn-worktree.sh --bus <ticket-id>`), and report unresolved findings without opening a PR.
7. **Plate Draft PR at the Pass, Bus the Cutting Board & Audit the Prep Log**:
   - When `pass_inspector` returns `approve`, open a **Draft Pull Request** (`draft: true`, per `principle-plate-at-the-pass`), written through [`../../plain-english-menu/SKILL.md`](../../plain-english-menu/SKILL.md).
   - Bus the finished cutting board back to the dishpit (`bash skills/head-chef-mode/scripts/spawn-worktree.sh --bus <ticket-id>`) and run `bash skills/head-chef-mode/scripts/closing-duty.sh`.
