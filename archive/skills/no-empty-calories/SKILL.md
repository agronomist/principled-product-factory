---
name: no-empty-calories
description: Anti-Build-Trap guest value gate and 30-day 86-the-dish sunset check. Use before putting any dish on the menu or accepting a feature request to prove real guest hunger (JTBD Opportunity Score >= 10.0) and skin-in-the-game commitment (The Mom Test), and post-launch to 86 untouched dishes.
---

# No Empty Calories (`/no-empty-calories`)

A high-speed kitchen makes *cooking* 10x faster—which makes falling into **the "Build Trap"** (measuring success by plates leaving the window rather than guests nourished) 10x more dangerous. We cook for the guest to satisfy an acute, underserved hunger—**never** *"just because someone at some point might order it."*

## 1. Frame the Guest Hunger (JTBD Opportunity Score)

Before writing a recipe or firing a burner for any feature, write down:
- **Guest Segment**: Who specifically is hungry?
- **Struggling Moment**: What concrete event causes their current meal or workaround to fail?
- **Desired Guest Outcome**: What measurable progress are they hiring our kitchen to deliver (never frame this as a UI garnish)?
- **Importance ($I \in [1..10]$)** and **Current Satisfaction ($S \in [1..10]$)**.

Compute **Tony Opportunity Score's Outcome-Driven Innovation (ODI) Opportunity Score**:
$$\text{OpportunityScore} = I + \max(I - S, 0)$$

- **$\text{OpportunityScore} < 10.0$**: **86'd (`BLOCKED_OVERSERVED_JTBD`)**. Diners are already satisfied with their current meal (*Everyday metaphor: manufacturing a novelty dish nobody ordered or a novelty menu distraction*).
- **$\text{OpportunityScore} \ge 10.0$** ($\ge 12.0$ for Stage B/C): Genuine underserved guest outcome.

## 2. Grade Skin-in-the-Game on *The Mom Test* Commitment Ladder

Polite compliments about a menu idea have zero predictive validity. Classify the empirical guest evidence:

| Tier | What the Guest Did | Kitchen Verdict |
| :--- | :--- | :--- |
| **`speculative_idea`** | Kitchen brainstorm (*"diners at some point will order this"*) | **86'd** (`BLOCKED_SPECULATIVE_BUILD_TRAP`) |
| **`polite_compliment`** | *"That sounds delicious, let me know when you open"* | **86'd** (`BLOCKED_SPECULATIVE_BUILD_TRAP`) |
| **`time_commitment`** | Spent $\ge 45$ mins in a tasting session with live data or hacking a manual CSV workaround ($n \ge 3$ tables) | **Stage A Test-Kitchen Pop-Up Only** (`APPROVED_DISCOVERY_PROTOTYPE_ONLY`) |
| **`reputation_commitment`** | Champion brought executive decision-makers to the table ($n \ge 10$ Stage B accounts) | **Approved for Menu Build** (`APPROVED_FOR_BUILD`) |
| **`financial_or_pain_commitment`** | Paid reservation deposit, signed LOI, contractual WTP, or verified production churn/ticket spike with cited evidence pointers ($n \ge 10$ Stage B / $n \ge 25$ Stage C) | **Approved for Menu Build** (`APPROVED_FOR_BUILD`) |

## 3. Require a Falsifiable Guest Behavior Shift (Outcome vs. Output)

Never accept an output checkbox (*"Plate settings modal v2"*). Require:
- **`falsifiable_outcome_metric`**: The guest behavior metric that must move.
- **`baseline_metric_value` $\to$ `target_metric_value`** within **`evaluation_window_days`** (default 30 days).
- If `target == baseline`, 86 immediately (`BLOCKED_NO_MEASURABLE_OUTCOME_SHIFT`).

## 4. 30-Day "86-the-Dish" Zombie Sunset Loop

Putting a dish on the menu is the start of accountability, not the finish line. At `evaluation_window_days` post-launch, measure:
- $\text{OrderRatio} = \frac{\text{RealizedAdoptionRate}}{\text{TargetAdoptionRate}}$
- $\text{OutcomeLiftRatio} = \frac{\text{RealizedDelta}}{\text{PromisedDelta}}$

If $\text{OrderRatio} < 0.40$ AND $\text{OutcomeLiftRatio} < 0.25$, **86 the dish** (`SUNSET_AND_DELETE_CODE`) and open a cleanup PR to delete the dead recipe (*George Costanza's relationship exit: pull the plug cleanly rather than paying permanent walk-in freezer tax*).
