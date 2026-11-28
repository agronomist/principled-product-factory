# CLAUDE.md — Operating Guide for the Kitchen Brigade Software Factory Skill Stack

This repository is a **42-skill modular kitchen brigade stack** and **5-station native subagent suite** implementing an autonomous software and revenue factory. Capabilities are decomposed into composable skills under [`skills/`](skills/) (symlinked to `.claude/skills/`, `.agents/skills/`, and `.cursor/skills/`), native station subagents under [`agents/`](agents/) (symlinked to `.claude/agents/`), and Claude Code plugin hooks under [`hooks/hooks.json`](hooks/hooks.json).

---

## 0. The 5 Entry-Point Commands (Zero Jargon Tax)

You do **not** need to memorize 42 skills. Users interact with **5 entry-point commands**, and `/head-chef-mode` automatically loads the right playbook and leaf skills behind the scenes:

| Command | Plain-English Action |
| :--- | :--- |
| **[`/head-chef-mode`](skills/head-chef-mode/SKILL.md)** | **Main Entry Point (Router)**: Classifies your task, picks one of the 7 service playbooks, and dispatches the 4-station subagent pipeline. |
| **[`/setup-kitchen`](skills/setup-kitchen/SKILL.md)** | **1-Minute Onboarding**: Configures station model tiers and sets up a live verification harness for your project. |
| **[`/kitchen-help`](skills/kitchen-help/SKILL.md)** | **Help & Copy-Paste Prompts**: Recommends the exact command or prompt for what you're trying to build or fix. |
| **[`/cook-off`](skills/cook-off/SKILL.md)** | **Parallel N-Candidate Bakeoff**: Spawns $N$ contenders on isolated `git worktree` branches, blind-reviews them, and grafts the best parts. |
| **[`/shift-handoff`](skills/shift-handoff/SKILL.md)** | **Session Catch-Up**: Summarizes `decisions.tsv`, what passed verification, what was reverted, and every Draft PR waiting for human review. |

---

## 1. How to Run the Kitchen in Claude Code (Portable Script Paths)

> **Path Note for External Projects**: Inside this repository, `.claude/skills` symlinks to `skills/`. When installed into another project (`./install.sh /path/to/project`), invoke scripts via `.claude/skills/head-chef-mode/scripts/<script>.sh` (or `~/.claude/skills/head-chef-mode/scripts/<script>.sh` for global installs). Every script automatically detects your current working Git repository (`git rev-parse --show-toplevel`).

1. **4:30 PM Pre-Shift Lineup & Walk-In Check ([`/pre-shift-lineup`](skills/pre-shift-lineup/SKILL.md))**:
   - Before firing tickets in a new session, check base stockpot status, active `factory/*` cutting boards (`WIP <= 5`), spoiled `FIFO-DATE-DOT` containers, and station cleanliness:
     ```bash
     bash .claude/skills/head-chef-mode/scripts/pre-shift-check.sh
     ```
2. **Start Every Non-Trivial Order with [`/head-chef-mode`](skills/head-chef-mode/SKILL.md)**:
   - `/head-chef-mode` classifies the Menu Stage (`Stage A: Test Kitchen 0-to-1`, `Stage B: Signature Menu & Growth`, or `Stage C: Multi-Kitchen Franchise Scale`), unbundles prescribed feature requests into problems to solve ([`/opportunity-brief`](skills/opportunity-brief/SKILL.md)), checks Marty Cagan's 4 Big Risks ([`/four-tasting-risks`](skills/four-tasting-risks/SKILL.md)), checks whether to serve a 5-minute [`/amuse-bouche`](skills/amuse-bouche/SKILL.md) first, picks the matching service playbook from `skills/head-chef-mode/playbooks/*.md`, and keeps the main context window clean (`principle-expediter-calls-not-cooks`).
3. **Line Station Kickoff Rule**:
   - The first line of every subagent or station prompt MUST be:
     `Read .claude/skills/head-chef-mode/station-brief.md before anything else.`
