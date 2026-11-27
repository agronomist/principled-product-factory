# `principled-product-factory` — The Kitchen Brigade Software Factory Skill Stack

A **31-skill modular cookbook** for AI coding agents (Claude Code, Cursor, Antigravity) that runs your repository like a Michelin-starred **Brigade de Cuisine**: every dish must prove real diner hunger and positive food-cost margin before a single burner is lit, every order moves through isolated line stations (`host_triage -> sous_chef_planner -> line_cook_implementer -> pass_inspector`), and every plate is blind-tasted on the real artifact before sitting under the pass heat lamp as a Draft Pull Request.

---

## Complete 31-Skill Kitchen Map (`skills/`)

Start any shift with **`/head-chef-mode`**, which matches your ticket to one of 7 service playbooks and loads the required station skills on demand—or invoke any skill directly:

### 1. Head Chef Mode & Service Playbooks
| Skill | Purpose |
| :--- | :--- |
| **[`/head-chef-mode`](skills/head-chef-mode/SKILL.md)** | Master kitchen router, line-station kickoff brief ([`station-brief.md`](skills/head-chef-mode/station-brief.md)), and 7 service playbooks: [`ticket-to-pass`](skills/head-chef-mode/playbooks/ticket-to-pass.md), [`test-kitchen-tasting`](skills/head-chef-mode/playbooks/test-kitchen-tasting.md), [`recipe-reduction-loop`](skills/head-chef-mode/playbooks/recipe-reduction-loop.md), [`sommelier-table-pitch`](skills/head-chef-mode/playbooks/sommelier-table-pitch.md), [`first-tables-and-service-speed`](skills/head-chef-mode/playbooks/first-tables-and-service-speed.md), [`dining-room-harvest`](skills/head-chef-mode/playbooks/dining-room-harvest.md), and [`off-menu-special`](skills/head-chef-mode/playbooks/off-menu-special.md). |

### 2. Menu Triage, Food Cost, Brigade Line & Sommelier Skills
| Skill | Purpose |
| :--- | :--- |
| **[`/no-empty-calories`](skills/no-empty-calories/SKILL.md)** | Blocks speculative dishes (*"diners at some point might order it"*); enforces Ulwick JTBD Opportunity Score $\ge 10.0$, *The Mom Test* commitment ladder, and 30-day "86-the-dish" zombie code deletion. |
| **[`/food-cost-guard`](skills/food-cost-guard/SKILL.md)** | Enforces `unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`, 4-axis recipe filter against molecular-gastronomy AI theater, Cohort P&L ($\text{CAC Payback} \le 12\text{m}$), and 6-month menu re-pricing retro-audits. |
| **[`/kitchen-brigade`](skills/kitchen-brigade/SKILL.md)** | Escoffier 4-station routing (`host_triage -> sous_chef_planner -> line_cook_implementer -> pass_inspector` + `forager_researcher`), pass-by-ID prep notes, anti-poisoning Master Recipe Book, and Draft-PR heat-lamp ceiling on `factory/*`. |
| **[`/sommelier-table-pitch`](skills/sommelier-table-pitch/SKILL.md)** | Challenger Sale 6-step commercial teaching choreography ($\text{COI} \ge 3\times \text{ACV}$), pairing value to every seat at the table, Constructive Tension against off-menu demands/discounts, and JOLT menu-paralysis de-risking. |
| **[`/signature-dish-moat`](skills/signature-dish-moat/SKILL.md)** | April Dunford's 5-step menu positioning canvas, Hamilton Helmer's 7 Powers moat verification, and Porter Five Forces defense against ingredient purveyor pricing power. |
| **[`/dining-room-feedback`](skills/dining-room-feedback/SKILL.md)** | Clusters plates sent back to the pass (`user_correction_diff`) into autonomous Brigade tickets, graduates $N=1 \to N=3 \to N=10$ table requests, and updates Bayesian hunger beliefs from diner workarounds. |
| **[`/central-commissary`](skills/central-commissary/SKILL.md)** | Stamps out new `products/<slug>/` kitchen lines, harvests Rule-of-Two mother sauces into `platform/`, simulates $3\times$ purveyor price shocks, replays sealed mystery-diner holdout twins, serves `1%->100%` first tables, and computes Goldratt OEE bottlenecks. |
| **[`/pantry-backup-and-incident-card`](skills/pantry-backup-and-incident-card/SKILL.md)** | Enforces 3-tier pantry fallback substitutions (`primary -> secondary -> tertiary`), halts retries immediately on duplicate SHA-256 burn signatures with reverse Saga pan-dumping, and laminates $\pm 3\sigma$ breaches into minimized JSON incident cards. |

