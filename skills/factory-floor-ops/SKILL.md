---
name: factory-floor-ops
description: Industrial software factory floor operations. Covers the Product-Line Stamping Press, Automated Rule-of-Two AST Harvester, Supply-Chain BOM & Supplier Price-Shock Simulator, Sealed Holdout Digital Twin, Progressive Canary Rollout (1% -> 10% -> 50% -> 100%), and Overall Equipment Effectiveness (OEE / Goldratt Theory of Constraints).
---

# Industrial Factory Floor Operations (`/factory-floor-ops`)

Turns a single-product repository into a multi-product software factory (Greenfield & Short *Software Factories*, StrongDM Dark Factory Holdout Twins, and Eliyahu Goldratt's *Theory of Constraints*).

## 1. Product-Line Stamping Press & Rule-of-Two Harvester

- **Stamping Press**: Never hand-craft a new vertical product from scratch. When an opportunity in [`../customer-flywheel/SKILL.md`](../customer-flywheel/SKILL.md) graduates and passes [`../escape-the-build-trap/SKILL.md`](../escape-the-build-trap/SKILL.md), stamp out `products/<product-slug>/` with its standard structure (`skills/`, `workflows/factory_dag.yaml`, `evals/golden_cases.jsonl`, and `features/README.md`).
- **Rule-of-Two AST Harvester**: Compare normalized function ASTs across all vertical products under `products/*`:
  - `products/a` must never import from `products/b`.
  - The moment $\ge 2$ products implement structurally duplicate logic, extract the shared primitive into `platform/` behind an immutable data contract and delete the duplicate product copies (`principle-build-the-lever`).

## 2. Supply-Chain Bill of Materials (BOM) & Supplier Price-Shock Simulator

Track every product's foundation model and external API dependencies in a central BOM ledger.
- **Porter Supplier-Power Stress Test**: Simulate upstream vendor price shocks (e.g., a $3\times$ token price hike on a primary frontier model) across the entire multi-product portfolio.
- Identify which products can automatically degrade to `secondary_distilled_model` while keeping unit contribution margin $\ge M_{\min}$, and pre-wire those distillation routes before a vendor hike occurs.

## 3. Sealed Holdout Digital Twin (Dark-Factory Wind Tunnel)

Coding agents can overfit to tests stored inside the repository (`golden_cases.jsonl`).
- Maintain a **Sealed Holdout Digital Twin**: shadow-traffic scenarios stored outside the implementer station's read path.
- Replay every candidate build against the sealed holdout set and require $100\%$ invariant pass rate and unit cost compliance before starting a canary rollout.

## 4. Progressive Canary Rollout Controller (`1% -> 10% -> 50% -> 100%`)

Never jump straight from merge to 100% traffic. Advance through `1% -> 10% -> 50% -> 100%`, checking three live gates at every stage:
1. **Shewhart $\pm 3\sigma$ Control Limits**: P99 latency and error rate stay inside $[\mu - 3\sigma, \mu + 3\sigma]$.
2. **Sample Ratio Mismatch (SRM) $\chi^2$ Gate**: Observed control vs. canary arm counts pass Pearson's $\chi^2$ test at $p \ge 0.01$.
3. **Live Contribution Margin Gate**: Realized unit margin $\ge M_{\min}$.

On any breach, auto-revert traffic to `0%` and compile a minimized regression fixture via [`../sre-fallback-and-postmortem/SKILL.md`](../sre-fallback-and-postmortem/SKILL.md).

## 5. Factory Floor OEE & Goldratt Theory of Constraints Monitor

Measure **Overall Equipment Effectiveness** across all stations:
$$\text{OEE} = \text{Availability} \times \text{Performance} \times \text{FirstPassYield}$$
- **First-Pass Yield (FPY)**: Fraction of Foreman runs approved by the cross-vendor reviewer on Round 0 without revision loops.
- **Scrap & Rework Cost Ratio**: Compute/token spend burned on reverted hillclimb brackets or revision loops divided by total spend.
- **Goldratt Drum-Buffer-Rope**: Identify the **Bottleneck Station** (highest mean cycle time $W$). Subordinate upstream arrival rate $\lambda$ to the bottleneck under Little's Law (`WIP_LIMIT = 5`, $L = \lambda W$) and focus distillation/caching on elevating the bottleneck.
