---
name: margin-guard
description: Unit Contribution Margin Gate, 4-Axis AI-Native Prioritization Filter, Cohort P&L / CAC Payback Validator, and 6-Month Re-Pricing Retro-Audit. Use when evaluating unit economics, token/HITL costs, pricing tiers, or blocking AI bolt-on theater where EVOI <= 0.
---

# Margin Guard & AI-Native Filter (`/margin-guard`)

Software engineering and AI orchestration are exercises in capital allocation. No workflow, model call, or commercial deal may bypass unit contribution margin and EVOI guardrails.

## 1. The Unit Contribution Margin Gate

Before invoking a frontier LLM or approving a workflow architecture, compute:
$$\text{UnitCOGS} = C_{\text{inference}} + C_{\text{data\_api}} + \left(P_{\text{HITL}} \cdot C_{\text{human\_review}}\right) + C_{\text{infra}}$$
$$\text{ContributionMargin} = R_{\text{unit}} - \text{UnitCOGS} \ge M_{\min}$$

- **If $\text{ContributionMargin} \ge M_{\min}$**: `APPROVED`.
- **If $\text{ContributionMargin} < M_{\min}$ on `primary_frontier_model`**: Recompute using `secondary_distilled_model` ($0.20\times$ inference cost). If distillation restores $\text{ContributionMargin} \ge M_{\min}$, emit `DOWNGRADE_TO_DISTILLED` (*subbing off the expensive #10 playmaker for the #8 box-to-box midfielder*).
- **If $\text{ContributionMargin} < M_{\min}$ even after distillation**: **BLOCKED** (*Kramer & Newman's Michigan bottle-deposit run: losing money on every mile driven*).

## 2. The 4-Axis AI-Native Prioritization Filter (Blocking AI Bolt-On Theater)

Score every proposed AI capability from $0.0$ to $1.0$ across four axes:
1. **Workflow Elimination**: Collapses multi-step human drudgery into an autonomous state transition (not just adding another chat sidebar the user has to babysit).
2. **Flywheel Velocity**: Passively emits zero-friction `(input_state, system_output, user_correction_diff, verified_outcome)` tuples during normal usage without nagging users with thumbs-up/down popups.
3. **Deterministic Verifiability**: Output is verifiable via Liskov postconditions, schema invariants, or calibrated Cohen's $\kappa \ge 0.80$ judges.
4. **Unit Margin Resilience**: Survives worst-case token expansion and HITL escalation rates.

**Hard Block Against AI Bolt-On Theater**:
Reject immediately if:
- Expected Value of Information $\text{EVOI} \le \text{Cost}$, OR
- A deterministic SQL query, regex, or rule engine suffices (`deterministic_rule_suffices == true` — *doing flashy Ronaldinho step-overs inside your own penalty box*), OR
- Any axis $< 0.60$ or composite mean $< 0.70$.

## 3. Cohort P&L, CAC Payback & 6-Month Re-Pricing Retro-Audit

For Stage B/C products:
- **Gross Margin Ratio**: $\ge 65\%$.
- **CAC Payback Period**: $\frac{\text{CAC}}{\text{ARPA} \times GM\%} \le 12.0\text{ months}$.
- **LTV / CAC**: $\ge 3.0$, **Annualized Net Dollar Retention (NDR)**: $\ge 120\%$.
- **Mandatory 6-Month Re-Pricing Retro-Audit** (Ramanujam *Monetizing Innovation*): Compare realized 6-month cohort gross margin and HITL escalation probability against launch WTP forecasts. If realized gross margin drifted down by $> 5\%$ or HITL probability drifted up by $> 50\%$, trigger an immediate re-pricing or model distillation task.
