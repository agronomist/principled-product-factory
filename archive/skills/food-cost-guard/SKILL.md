---
name: food-cost-guard
description: Food-Cost & Unit Contribution Margin Gate, 4-Axis AI-Native Recipe Filter, Cohort P&L / CAC Payback Validator, and 6-Month Menu Re-Pricing Retro-Audit. Use when evaluating unit economics, ingredient/token/HITL costs, menu pricing tiers, or blocking molecular-gastronomy AI theater where EVOI <= 0.
---

# Food-Cost Guard & Recipe Filter (`/food-cost-guard`)

Running a kitchen is an exercise in ingredient and labor allocation. No dish, model call, or table contract may bypass food-cost contribution margin and EVOI guardrails.

## 1. The Food-Cost (Unit Contribution Margin) Gate

Before firing an expensive frontier model burner or approving a workflow recipe, compute:
$$\text{PlateCOGS} = C_{\text{inference}} + C_{\text{data\_api}} + \left(P_{\text{HITL}} \cdot C_{\text{human\_review}}\right) + C_{\text{infra}}$$
$$\text{ContributionMargin} = R_{\text{plate}} - \text{PlateCOGS} \ge M_{\min}$$

- **If $\text{ContributionMargin} \ge M_{\min}$**: `APPROVED`.
- **If $\text{ContributionMargin} < M_{\min}$ on `primary_frontier_model`**: Recompute using `secondary_distilled_model` ($0.20\times$ inference cost). If house-stock distillation restores $\text{ContributionMargin} \ge M_{\min}$, emit `DOWNGRADE_TO_DISTILLED` (*subbing off the expensive #10 playmaker for the #8 box-to-box midfielder*).
- **If $\text{ContributionMargin} < M_{\min}$ even after distillation**: **86'd / BLOCKED** (*the cross-state bottle-deposit mail truck: losing money on every plate served*).

## 2. The 4-Axis Recipe Filter (Blocking Molecular-Gastronomy AI Theater)

Score every proposed AI capability from $0.0$ to $1.0$ across four axes:
1. **Prep Elimination (`workflow_elimination`)**: Collapses multi-step human prep drudgery into an autonomous dish completion (not just adding another chat garnish the user has to babysit).
2. **Dining-Room Flywheel (`flywheel_velocity`)**: Passively captures zero-friction `(input_state, system_output, user_correction_diff, verified_outcome)` tuples when plates come back to the pass—without nagging diners with table-tent surveys.
3. **Deterministic Tasting (`deterministic_verifiability`)**: Output is verifiable via contract postconditions, container schemas, or calibrated Cohen's $\kappa \ge 0.80$ tasters.
4. **Food-Cost Resilience (`unit_margin_resilience`)**: Survives worst-case token expansion and human-in-the-loop (HITL) refire rates.

**Hard Block Against Molecular-Gastronomy Foam Theater**:
Reject immediately if:
- Expected Value of Information $\text{EVOI} \le \text{Cost}$, OR
- A deterministic SQL query, regex, or standard knife cut suffices (`deterministic_rule_suffices == true` — *doing flashy Ronaldinho step-overs inside your own penalty box*), OR
- Any axis $< 0.60$ or composite mean $< 0.70$.

## 3. Dining-Room P&L, CAC Payback & 6-Month Menu Re-Pricing Retro-Audit

For Stage B/C kitchens:
- **Gross Margin Ratio**: $\ge 65\%$.
- **Table Acquisition (CAC) Payback Period**: $\frac{\text{CAC}}{\text{ARPA} \times GM\%} \le 12.0\text{ months}$.
- **LTV / CAC**: $\ge 3.0$, **Annualized Net Dollar Retention (NDR)**: $\ge 120\%$.
- **Mandatory 6-Month Menu Re-Pricing Retro-Audit** (Ramanujam *Monetizing Innovation*): Compare realized 6-month cohort food-cost margin and refire (HITL) probability against launch WTP forecasts. If realized margin drifted down by $> 5\%$ or refire probability drifted up by $> 50\%$, trigger an immediate menu re-pricing or stock-distillation task.
