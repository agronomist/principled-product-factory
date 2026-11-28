---
name: central-commissary
description: Multi-kitchen Central Commissary operations. Covers the Kitchen-Line Stamping Press, Automated Rule-of-Two Mother-Sauce Harvester, Purveyor BOM & Ingredient Price-Shock Simulator, Sealed Mystery-Diner Holdout Twin, First-Tables Progressive Rollout (1% -> 10% -> 50% -> 100%), and Kitchen Service OEE / Theory of Constraints.
---

# Central Commissary & Multi-Kitchen Operations (`/central-commissary`)

Scales a single kitchen into a multi-restaurant commissary system (Software Factory Stamping, Dark-Kitchen Mystery-Diner Holdout Twins, and the Theory of Constraints).

## 1. Kitchen-Line Stamping Press & Rule-of-Two Mother-Sauce Harvester

- **Kitchen-Line Stamping Press**: Never build a new vertical kitchen line from scratch. When an opportunity in [`../dining-room-feedback/SKILL.md`](../dining-room-feedback/SKILL.md) graduates and passes [`../no-empty-calories/SKILL.md`](../no-empty-calories/SKILL.md), stamp out `products/<product-slug>/` with its standard stations (`skills/`, `workflows/factory_dag.yaml`, `evals/golden_cases.jsonl`, and `features/README.md`).
- **Rule-of-Two Mother-Sauce Harvester**: Compare normalized function ASTs across all vertical kitchen lines under `products/*`:
  - `products/a` must never borrow directly from `products/b`'s line (`principle-clean-cutting-boards`).
  - The moment $\ge 2$ kitchen lines prepare the exact same mother sauce or helper function, harvest that shared primitive into the **Central Commissary (`platform/`)** behind a sealed container contract and delete the duplicate product copies.

## 2. Purveyor Bill of Materials (BOM) & Ingredient Price-Shock Simulator

Track every kitchen line's foundation model and external API ingredients in a central Purveyor BOM ledger.
- **Purveyor-Power Stress Test**: Simulate upstream supplier price shocks (e.g., a $3\times$ truffle/token price hike on a primary frontier model) across every dish on the menu simultaneously.
- Identify which dishes can automatically substitute house-distilled stock (`secondary_distilled_model`) while keeping food-cost margin $\ge M_{\min}$, and pre-wire those substitutions before a purveyor price hike hits.

## 3. Sealed Mystery-Diner Holdout Twin (Dark-Kitchen Wind Tunnel)

Line cooks can accidentally over-season for the 10 known recipes in `golden_cases.jsonl`.
- Maintain a **Sealed Mystery-Diner Holdout Twin**: real shadow-traffic orders stored outside the Line Cook's repository read path.
- Replay every candidate recipe against the mystery-diner holdout set and require $100\%$ plating invariant pass rate and food-cost compliance before serving the first table.

## 4. First-Tables Progressive Rollout (`1% -> 10% -> 50% -> 100%`)

Never serve a brand-new dish to the entire dining room at once. Advance through `1% -> 10% -> 50% -> 100%` of tables, checking three live gates at every seating:
1. **Statistical Process Control $\pm 3\sigma$ Ticket-Time Limits**: P99 latency and error rate stay inside $[\mu - 3\sigma, \mu + 3\sigma]$.
2. **Sample Ratio Mismatch (SRM) $\chi^2$ Gate**: Observed control vs. new-dish table counts pass Pearson's $\chi^2$ test at $p \ge 0.01$.
3. **Live Food-Cost Margin Gate**: Realized plate margin $\ge M_{\min}$.

On any breach, immediately 86 the rollout (`0%`) and file a minimized incident card via [`../pantry-backup-and-incident-card/SKILL.md`](../pantry-backup-and-incident-card/SKILL.md).

## 5. Kitchen Service OEE & Theory of Constraints Bottleneck Monitor

Measure **Overall Equipment Effectiveness** across all stations:
$$\text{OEE} = \text{Availability} \times \text{Performance} \times \text{FirstPassYield}$$
- **First-Pass Yield (FPY)**: Fraction of tickets approved by the Blind Pass Inspector on Round 0 without a refire.
- **Food Waste & Refire Cost Ratio**: Compute/token spend burned on dumped pans or refire loops divided by total kitchen spend.
- **Drum-Buffer-Rope**: Pinpoint the **Bottleneck Station** (highest mean ticket time $W$). Pace the Expediter's ticket call rate $\lambda$ to the bottleneck under Little's Law (`WIP_LIMIT = 5`, $L = \lambda W$) and focus prep automation on elevating the bottleneck.
