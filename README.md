# `principled-product-factory` — Modular Software Factory Skill Stack (`fstack`)

A **`pstack`-style modular skill set** for AI coding agents (Claude Code, Cursor, Antigravity) that turns your repository into an autonomous, customer-obsessed software and revenue factory.

Combines:
- **Customer Discovery & Anti-Build-Trap Gates** (Melissa Perri, Tony Ulwick JTBD Opportunity Score $\ge 10.0$, Rob Fitzpatrick *The Mom Test*, Teresa Torres Continuous Discovery).
- **Unit Economics & AI-Native Prioritization** (Contribution Margin Floor, Expected Value of Information $\text{EVOI} > \text{Cost}$, Madhavan Ramanujam *Monetizing Innovation* + 6-Month Re-Pricing Retro-Audits).
- **Vercel `eve` / Foreman 4-Station Pipeline** (`classifier -> analyst -> implementer -> reviewer` + `researcher`, isolated `git worktree` sandboxes, pass-by-ID handoff artifacts, anti-poisoning Factory Brain, and Draft-PR unattended ceiling).
- **`pstack` Scientific Loops & Verification Harnesses** (`/arena` multi-candidate bakeoffs with cross-vendor judging & grafting, `/interrogate` execution-proved adversarial review, `/create-verification-skill` live app harnesses, `/show-me-your-work` TSV decision trails, `/correct` 5-level structural ratchets, and `principle-attack-the-premise`).
- **Challenger Sale & JOLT GTM Deal Desk** (6-Step Commercial Teaching choreography, $\text{COI} \ge 3\times \text{ACV}$, Buying Committee tailoring, Constructive Tension against Build-Trap demands and untraded discounts, and JOLT FOMU de-risking).
- **Industrial Factory Floor Operations** (Product-Line Stamping Press, Rule-of-Two AST Harvester, Sealed Holdout Digital Twin, `1% -> 10% -> 50% -> 100%` Canary Rollout with Shewhart $\pm 3\sigma$ and SRM $\chi^2$ gates, and Goldratt Theory of Constraints OEE).

---

## Skill Map (`skills/`)

Start any task with **`/factory-mode`**, which matches your request to a playbook and loads the required skills on demand—or invoke any skill directly:

### 1. Master Mode & Playbooks
| Skill | Purpose |
| :--- | :--- |
| **[`/factory-mode`](skills/factory-mode/SKILL.md)** | Master router, subagent kickoff contract ([`worker.md`](skills/factory-mode/worker.md)), and 7 playbooks ([`intake-to-draft-pr`](skills/factory-mode/playbooks/intake-to-draft-pr.md), [`stage-a-discovery`](skills/factory-mode/playbooks/stage-a-discovery.md), [`scientific-hillclimb`](skills/factory-mode/playbooks/scientific-hillclimb.md), [`enterprise-deal-desk`](skills/factory-mode/playbooks/enterprise-deal-desk.md), [`canary-and-oee`](skills/factory-mode/playbooks/canary-and-oee.md), [`flywheel-and-harvest`](skills/factory-mode/playbooks/flywheel-and-harvest.md), [`figure-it-out`](skills/factory-mode/playbooks/figure-it-out.md)). |

