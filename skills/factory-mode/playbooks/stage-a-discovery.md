# Playbook: Stage A 0-to-1 Discovery & Anti-Build-Trap Triage (`stage-a-discovery.md`)

Use this playbook when evaluating a new product concept, feature request, or AI workflow proposal before committing engineering build capacity.

## Todo List Steps (Copy into Todo Tool First)

1. **Step 0 Lifecycle Stage & Bayesian Prior Declaration**:
   - Classify the initiative into `Stage A (0-to-1 Discovery)`, `Stage B (PMF & Growth)`, or `Stage C (Enterprise & Multi-Product Scale)`.
   - Declare the prior probability of success $P(H)$, minimum viable posterior kill-switch threshold $P_{\text{kill}}$, and exploration timebox/sample size.
2. **Run the Anti-Build-Trap Gate (`escape-the-build-trap`)**:
   - Open [`../../escape-the-build-trap/SKILL.md`](../../escape-the-build-trap/SKILL.md).
   - Compute Tony Ulwick's JTBD Opportunity Score:
     $$\text{OpportunityScore} = \text{Importance} + \max(\text{Importance} - \text{Satisfaction}, 0)$$
   - Grade customer evidence on **The Mom Test Commitment Ladder** (`speculative_idea`, `polite_compliment`, `time_commitment`, `reputation_commitment`, `financial_or_pain_commitment`).
   - **Hard Block**: If the commitment tier is `speculative_idea` (*"someone at some point will like it"*) or `polite_compliment`, or if $\text{OpportunityScore} < 10.0$, **reject the build** and explain why using the *Kramer's Coffee Table Book / Urban Sombrero* metaphor.
3. **Run the 4-Axis AI-Native Filter & Contribution Margin Gate (`margin-guard`)**:
   - Open [`../../margin-guard/SKILL.md`](../../margin-guard/SKILL.md).
   - Score all 4 axes: Workflow Elimination, Flywheel Velocity (passive `user_correction_diff` capture), Deterministic Verifiability, and Unit Margin Resilience.
   - Compute Expected Value of Information ($\text{EVOI}$). If $\text{EVOI} \le 0$ or a deterministic SQL/regex rule suffices, block as **AI Bolt-On Theater** (*doing step-overs in your own penalty box*).
   - Verify pre-flight unit economics: `unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`.
4. **Sequence Riskiest-Unknown-First Falsification Probe (`principle-sequence-verifiable-units`)**:
   - If approved for a Stage A discovery probe, design the cheapest falsification experiment (highest $\frac{\text{EVOI} \times (1 + P_{\text{fail}})}{\text{Cost}}$) to test willingness-to-pay and core value before building infrastructure.
5. **Define Post-Ship Zombie Sunset Predicate**:
   - Record the falsifiable customer behavior shift (`baseline_metric -> target_metric` over `evaluation_window_days`) so features with $< 40\%$ target adoption and $< 25\%$ outcome lift are automatically deleted post-ship.
