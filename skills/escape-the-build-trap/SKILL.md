---
name: escape-the-build-trap
description: Anti-Build-Trap customer value gate and post-ship zombie feature sunset check. Use before building any feature or accepting a roadmap request to prove real customer value (Ulwick JTBD Opportunity Score >= 10.0) and skin-in-the-game commitment (The Mom Test), and post-launch to delete low-adoption zombie features.
---

# Escape the Build Trap (`/escape-the-build-trap`)

An autonomous software factory makes *building* 10x faster—which makes falling into **Melissa Perri's "Build Trap"** (measuring success by pull requests shipped rather than customer problems solved) 10x more dangerous. We build for the customer to solve an acute, underserved problem—**never** *"just because someone at some point will like it."*

## 1. Frame the Customer Job-to-Be-Done (Ulwick Opportunity Score)

Before writing a plan or code for any feature, write down:
- **Customer Segment**: Who specifically is struggling?
- **Struggling Moment**: What concrete event causes their current workaround to fail?
- **Desired Customer Outcome**: What measurable progress are they hiring us to achieve (never frame this as a UI widget)?
- **Importance ($I \in [1..10]$)** and **Current Satisfaction ($S \in [1..10]$)**.

Compute **Tony Ulwick's Outcome-Driven Innovation (ODI) Opportunity Score**:
$$\text{OpportunityScore} = I + \max(I - S, 0)$$

- **$\text{OpportunityScore} < 10.0$**: **BLOCKED (`BLOCKED_OVERSERVED_JTBD`)**. Customers are already satisfied enough with their status-quo workaround (*Seinfeld metaphor: manufacturing Kramer's Coffee Table Book or The Urban Sombrero*).
- **$\text{OpportunityScore} \ge 10.0$** ($\ge 12.0$ for Stage B/C): Genuine underserved customer outcome.

## 2. Grade Skin-in-the-Game on *The Mom Test* Commitment Ladder

Polite praise has zero predictive validity. Classify the empirical customer evidence:

| Tier | What the Customer Did | Factory Verdict |
| :--- | :--- | :--- |
| **`speculative_idea`** | Internal brainstorm (*"someone at some point will like this"*) | **BLOCKED** (`BLOCKED_SPECULATIVE_BUILD_TRAP`) |
| **`polite_compliment`** | *"That sounds neat, let me know when you launch"* | **BLOCKED** (`BLOCKED_SPECULATIVE_BUILD_TRAP`) |
| **`time_commitment`** | Spent $\ge 45$ mins walking through live data or building a manual CSV workaround ($n \ge 3$ accounts) | **Stage A Discovery Probe Only** (`APPROVED_DISCOVERY_PROTOTYPE_ONLY`) |
| **`reputation_commitment`** | Champion introduced procurement / executive decision-makers ($n \ge 10$ Stage B accounts) | **Approved for Production Build** (`APPROVED_FOR_BUILD`) |
| **`financial_or_pain_commitment`** | Signed LOI, paid pilot deposit, contractual WTP, or verified production churn/ticket spike with cited evidence pointers ($n \ge 10$ Stage B / $n \ge 25$ Stage C) | **Approved for Production Build** (`APPROVED_FOR_BUILD`) |

## 3. Require a Falsifiable Customer Behavior Shift (Outcome vs. Output)

Never accept an output checkbox (*"Ship settings modal v2"*). Require:
- **`falsifiable_outcome_metric`**: The customer behavior metric that must move.
- **`baseline_metric_value` $\to$ `target_metric_value`** within **`evaluation_window_days`** (default 30 days).
- If `target == baseline`, block immediately (`BLOCKED_NO_MEASURABLE_OUTCOME_SHIFT`).

## 4. Post-Ship Zombie Feature Sunset Loop (`principle-subtract-before-you-add`)

Shipping a PR is the start of accountability, not the finish line. At `evaluation_window_days` post-ship, measure:
- $\text{AdoptionRatio} = \frac{\text{RealizedAdoptionRate}}{\text{TargetAdoptionRate}}$
- $\text{OutcomeLiftRatio} = \frac{\text{RealizedDelta}}{\text{PromisedDelta}}$

If $\text{AdoptionRatio} < 0.40$ AND $\text{OutcomeLiftRatio} < 0.25$, classify the feature as a **Zombie Feature** (`SUNSET_AND_DELETE_CODE`) and open a cleanup PR to delete the dead code (*George Costanza's relationship exit: pull the plug cleanly rather than paying permanent maintenance tax*).
