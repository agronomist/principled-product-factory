# Playbook: Intake to Reviewed Draft Pull Request (`intake-to-draft-pr.md`)

Use this playbook when an issue arrives from GitHub (`factory` label or `@mention`), a Linear Agent Session, or the user asks to turn a work item into a pull request.

## Todo List Steps (Copy into Todo Tool First)

1. **Ground in Memory & Stamp Trust (`foreman-pipeline`)**:
   - Read the Factory Brain (`factory-brain/<sha256(repo)>.md`) for repository build quirks, verification gotchas, and recurring review findings.
   - Stamp the caller's principal class (`unattended_autonomous`, `trusted_interactive`, or `dev_tui`).
   - Log a `frame` row to `decisions.tsv` via [`../../show-me-your-work/SKILL.md`](../../show-me-your-work/SKILL.md).
2. **Station 1 — Classifier (`foreman-pipeline`)**:
   - Spawn `classifier` starting with `Read <path>/worker.md before anything else.`
   - Classify `work_type` (`bug | feature | refactor | perf | chore`), `priority`, `complexity`, `affected_area`, and `needs_clarification`.
   - **Stop Rule**: If `needs_clarification == true`, post the questions on the intake thread and **halt immediately**. Never leave an unattended session parked waiting on input.
3. **Anti-Build-Trap & Unit Margin Gates (`escape-the-build-trap` + `margin-guard`)**:
   - If `work_type == "feature"`, run [`../../escape-the-build-trap/SKILL.md`](../../escape-the-build-trap/SKILL.md). Verify Ulwick JTBD Opportunity Score $\ge 10.0$ and real customer skin-in-the-game (*The Mom Test*). Block if speculative (*"someone at some point will like it"*).
   - Run [`../../margin-guard/SKILL.md`](../../margin-guard/SKILL.md) to confirm unit contribution margin $\ge M_{\min}$ and $\text{EVOI} > \text{Cost}$.
4. **Station 2 — Analyst (+ Optional Researcher) (`foreman-pipeline`)**:
   - If external facts (upstream bugs, library versions) are needed, spawn `researcher` first and save its memo as a pass-by-ID handoff artifact (`^[a-z0-9]+(?:-[a-z0-9]+)*$`).
   - Spawn `analyst` against a live checkout to produce ordered steps, risks, **verbatim acceptance criteria**, and an analysis handoff artifact ID.
   - If the design is a high-risk One-Way Door, run [`../../arena/SKILL.md`](../../arena/SKILL.md) first to settle the shape across isolated candidates.
5. **Station 3 — Implementer (`foreman-pipeline`)**:
   - Provision an isolated `git worktree` on branch `factory/<item-id>` (`principle-separate-before-serializing-shared-state`).
   - Spawn `implementer` with the self-contained brief (work item verbatim + analysis artifact ID + acceptance criteria).
   - Inside the worktree, run the project's `verify-*` harness (`Doctor -> Drive -> Evidence -> Cleanup`) and tests. Commit to `factory/<item-id>`.
6. **Station 4 — Independent Cross-Vendor Reviewer (`foreman-pipeline` + `interrogate`)**:
   - Spawn `reviewer` on a **different model vendor** than `implementer` (`principle-cross-vendor-blind-review`).
   - Pass only the work item, verbatim acceptance criteria, analysis artifact ID, pushed `factory/<item-id>` branch diff, and verification output—**never** the implementer's private reasoning.
   - On `request_changes`, route findings back to a fresh `implementer` and re-review, capped at **at most 2 revision rounds** (`MAX_REVISION_ROUNDS = 2`). If still unapproved after 2 rounds, halt the line and report unresolved findings without opening a PR.
7. **Deliver Draft PR & Update Audit Trail**:
   - When `reviewer` returns `approve`, open a **Draft Pull Request** (`draft: true`, per `principle-draft-pr-unattended-ceiling`). Merging and marking ready stay human decisions.
   - Audit `decisions.tsv` against the transcript with a cross-vendor reviewer (`show-me-your-work`) and include the `Attention` section in the final report.