4. **Spawn & Bus Isolated Cutting Boards with Little's Law WIP Guard (`WIP <= 5`)**:
   - Before [`line-cook-implementer`](agents/line-cook-implementer.md), [`/cook-off`](skills/cook-off/SKILL.md), or [`/stage-tryout`](skills/stage-tryout/SKILL.md) touches code, provision a clean `factory/<ticket-slug>` git worktree (and bus it back to the dishpit when done):
     ```bash
     bash .claude/skills/head-chef-mode/scripts/spawn-worktree.sh <ticket-slug>
     bash .claude/skills/head-chef-mode/scripts/spawn-worktree.sh --list
     bash .claude/skills/head-chef-mode/scripts/spawn-worktree.sh --bus <ticket-slug>
     ```
5. **"Clean As You Go", Purple-Board Allergy Scan & FIFO Date Dots ([`/allergy-alert`](skills/allergy-alert/SKILL.md), [`/fifo-walk-in`](skills/fifo-walk-in/SKILL.md))**:
   - Before calling [`pass-inspector`](agents/pass-inspector.md), wipe the station down, scan for allergens/secrets, and check `FIFO-DATE-DOT` expiration labels:
     ```bash
     bash .claude/skills/head-chef-mode/scripts/clean-station.sh --allergy
     bash .claude/skills/head-chef-mode/scripts/audit-date-dots.sh
     ```
6. **Generate a Reasoning-Stripped Blind Tasting Packet (with Working-Tree SHA-256 Lock)**:
   - Strip the Line Cook's internal reasoning, record the pre-inspection working-tree SHA-256 fingerprint, and package only verbatim criteria + raw unified diff:
     ```bash
     bash .claude/skills/head-chef-mode/scripts/cross-vendor-taste.sh HEAD~1 "Verbatim criterion 1; Verbatim criterion 2"
     ```
7. **Run the End-to-End Live Tasting Harness ([`/verify-kitchen-cookbook`](skills/verify-kitchen-cookbook/SKILL.md))**:
   - Executes `Fire Up -> Station Check -> Plate -> Proof -> Dishpit` across every feature in [`features/README.md`](features/README.md) (including clean-project external install verification and bouncer bypass checks) and writes `.audit/evidence/proof-kitchen-cookbook.json`:
     ```bash
     bash .claude/skills/head-chef-mode/scripts/run-live-tasting.sh
     ```
8. **End-of-Shift Closing Duty (2-Minute Flywheel)**:
   - Run closing inspection at the end of every shift before `/update-the-cookbook` or `/sharpen-the-knives`:
     ```bash
     bash .claude/skills/head-chef-mode/scripts/closing-duty.sh
     ```

---

## 2. Health-Code Rule-to-Skill Enforcement Table (`/sharpen-the-knives`)