### 3. Mise en Place, Cook-Off, Tasting & Shift Handoff Skills
| Skill | Purpose |
| :--- | :--- |
| **[`/mise-en-place`](skills/mise-en-place/SKILL.md)** | Sketches immutable container types, function signatures, and Liskov pre/postconditions before any cooking starts. |
| **[`/cook-off`](skills/cook-off/SKILL.md)** | Spawns $N$ line cooks on isolated `git worktree` cutting boards, scores with a cross-vendor blind taster against a hidden rubric, picks the simplest base dish, and grafts the best elements from runners-up. |
| **[`/health-inspector`](skills/health-inspector/SKILL.md)** | Multi-model adversarial health inspection where violations survive **only** if proven by a real failing execution run. |
| **[`/cross-contamination`](skills/cross-contamination/SKILL.md)** | Finds what a change could spoil three stations downstream beyond `grep`, and proves the one safety fact it relies on by running real code. |
| **[`/taste-the-dish`](skills/taste-the-dish/SKILL.md)** | Generates and maintains a project-local live tasting harness (`Fire Up -> Station Check -> Plate -> Proof -> Dishpit`) and living diner-POV menu map (`features/`). |
| **[`/thermometer-check`](skills/thermometer-check/SKILL.md)** | Vets any performance, latency, cost, or eval number across 7 checks (did cooking happen, physical limiter, zero spoilage, repeatability, tuning parity, CUPED/SRM, dining-room relevance). |
| **[`/haccp-statechart`](skills/haccp-statechart/SKILL.md)** | Formally verifies critical concurrency (`WIP_LIMIT = 5`), retry, Saga, and circuit-breaker state machines, proves sensitivity on spoiled mutations, tracks `last_synced_commit`, and draws Mermaid statecharts. |
| **[`/prep-log`](skills/prep-log/SKILL.md)** | Appends sanitized single-line TSV rows to `decisions.tsv` ([`scripts/log-decision.sh`](skills/head-chef-mode/scripts/log-decision.sh)) and audits evidence pointers with a cross-vendor taster. |
| **[`/sharpen-the-knives`](skills/sharpen-the-knives/SKILL.md)** | Eliminates recurring line-cook accidents up the 5-level hierarchy: **1. Kitchen Layout (Architecture) $\to$ 2. Labeled Containers (Types) $\to$ 3. Fix-Naming Alarm (Lint) $\to$ 4. Taste Test $\to$ 5. Wall Sign (Docs) last**. |
| **[`/shift-handoff`](skills/shift-handoff/SKILL.md)** | Catches the Head Chef up after an overnight shift in plain words and small visuals, listing every Draft PR waiting under the heat lamp with everything needed to decide from the reply alone. |
| **[`/update-the-cookbook`](skills/update-the-cookbook/SKILL.md)** | Mines the shift transcript for durable 6-month lessons and proposes surgical updates to `skills/*/SKILL.md`. |
| **[`/plain-english-menu`](skills/plain-english-menu/SKILL.md)** | Strips corporate foam and AI tells out of prose, labels evidence (`measured`, `inferred`, `guess`), and supplies the canonical **Soccer & Seinfeld Metaphor Bank**. |

### 4. Ten One-Rule Kitchen Principles (`principle-*`)
- [`principle-no-empty-calories`](skills/principle-no-empty-calories/SKILL.md)
- [`principle-food-cost-floor`](skills/principle-food-cost-floor/SKILL.md)
- [`principle-expediter-calls-not-cooks`](skills/principle-expediter-calls-not-cooks/SKILL.md)
- [`principle-blind-taste-test`](skills/principle-blind-taste-test/SKILL.md)
- [`principle-plate-at-the-pass`](skills/principle-plate-at-the-pass/SKILL.md)
- [`principle-clean-cutting-boards`](skills/principle-clean-cutting-boards/SKILL.md)
- [`principle-check-the-oven`](skills/principle-check-the-oven/SKILL.md)
- [`principle-taste-before-serving`](skills/principle-taste-before-serving/SKILL.md)
- [`principle-one-course-at-a-time`](skills/principle-one-course-at-a-time/SKILL.md)
- [`principle-kitchen-muscle-memory`](skills/principle-kitchen-muscle-memory/SKILL.md)

---

## Quickstart & Validation

The repository symlinks `skills/` to `.claude/skills`, `.agents/skills`, and `.cursor/skills` so every skill registers automatically in Claude Code, Cursor, and Antigravity.

```bash
# Validate all 31 modular kitchen skills (YAML frontmatter, directory match, playbooks, and scripts)
bash skills/head-chef-mode/scripts/validate-skills.sh

# Log a prep decision row to decisions.tsv
bash skills/head-chef-mode/scripts/log-decision.sh \
  decisions.tsv "mise-en-place" "Validated all 31 kitchen brigade skills" "Ensure 100% frontmatter and playbook integrity" "skills/head-chef-mode/SKILL.md:1" "VERIFIED"
```