### 2. Core Factory & GTM Workflow Skills
| Skill | Purpose |
| :--- | :--- |
| **[`/escape-the-build-trap`](skills/escape-the-build-trap/SKILL.md)** | Blocks speculative features (*"someone at some point will like it"*); enforces Ulwick JTBD Opportunity Score $\ge 10.0$, *The Mom Test* commitment ladder, and 30-day post-ship zombie-feature code deletion. |
| **[`/margin-guard`](skills/margin-guard/SKILL.md)** | Enforces `unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`, 4-axis AI-native scorecard, Cohort P&L ($\text{CAC Payback} \le 12\text{m}$), and 6-month re-pricing retro-audits. |
| **[`/foreman-pipeline`](skills/foreman-pipeline/SKILL.md)** | Routes work items through stateless task-mode stations (`classifier -> analyst -> implementer -> reviewer`), passes memos by validated ID, protects the Factory Brain against prompt injection, and stops at a Draft PR on `factory/*`. |
| **[`/challenger-deal-desk`](skills/challenger-deal-desk/SKILL.md)** | Enforces the 6-step Challenger Commercial Teaching choreography ($\text{COI} \ge 3\times \text{ACV}$), tailors briefs across the buying committee, holds Constructive Tension on scope/discounts, and runs the JOLT FOMU playbook. |
| **[`/customer-flywheel`](skills/customer-flywheel/SKILL.md)** | Clusters passive `user_correction_diff` tuples into autonomous Foreman work items, graduates $N=1 \to N=3 \to N=10$ customer pain signals, and updates JTBD beliefs via Bayes' rule from live user workarounds. |
| **[`/factory-floor-ops`](skills/factory-floor-ops/SKILL.md)** | Stamps out new `products/<slug>/` lines, harvests Rule-of-Two AST duplicates into `platform/`, simulates supplier price shocks, replays sealed holdout digital twins, drives `1%->100%` canaries, and computes OEE bottlenecks. |
| **[`/sre-fallback-and-postmortem`](skills/sre-fallback-and-postmortem/SKILL.md)** | Enforces 3-tier graceful degradation (`primary -> secondary -> tertiary`), halts retries immediately on duplicate SHA-256 error signatures with reverse Saga rollbacks, and compiles $\pm 3\sigma$ breaches into minimized JSON regression fixtures. |

### 3. Verification, Bakeoff & Audit Loop Skills
| Skill | Purpose |
| :--- | :--- |
| **[`/arena`](skills/arena/SKILL.md)** | Spawns $N$ isolated worktree candidates on the same brief, scores with a cross-vendor judge against a hidden rubric, picks the cleanest base (Laziness Protocol), and grafts winning ideas from the losers. |
| **[`/interrogate`](skills/interrogate/SKILL.md)** | Multi-model adversarial review where findings survive **only** if proven by a real failing execution run. |
| **[`/create-verification-skill`](skills/create-verification-skill/SKILL.md)** | Generates and maintains a project-local `verify-<app>` harness (`Launch -> Doctor -> Drive -> Evidence -> Cleanup`) and living user-POV feature map (`features/`). |
| **[`/show-me-your-work`](skills/show-me-your-work/SKILL.md)** | Appends sanitized single-line TSV rows to `decisions.tsv` ([`scripts/log-decision.sh`](skills/factory-mode/scripts/log-decision.sh)) and audits evidence pointers with a cross-vendor reviewer. |
| **[`/correct`](skills/correct/SKILL.md)** | Eliminates recurring agent mistakes up the 5-level structural hierarchy: **1. Architecture $\to$ 2. Types $\to$ 3. Fix-Naming Lint $\to$ 4. Test $\to$ 5. Docs last**. |

### 4. One-Rule Composable Principles (`principle-*`)
- [`principle-no-build-trap`](skills/principle-no-build-trap/SKILL.md)
- [`principle-contribution-margin-floor`](skills/principle-contribution-margin-floor/SKILL.md)
- [`principle-orchestrator-routes-not-writes`](skills/principle-orchestrator-routes-not-writes/SKILL.md)
- [`principle-cross-vendor-blind-review`](skills/principle-cross-vendor-blind-review/SKILL.md)
- [`principle-draft-pr-unattended-ceiling`](skills/principle-draft-pr-unattended-ceiling/SKILL.md)
- [`principle-separate-before-serializing-shared-state`](skills/principle-separate-before-serializing-shared-state/SKILL.md)
- [`principle-attack-the-premise`](skills/principle-attack-the-premise/SKILL.md)
- [`principle-prove-it-works`](skills/principle-prove-it-works/SKILL.md)
- [`principle-sequence-verifiable-units`](skills/principle-sequence-verifiable-units/SKILL.md)
- [`principle-encode-lessons-in-structure`](skills/principle-encode-lessons-in-structure/SKILL.md)

---

## Quickstart & Validation

The repository symlinks `skills/` to `.claude/skills`, `.agents/skills`, and `.cursor/skills` out of the box so it works immediately in Claude Code, Cursor, and Antigravity.

```bash
# Validate all 22 modular skills (YAML frontmatter, directory match, playbooks, and scripts)
bash skills/factory-mode/scripts/validate-skills.sh

# Log a decision row to decisions.tsv
bash skills/factory-mode/scripts/log-decision.sh \
  decisions.tsv "frame" "Initialized modular skill stack" "Replace monolithic code with composable skills" "skills/factory-mode/SKILL.md:1" "VERIFIED"
```