| Kitchen Law | Governing Skill | Structural Enforcer / Playbook |
| :--- | :--- | :--- |
| **No Empty Calories (Guest Hunger First)** | [`no-empty-calories`](skills/no-empty-calories/SKILL.md), [`principle-no-empty-calories`](skills/principle-no-empty-calories/SKILL.md) | [`playbooks/test-kitchen-tasting.md`](skills/head-chef-mode/playbooks/test-kitchen-tasting.md) (Ulwick Score $\ge 10.0$ + Mom Test Ladder + 30-day 86-the-Dish Sunset) |
| **Marty Cagan Product Trio & 4 Big Risks** | [`opportunity-brief`](skills/opportunity-brief/SKILL.md), [`four-tasting-risks`](skills/four-tasting-risks/SKILL.md), [`plating-and-experience`](skills/plating-and-experience/SKILL.md) | Problem-not-feature reframe, 3 competing options, Value/Usability/Feasibility/Viability check, High-Integrity Reservations, and `Plated != Eaten` mandatory outcome telemetry hook |
| **Food-Cost Margin Floor & Zero Foam Theater** | [`food-cost-guard`](skills/food-cost-guard/SKILL.md), [`principle-food-cost-floor`](skills/principle-food-cost-floor/SKILL.md) | 4-Axis Recipe Filter, $\text{EVOI} > \text{Cost}$, 6-Month Menu Re-Pricing Retro-Audit |
| **4-Station Brigade & Plate-at-the-Pass Ceiling** | [`kitchen-brigade`](skills/kitchen-brigade/SKILL.md), [`principle-expediter-calls-not-cooks`](skills/principle-expediter-calls-not-cooks/SKILL.md), [`principle-plate-at-the-pass`](skills/principle-plate-at-the-pass/SKILL.md) | [`playbooks/ticket-to-pass.md`](skills/head-chef-mode/playbooks/ticket-to-pass.md) + [`hooks/hooks.json`](hooks/hooks.json) + [`hooks/pre-tool-guard.sh`](hooks/pre-tool-guard.sh) (plus GitHub branch protection as the server-side lock) |
| **Blind Cross-Vendor Tasting & Read-Only Tree Lock** | [`principle-blind-taste-test`](skills/principle-blind-taste-test/SKILL.md), [`health-inspector`](skills/health-inspector/SKILL.md), [`cook-off`](skills/cook-off/SKILL.md) | [`scripts/cross-vendor-taste.sh`](skills/head-chef-mode/scripts/cross-vendor-taste.sh) (strips monologue, records pre-inspection tree SHA-256 fingerprint, supports external cross-vendor CLIs) |
| **Mise en Place & Cross-Contamination Check** | [`mise-en-place`](skills/mise-en-place/SKILL.md), [`cross-contamination`](skills/cross-contamination/SKILL.md), [`haccp-statechart`](skills/haccp-statechart/SKILL.md) | Types & Liskov contracts before cooking; Rung 4/5 code proof of downstream safety; Mermaid statecharts |
| **Sommelier Table Pitch & JOLT Deal Desk** | [`sommelier-table-pitch`](skills/sommelier-table-pitch/SKILL.md), [`signature-dish-moat`](skills/signature-dish-moat/SKILL.md) | [`playbooks/sommelier-table-pitch.md`](skills/head-chef-mode/playbooks/sommelier-table-pitch.md) (6-step reframe, $\text{COI} \ge 3\times \text{ACV}$, Give-Get tension, JOLT de-risking, Helmer 7 Powers) |
| **Dining-Room Feedback & Recipe Flywheel** | [`dining-room-feedback`](skills/dining-room-feedback/SKILL.md), [`update-the-cookbook`](skills/update-the-cookbook/SKILL.md) | [`playbooks/dining-room-harvest.md`](skills/head-chef-mode/playbooks/dining-room-harvest.md) (Plate-back diff clustering, $N=1 \to 3 \to 10$ graduation, Bayesian hunger update) |
| **3-Tier Pantry Backup, First Tables & OEE** | [`pantry-backup-and-incident-card`](skills/pantry-backup-and-incident-card/SKILL.md), [`central-commissary`](skills/central-commissary/SKILL.md), [`thermometer-check`](skills/thermometer-check/SKILL.md) | [`playbooks/first-tables-and-service-speed.md`](skills/head-chef-mode/playbooks/first-tables-and-service-speed.md) (Mystery-diner holdout, `1%->100%` Shewhart/SRM gates, Goldratt OEE) |
| **Append-Only TSV Prep Log & Shift Handoff** | [`prep-log`](skills/prep-log/SKILL.md), [`shift-handoff`](skills/shift-handoff/SKILL.md), [`plain-english-menu`](skills/plain-english-menu/SKILL.md) | [`scripts/log-decision.sh`](skills/head-chef-mode/scripts/log-decision.sh) (`ts | phase | decision | why | evidence | result`) |
| **Cookbook Registry, Manifest & Resource Integrity** | [`sharpen-the-knives`](skills/sharpen-the-knives/SKILL.md), [`principle-kitchen-muscle-memory`](skills/principle-kitchen-muscle-memory/SKILL.md) | [`scripts/validate-skills.sh`](skills/head-chef-mode/scripts/validate-skills.sh) |
