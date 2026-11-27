---
name: principle-contribution-margin-floor
description: Apply before invoking AI models, designing workflows, or approving commercial discounts. Enforce positive unit contribution margin >= min_margin, EVOI > Cost, and block AI bolt-on theater where deterministic rules suffice.
---

# Principle: Contribution Margin Floor

Never ship an AI workflow or sign a commercial contract that loses money at the unit level (*Kramer & Newman's Michigan bottle-deposit run*).

- Enforce pre-flight unit economics on every transaction:
  $$\texttt{unit\_revenue} - (\texttt{inference\_cost} + \texttt{data\_api\_cost} + \texttt{hitl\_prob} \cdot \texttt{human\_review\_cost} + \texttt{infra\_cost}) \ge \texttt{min\_margin}$$
- If frontier inference breaches the floor, automatically downgrade to `secondary_distilled_model`; if still below floor, block execution.
- Block **AI Bolt-On Theater** immediately when Expected Value of Information $\text{EVOI} \le \text{Cost}$ or a deterministic SQL query / rule engine suffices.
- Never grant a B2B sales discount without verifying the margin floor AND extracting a concrete **Give-Get** concession.
