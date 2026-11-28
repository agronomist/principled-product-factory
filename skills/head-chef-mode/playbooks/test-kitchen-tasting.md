# Playbook: Test Kitchen Tasting & Menu Triage (`test-kitchen-tasting.md`)

Use this playbook when evaluating a new product concept, menu addition, or AI capability before committing line-cook capacity.

## Todo List Steps (Copy into Todo Tool First)

1. **Step 0 Menu Stage, Opportunity Reframe & 3 Competing Options (`opportunity-brief`)**:
   - Classify the dish into `Stage A (Test Kitchen 0-to-1)`, `Stage B (Signature Menu & Growth)`, or `Stage C (Multi-Kitchen Franchise Scale)`.
   - Open [`../../opportunity-brief/SKILL.md`](../../opportunity-brief/SKILL.md): strip off the requester's prescribed solution, answer **The 4 Opportunity Questions** (Business Objective, Leading-Indicator Key Result, Diner Problem, Target Table Persona), and sketch **3 competing dish options** (1. Garnish/Knife Twist, 2. Bistro 80/20 Special, 3. Full Tasting-Menu Course).
   - Declare the prior probability of success $P(H)$, minimum viable posterior kill-switch threshold $P_{\text{kill}}$, and tasting sample size.
2. **Run The Four Big Discovery Risks & No-Empty-Calories Gate (`four-tasting-risks` + `no-empty-calories`)**:
   - Open [`../../four-tasting-risks/SKILL.md`](../../four-tasting-risks/SKILL.md) and [`../../no-empty-calories/SKILL.md`](../../no-empty-calories/SKILL.md).
   - **Risk 1 — Value Risk**: Compute the JTBD Opportunity Score ($\text{Importance} + \max(\text{Importance} - \text{Satisfaction}, 0) \ge 10.0$) and grade guest evidence on **The Mom Test Commitment Ladder**. If speculative (*"diners at some point will order it"*), **86 the dish** (*Novelty Dish Nobody Ordered*).
   - **Risk 2 — Usability Risk ([`../../plating-and-experience/SKILL.md`](../../plating-and-experience/SKILL.md))**: Verify Time-to-First-Bite $\le 3$ steps, Empty-Plate first-run guidance, and Burned-Plate fix-naming errors.
   - **Risk 3 — Feasibility Risk**: Have [`sous-chef-planner`](../../../agents/sous-chef-planner.md) run a Day-0 feasibility check against the live codebase to see if tweaking 10% of the recipe makes it $5\times$ cheaper to cook.
   - **Risk 4 — Business Viability Risk**: Verify compliance/allergy constraints ([`../../allergy-alert/SKILL.md`](../../allergy-alert/SKILL.md)), GTM channel fit, and menu cannibalization. Enforce **High-Integrity Reservations** (zero hard delivery date promises until all 4 risks are retired).
3. **Verify Signature Dish Positioning & Moat (`signature-dish-moat`)**:
   - Open [`../../signature-dish-moat/SKILL.md`](../../signature-dish-moat/SKILL.md).
   - Walk through the 5-step positioning canvas and verify at least one of Hamilton the **7 Structural Moats** while defending against ingredient supplier power (Supplier & Competitive Forces).
4. **Run the 4-Axis AI-Native Filter & Food-Cost Gate (`food-cost-guard`)**:
   - Open [`../../food-cost-guard/SKILL.md`](../../food-cost-guard/SKILL.md).
   - Score Workflow Elimination, Flywheel Velocity (passive `user_correction_diff` capture), Deterministic Verifiability, and Unit Margin Resilience.
   - If $\text{EVOI} \le 0$ or a deterministic recipe suffices, block as **Molecular-Gastronomy Foam Theater** (*doing step-overs in your own penalty box*).
   - Verify pre-flight food cost: `unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`.
5. **Serve the Amuse-Bouche First, Wire Outcome Telemetry & Stamp a FIFO Date Dot (`amuse-bouche` + `plating-and-experience` + `fifo-walk-in`)**:
   - For `Stage A (Test Kitchen 0-to-1)` features, serve a working 5-minute single-bite interactive/CLI slice on fixture data via [`../../amuse-bouche/SKILL.md`](../../amuse-bouche/SKILL.md) before building database migrations or retry plumbing.
   - Require an **Outcome Telemetry Hook (`Plated != Eaten`)** so adoption is measured from Day 1, order prep steps by **Riskiest-Ingredient-First** ($\frac{\text{EVOI} \times (1 + P_{\text{fail}})}{\text{Cost}}$), and stamp a **`FIFO-DATE-DOT`** tag ([`../../fifo-walk-in/SKILL.md`](../../fifo-walk-in/SKILL.md)) enforcing the 30-day **86-the-Dish Sunset Threshold**.
