# CLAUDE.md — Operating Guide for the Kitchen Brigade Software Factory Skill Stack

This repository is a **42-skill modular kitchen brigade stack** and **5-station native subagent suite** implementing an autonomous software and revenue factory. Capabilities are decomposed into composable skills under [`skills/`](file:///home/antigravity/principled-product-factory/skills/) (symlinked to `.claude/skills/`, `.agents/skills/`, and `.cursor/skills/`) and native station subagents under [`agents/`](file:///home/antigravity/principled-product-factory/agents/) (symlinked to `.claude/agents/`).

---

## 1. How to Run the Kitchen in Claude Code (The Factory Levers & Daily Chef Rituals)

1. **4:30 PM Pre-Shift Lineup & Walk-In Check ([`/pre-shift-lineup`](file:///home/antigravity/principled-product-factory/skills/pre-shift-lineup/SKILL.md))**:
   - Before firing tickets in a new session, check base stockpot status, active `factory/*` cutting boards (`WIP <= 5`), spoiled `FIFO-DATE-DOT` containers, and station cleanliness:
     ```bash
     bash skills/head-chef-mode/scripts/pre-shift-check.sh
     ```
2. **Start Every Non-Trivial Order with [`/head-chef-mode`](file:///home/antigravity/principled-product-factory/skills/head-chef-mode/SKILL.md)**:
   - `/head-chef-mode` classifies the Menu Stage (`Stage A: Test Kitchen 0-to-1`, `Stage B: Signature Menu & Growth`, or `Stage C: Multi-Kitchen Franchise Scale`), unbundles prescribed feature requests into problems to solve ([`/opportunity-brief`](file:///home/antigravity/principled-product-factory/skills/opportunity-brief/SKILL.md)), checks Marty Cagan's 4 Big Risks ([`/four-tasting-risks`](file:///home/antigravity/principled-product-factory/skills/four-tasting-risks/SKILL.md)), checks whether to serve a 5-minute [`/amuse-bouche`](file:///home/antigravity/principled-product-factory/skills/amuse-bouche/SKILL.md) first, picks the matching service playbook from `skills/head-chef-mode/playbooks/*.md`, and keeps the main context window clean (`principle-expediter-calls-not-cooks`).
3. **Line Station Kickoff Rule**:
   - The first line of every subagent or station prompt MUST be:
     `Read <repo-root>/skills/head-chef-mode/station-brief.md before anything else.`
4. **Spawn Isolated Cutting Boards with Little's Law WIP Guard (`WIP <= 5`)**:
   - Before [`line-cook-implementer`](file:///home/antigravity/principled-product-factory/agents/line-cook-implementer.md), [`/cook-off`](file:///home/antigravity/principled-product-factory/skills/cook-off/SKILL.md), or [`/stage-tryout`](file:///home/antigravity/principled-product-factory/skills/stage-tryout/SKILL.md) touches code, provision a clean `factory/<ticket-slug>` git worktree:
     ```bash
     bash skills/head-chef-mode/scripts/spawn-worktree.sh <ticket-slug>
     ```
5. **"Clean As You Go", Purple-Board Allergy Scan & FIFO Date Dots ([`/allergy-alert`](file:///home/antigravity/principled-product-factory/skills/allergy-alert/SKILL.md), [`/fifo-walk-in`](file:///home/antigravity/principled-product-factory/skills/fifo-walk-in/SKILL.md))**:
   - Before calling [`pass-inspector`](file:///home/antigravity/principled-product-factory/agents/pass-inspector.md), wipe the station down, scan for allergens/secrets, and check `FIFO-DATE-DOT` expiration labels:
     ```bash
     bash skills/head-chef-mode/scripts/clean-station.sh --allergy
     bash skills/head-chef-mode/scripts/audit-date-dots.sh
     ```
6. **Generate a Reasoning-Stripped Blind Tasting Packet**:
   - Strip the Line Cook's internal reasoning and package only verbatim criteria + raw unified diff (automatically runs `clean-station.sh` first):
     ```bash
     bash skills/head-chef-mode/scripts/cross-vendor-taste.sh HEAD~1 "Verbatim criterion 1; Verbatim criterion 2"
     ```
7. **Run the End-to-End Live Tasting Harness ([`/verify-kitchen-cookbook`](file:///home/antigravity/principled-product-factory/skills/verify-kitchen-cookbook/SKILL.md))**:
   - Executes `Fire Up -> Station Check -> Plate -> Proof -> Dishpit` across every feature in [`features/README.md`](file:///home/antigravity/principled-product-factory/features/README.md) and writes `.audit/evidence/proof-kitchen-cookbook.json`:
     ```bash
     bash skills/head-chef-mode/scripts/run-live-tasting.sh
     ```
8. **End-of-Shift Closing Duty (2-Minute Flywheel)**:
   - Run closing inspection at the end of every shift before `/update-the-cookbook` or `/sharpen-the-knives`:
     ```bash
     bash skills/head-chef-mode/scripts/closing-duty.sh
     ```

---

## 2. Health-Code Rule-to-Skill Enforcement Table (`/sharpen-the-knives`)

| Kitchen Law | Governing Skill | Structural Enforcer / Playbook |
| :--- | :--- | :--- |
| **No Empty Calories (Guest Hunger First)** | [`no-empty-calories`](file:///home/antigravity/principled-product-factory/skills/no-empty-calories/SKILL.md), [`principle-no-empty-calories`](file:///home/antigravity/principled-product-factory/skills/principle-no-empty-calories/SKILL.md) | [`playbooks/test-kitchen-tasting.md`](file:///home/antigravity/principled-product-factory/skills/head-chef-mode/playbooks/test-kitchen-tasting.md) (Ulwick Score $\ge 10.0$ + Mom Test Ladder + 30-day 86-the-Dish Sunset) |
| **Marty Cagan Product Trio & 4 Big Risks** | [`opportunity-brief`](file:///home/antigravity/principled-product-factory/skills/opportunity-brief/SKILL.md), [`four-tasting-risks`](file:///home/antigravity/principled-product-factory/skills/four-tasting-risks/SKILL.md), [`plating-and-experience`](file:///home/antigravity/principled-product-factory/skills/plating-and-experience/SKILL.md) | Problem-not-feature reframe, 3 competing options, Value/Usability/Feasibility/Viability check, High-Integrity Reservations, and `Plated != Eaten` mandatory outcome telemetry hook |
| **Food-Cost Margin Floor & Zero Foam Theater** | [`food-cost-guard`](file:///home/antigravity/principled-product-factory/skills/food-cost-guard/SKILL.md), [`principle-food-cost-floor`](file:///home/antigravity/principled-product-factory/skills/principle-food-cost-floor/SKILL.md) | 4-Axis Recipe Filter, $\text{EVOI} > \text{Cost}$, 6-Month Menu Re-Pricing Retro-Audit |
| **4-Station Brigade & Plate-at-the-Pass Ceiling** | [`kitchen-brigade`](file:///home/antigravity/principled-product-factory/skills/kitchen-brigade/SKILL.md), [`principle-expediter-calls-not-cooks`](file:///home/antigravity/principled-product-factory/skills/principle-expediter-calls-not-cooks/SKILL.md), [`principle-plate-at-the-pass`](file:///home/antigravity/principled-product-factory/skills/principle-plate-at-the-pass/SKILL.md) | [`playbooks/ticket-to-pass.md`](file:///home/antigravity/principled-product-factory/skills/head-chef-mode/playbooks/ticket-to-pass.md) (`host_triage -> sous_chef_planner -> line_cook_implementer -> pass_inspector`, `factory/*` branch guard) |
| **Blind Cross-Vendor Tasting at the Pass** | [`principle-blind-taste-test`](file:///home/antigravity/principled-product-factory/skills/principle-blind-taste-test/SKILL.md), [`health-inspector`](file:///home/antigravity/principled-product-factory/skills/health-inspector/SKILL.md), [`cook-off`](file:///home/antigravity/principled-product-factory/skills/cook-off/SKILL.md) | Different model vendor for Pass Inspector / Cook-Off taster, monologue stripped, max 2 refires |
| **Mise en Place & Cross-Contamination Check** | [`mise-en-place`](file:///home/antigravity/principled-product-factory/skills/mise-en-place/SKILL.md), [`cross-contamination`](file:///home/antigravity/principled-product-factory/skills/cross-contamination/SKILL.md), [`haccp-statechart`](file:///home/antigravity/principled-product-factory/skills/haccp-statechart/SKILL.md) | Types & Liskov contracts before cooking; Rung 4/5 code proof of downstream safety; Mermaid statecharts |
| **Sommelier Table Pitch & JOLT Deal Desk** | [`sommelier-table-pitch`](file:///home/antigravity/principled-product-factory/skills/sommelier-table-pitch/SKILL.md), [`signature-dish-moat`](file:///home/antigravity/principled-product-factory/skills/signature-dish-moat/SKILL.md) | [`playbooks/sommelier-table-pitch.md`](file:///home/antigravity/principled-product-factory/skills/head-chef-mode/playbooks/sommelier-table-pitch.md) (6-step reframe, $\text{COI} \ge 3\times \text{ACV}$, Give-Get tension, JOLT de-risking, Helmer 7 Powers) |
| **Dining-Room Feedback & Recipe Flywheel** | [`dining-room-feedback`](file:///home/antigravity/principled-product-factory/skills/dining-room-feedback/SKILL.md), [`update-the-cookbook`](file:///home/antigravity/principled-product-factory/skills/update-the-cookbook/SKILL.md) | [`playbooks/dining-room-harvest.md`](file:///home/antigravity/principled-product-factory/skills/head-chef-mode/playbooks/dining-room-harvest.md) (Plate-back diff clustering, $N=1 \to 3 \to 10$ graduation, Bayesian hunger update) |
| **3-Tier Pantry Backup, First Tables & OEE** | [`pantry-backup-and-incident-card`](file:///home/antigravity/principled-product-factory/skills/pantry-backup-and-incident-card/SKILL.md), [`central-commissary`](file:///home/antigravity/principled-product-factory/skills/central-commissary/SKILL.md), [`thermometer-check`](file:///home/antigravity/principled-product-factory/skills/thermometer-check/SKILL.md) | [`playbooks/first-tables-and-service-speed.md`](file:///home/antigravity/principled-product-factory/skills/head-chef-mode/playbooks/first-tables-and-service-speed.md) (Mystery-diner holdout, `1%->100%` Shewhart/SRM gates, Goldratt OEE) |
| **Append-Only TSV Prep Log & Shift Handoff** | [`prep-log`](file:///home/antigravity/principled-product-factory/skills/prep-log/SKILL.md), [`shift-handoff`](file:///home/antigravity/principled-product-factory/skills/shift-handoff/SKILL.md), [`plain-english-menu`](file:///home/antigravity/principled-product-factory/skills/plain-english-menu/SKILL.md) | [`scripts/log-decision.sh`](file:///home/antigravity/principled-product-factory/skills/head-chef-mode/scripts/log-decision.sh) (`ts | phase | decision | why | evidence | result`) |
| **Cookbook Registry & Resource Integrity** | [`sharpen-the-knives`](file:///home/antigravity/principled-product-factory/skills/sharpen-the-knives/SKILL.md), [`principle-kitchen-muscle-memory`](file:///home/antigravity/principled-product-factory/skills/principle-kitchen-muscle-memory/SKILL.md) | [`scripts/validate-skills.sh`](file:///home/antigravity/principled-product-factory/skills/head-chef-mode/scripts/validate-skills.sh) |
