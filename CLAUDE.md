# CLAUDE.md — Operating Guide for the Modular Software Factory Skill Stack (`fstack`)

This repository is a **`pstack`-style modular skill set** implementing a complete autonomous software and revenue factory. Instead of a monolithic codebase or single giant prompt, capabilities are decomposed into **22 composable skills** under [`skills/`](file:///home/antigravity/principled-product-factory/skills/) (symlinked to `.claude/skills/`, `.agents/skills/`, and `.cursor/skills/`).

---

## 1. How to Operate the Factory

1. **Start Every Non-Trivial Task with [`/factory-mode`](file:///home/antigravity/principled-product-factory/skills/factory-mode/SKILL.md)**:
   - `/factory-mode` classifies the Lifecycle Stage (`Stage A`, `Stage B`, or `Stage C`), picks the matching playbook from `skills/factory-mode/playbooks/*.md`, copies its steps into your todo list, and loads leaf workflow and `principle-*` skills on demand.
2. **Subagent Kickoff Rule**:
   - The first line of every subagent or station prompt MUST be:
     `Read <repo-root>/skills/factory-mode/worker.md before anything else.`
3. **Verify Every Skill Edit**:
   - Before committing any change to `skills/`, run the structural validator:
     ```bash
     bash skills/factory-mode/scripts/validate-skills.sh
     ```

---

## 2. Rule-to-Skill Enforcement Table (`/correct`)

| Factory Law | Governing Skill | Structural Enforcer / Playbook |
| :--- | :--- | :--- |
| **No Build Trap (Customer Value First)** | [`escape-the-build-trap`](file:///home/antigravity/principled-product-factory/skills/escape-the-build-trap/SKILL.md), [`principle-no-build-trap`](file:///home/antigravity/principled-product-factory/skills/principle-no-build-trap/SKILL.md) | [`playbooks/stage-a-discovery.md`](file:///home/antigravity/principled-product-factory/skills/factory-mode/playbooks/stage-a-discovery.md) (Ulwick Score $\ge 10.0$ + Mom Test Ladder + 30-day Zombie Sunset) |
| **Contribution Margin Floor & Zero AI Theater** | [`margin-guard`](file:///home/antigravity/principled-product-factory/skills/margin-guard/SKILL.md), [`principle-contribution-margin-floor`](file:///home/antigravity/principled-product-factory/skills/principle-contribution-margin-floor/SKILL.md) | 4-Axis AI-Native Scorecard, $\text{EVOI} > \text{Cost}$, 6-Month Re-Pricing Retro-Audit |
| **4-Station Pipeline & Draft-PR Ceiling** | [`foreman-pipeline`](file:///home/antigravity/principled-product-factory/skills/foreman-pipeline/SKILL.md), [`principle-orchestrator-routes-not-writes`](file:///home/antigravity/principled-product-factory/skills/principle-orchestrator-routes-not-writes/SKILL.md), [`principle-draft-pr-unattended-ceiling`](file:///home/antigravity/principled-product-factory/skills/principle-draft-pr-unattended-ceiling/SKILL.md) | [`playbooks/intake-to-draft-pr.md`](file:///home/antigravity/principled-product-factory/skills/factory-mode/playbooks/intake-to-draft-pr.md) (`classifier -> analyst -> implementer -> reviewer`, `factory/*` branch guard) |
| **Independent Cross-Vendor Blind Review** | [`principle-cross-vendor-blind-review`](file:///home/antigravity/principled-product-factory/skills/principle-cross-vendor-blind-review/SKILL.md), [`interrogate`](file:///home/antigravity/principled-product-factory/skills/interrogate/SKILL.md), [`arena`](file:///home/antigravity/principled-product-factory/skills/arena/SKILL.md) | Different model vendor for `reviewer` / cross-judge, reasoning stripped, max 2 revisions |
| **Challenger Sale & JOLT Deal Desk** | [`challenger-deal-desk`](file:///home/antigravity/principled-product-factory/skills/challenger-deal-desk/SKILL.md) | [`playbooks/enterprise-deal-desk.md`](file:///home/antigravity/principled-product-factory/skills/factory-mode/playbooks/enterprise-deal-desk.md) (6-step reframe, $\text{COI} \ge 3\times \text{ACV}$, Give-Get tension, JOLT de-risking) |
| **Continuous Customer Learning Flywheel** | [`customer-flywheel`](file:///home/antigravity/principled-product-factory/skills/customer-flywheel/SKILL.md) | [`playbooks/flywheel-and-harvest.md`](file:///home/antigravity/principled-product-factory/skills/factory-mode/playbooks/flywheel-and-harvest.md) (Correction-diff clustering, $N=1 \to 3 \to 10$ demand graduation, Bayesian JTBD update) |
| **SRE 3-Tier Fallbacks, Canary & OEE** | [`sre-fallback-and-postmortem`](file:///home/antigravity/principled-product-factory/skills/sre-fallback-and-postmortem/SKILL.md), [`factory-floor-ops`](file:///home/antigravity/principled-product-factory/skills/factory-floor-ops/SKILL.md) | [`playbooks/canary-and-oee.md`](file:///home/antigravity/principled-product-factory/skills/factory-mode/playbooks/canary-and-oee.md) (Holdout twin, `1%->10%->50%->100%` Shewhart/SRM gates, Goldratt OEE) |
| **Append-Only TSV Audit Trail** | [`show-me-your-work`](file:///home/antigravity/principled-product-factory/skills/show-me-your-work/SKILL.md) | [`scripts/log-decision.sh`](file:///home/antigravity/principled-product-factory/skills/factory-mode/scripts/log-decision.sh) (`ts | phase | decision | why | evidence | result`) |
| **Skill Registry & Resource Integrity** | [`correct`](file:///home/antigravity/principled-product-factory/skills/correct/SKILL.md), [`principle-encode-lessons-in-structure`](file:///home/antigravity/principled-product-factory/skills/principle-encode-lessons-in-structure/SKILL.md) | [`scripts/validate-skills.sh`](file:///home/antigravity/principled-product-factory/skills/factory-mode/scripts/validate-skills.sh) |
