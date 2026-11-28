# Playbook: Test Kitchen Tasting & Menu Triage (`test-kitchen-tasting.md`)

Use this playbook when evaluating a new product concept, menu addition, or AI capability before committing line-cook capacity.

## Todo List Steps (Copy into Todo Tool First)

1. **Step 0 Menu Stage & Bayesian Kill-Switch Declaration**:
   - Classify the dish into `Stage A (Test Kitchen 0-to-1)`, `Stage B (Signature Menu & Growth)`, or `Stage C (Multi-Kitchen Franchise Scale)`.
   - Declare the prior probability of success $P(H)$, minimum viable posterior kill-switch threshold $P_{\text{kill}}$, and tasting sample size.
2. **Run the No-Empty-Calories Gate (`no-empty-calories`)**:
   - Open [`../../no-empty-calories/SKILL.md`](../../no-empty-calories/SKILL.md).
   - Compute Tony Ulwick's JTBD Opportunity Score:
     $$\text{OpportunityScore} = \text{Importance} + \max(\text{Importance} - \text{Satisfaction}, 0)$$
   - Grade guest evidence on **The Mom Test Commitment Ladder** (`speculative_idea`, `polite_compliment`, `time_commitment`, `reputation_commitment`, `financial_or_pain_commitment`).
   - **Hard 86**: If the commitment tier is `speculative_idea` (*"diners at some point will order it"*) or `polite_compliment`, or if $\text{OpportunityScore} < 10.0$, **86 the dish** and explain why using the *Kramer's Coffee Table Book / Urban Sombrero* metaphor.
3. **Verify Signature Dish Positioning & Moat (`signature-dish-moat`)**:
   - Open [`../../signature-dish-moat/SKILL.md`](../../signature-dish-moat/SKILL.md).
   - Walk through April Dunford's 5-step positioning canvas and verify at least one of Hamilton Helmer's **7 Powers** while defending against ingredient supplier power (Porter's Five Forces).
4. **Run the 4-Axis AI-Native Filter & Food-Cost Gate (`food-cost-guard`)**:
   - Open [`../../food-cost-guard/SKILL.md`](../../food-cost-guard/SKILL.md).
   - Score Workflow Elimination, Flywheel Velocity (passive `user_correction_diff` capture), Deterministic Verifiability, and Unit Margin Resilience.
   - If $\text{EVOI} \le 0$ or a deterministic recipe suffices, block as **Molecular-Gastronomy Foam Theater** (*doing step-overs in your own penalty box*).
   - Verify pre-flight food cost: `unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`.
5. **Serve the Amuse-Bouche First & Stamp a FIFO Date Dot (`amuse-bouche` + `fifo-walk-in` + `principle-one-course-at-a-time`)**:
   - For `Stage A (Test Kitchen 0-to-1)` features, serve a working 5-minute single-bite interactive/CLI slice on fixture data via [`../../amuse-bouche/SKILL.md`](../../amuse-bouche/SKILL.md) before building database migrations or retry plumbing.
   - Order prep steps by **Riskiest-Ingredient-First** ($\frac{\text{EVOI} \times (1 + P_{\text{fail}})}{\text{Cost}}$).
   - Stamp a green painter's tape **`FIFO-DATE-DOT`** expiration tag ([`../../fifo-walk-in/SKILL.md`](../../fifo-walk-in/SKILL.md)) recording the 30-day **86-the-Dish Sunset Threshold** ($< 40\%$ target orders and $< 25\%$ outcome lift $\implies$ remove from menu and delete code).
