# Canonical Formulations, Playbooks, Financial Invariants & Metaphor Bank (`v10`)

This reference accompanies `.claude/skills/principled-product-builder/SKILL.md` and defines the exact mathematical equations, practitioner playbooks, unit-economics invariants, and plain-English metaphors enforced across `principled-product-factory`.

---

## 1. Tier-1 Foundational Science Formulations (Hard Invariants)

### 1.1 Operations Research & Queueing Theory
1. **Little's Law** (John Little, 1961):
   $$L = \lambda \cdot W$$
   - $L$: Mean work-in-progress (WIP) items concurrently active in the DAG orchestrator.
   - $\lambda$: Mean arrival/completion throughput (items per unit time).
   - $W$: Mean cycle time / latency per item.
   - **Enforcement**: `platform/orchestrator/dag_runner.py` enforces a strict semaphore bound `WIP_LIMIT = 5`. Any submission exceeding `WIP_LIMIT` blocks or queues cleanly rather than thrashing downstream LLM or database pools.

2. **Kingman's VUT Approximation** (John Kingman, 1961):
   $$\mathbb{E}[W_q] \approx \left(\frac{\rho}{1 - \rho}\right) \cdot \left(\frac{c_a^2 + c_s^2}{2}\right) \cdot \tau$$
   - $\rho = \lambda / \mu \in [0, 1)$: Server utilization ratio.
   - $c_a^2, c_s^2$: Squared coefficients of variation for inter-arrival and service times.
   - $\tau = 1 / \mu$: Mean service time.
   - **Enforcement**: When frontier LLM service variance $c_s^2$ spikes, tail latency explodes as $\rho \to 1$. The SRE fallback circuit sheds load to `secondary_distilled_model` (lower $\tau$, lower $c_s^2$) or `tertiary_cached_deterministic` ($c_s^2 \approx 0$).

3. **Bellman's Principle of Optimality & Execution Routing** (Richard Bellman, 1957):
   $$V(s) = \max_{a \in \mathcal{A}(s)} \left\{ R(s, a) - C(s, a) + \gamma \sum_{s'} P(s' \mid s, a) V(s') \right\}$$
   - **Enforcement**: `dag_runner.py` computes a Bellman value score over task complexity, failure risk, and unit margin headroom to choose between:
     - `fast_implement`: Single-path deterministic execution when complexity and risk are low or margin headroom is tight.
     - `parallel_fan_out`: Multi-branch speculative/ensemble execution when EVOI exceeds the parallel inference cost and margin headroom permits.

### 1.2 Decision Theory & Causal Econometrics
1. **Expected Value of Information (EVOI)** (Howard Raiffa, 1961):
   $$\text{EVOI}(Y) = \mathbb{E}_Y \left[ \max_{a \in \mathcal{A}} \mathbb{E}_{\theta \mid Y}[U(a, \theta)] \right] - \max_{a \in \mathcal{A}} \mathbb{E}_\theta[U(a, \theta)]$$
   - An AI call or A/B experiment is justified if and only if $\text{EVOI}(Y) > \text{Cost}(Y)$.

2. **CUPED (Controlled-experiment Using Pre-Experiment Data)** (Deng et al., WSDM 2013):
   Given post-treatment outcome $Y$ and pre-experiment baseline covariate $X$ (unaffected by treatment assignment):
   $$\hat{Y}_{\text{CUPED}} = Y - \theta (X - \bar{X}), \quad \text{where } \theta = \frac{\text{Cov}(Y, X)}{\text{Var}(X)}$$
   - Variance reduction factor:
     $$\text{Var}(\hat{Y}_{\text{CUPED}}) = \text{Var}(Y)(1 - \rho_{X,Y}^2)$$
   - Where $\rho_{X,Y}$ is the Pearson correlation between pre-experiment covariate $X$ and outcome $Y$. Implemented in `platform/evals/runner.py`.

3. **Sample Ratio Mismatch (SRM) Chi-Square Gate**:
   Given observed arm counts $(O_1, \dots, O_k)$ and expected counts $(E_1, \dots, E_k)$ under target allocation proportions $(p_1, \dots, p_k)$ with $N = \sum O_i$:
   $$\chi^2 = \sum_{i=1}^k \frac{(O_i - E_i)^2}{E_i} \sim \chi^2_{k-1}$$
   - **Invariant**: If $p\text{-value} < 0.01$ (or $\chi^2$ exceeds the critical value for $\alpha = 0.01$), `platform/evals/runner.py` flags `srm_detected = True` and invalidates the experiment.

4. **Cohen's Kappa ($\kappa$) Evaluator Calibration** (Jacob Cohen, 1960):
   $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
   - $p_o$: Observed proportion of agreement between the automated evaluator and human gold labels.
   - $p_e = \sum_{c} P_{\text{judge}}(c) \cdot P_{\text{human}}(c)$: Expected agreement by chance.
   - **Invariant**: Automated Tier B judge calibration requires $\kappa \ge 0.80$.

### 1.3 Software Correctness & Distributed Systems
1. **Liskov Substitution Principle (LSP)** (Liskov & Wing, 1994):
   - $\text{Pre}_{\text{super}} \implies \text{Pre}_{\text{sub}}$ (Contravariance of preconditions).
   - $\text{Post}_{\text{sub}} \implies \text{Post}_{\text{super}}$ (Covariance of postconditions).
   - Invariant preservation across all state transitions $\sigma \to \sigma'$.
2. **Parnas Information Hiding** (David Parnas, 1972):
   - Every module in `platform/` and `products/` exposes only frozen/validated Pydantic v2 data contracts (`ConfigDict(extra="forbid", frozen=True)` where applicable) and hides internal implementation state.
3. **Saga Compensating Transactions** (Garcia-Molina & Salem, 1987):
   - Forward execution sequence $T_1, T_2, \dots, T_k$ paired with idempotent compensating handlers $C_k, C_{k-1}, \dots, C_1$.
   - On any duplicate SHA-256 error signature or unrecoverable exception at step $k$, execute $[C_{k-1}, \dots, C_1]$ in exact reverse order and emit a structured HITL escalation payload.
4. **Shewhart $\pm 3\sigma$ Statistical Process Control**:
   - Control limits: $\text{UCL} = \mu + 3\sigma$, $\text{LCL} = \mu - 3\sigma$. Any metric excursion outside $[\text{LCL}, \text{UCL}]$ triggers `BlamelessPostMortem` fixture generation.

---

## 2. Tier-2 Practitioner Playbooks

| Canon / Author | Core Diagnostic Question | Factory Enforcement Mechanism |
| :--- | :--- | :--- |
| **Porter Five Forces** | Does our reliance on a single foundation model vendor give suppliers 100% pricing power over our gross margin? | Mandatory 3-tier `FallbackCircuit` (`primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`). |
| **Christensen / Ulwick JTBD** | What measurable job step is the customer trying to eliminate, and what is the underserved outcome score? | Axis 1 (`workflow_elimination_score >= 0.60`) of the AI-Native Prioritization Filter. |
| **April Dunford Positioning** | Compared to what status-quo spreadsheet or manual ops team are we 10x faster/cheaper? | Explicit `Before vs. After` primitive tables in every product `README.md` and Stage B spec. |
| **Hamilton Helmer 7 Powers** | How does today's usage build a proprietary data or process moat that competitors cannot copy tomorrow? | Axis 2 (`flywheel_velocity_score >= 0.60`) via passive `user_correction_diff` telemetry tuples. |
| **Steve Jobs Focus & Craft** | Can we delete 3 configuration knobs and infer the right default automatically? | Zero-friction passive learning signals; no annoying modal surveys. |
| **Marty Cagan 4-Risk Discovery** | Have we proven Value, Usability, Feasibility, and Viability before scaling engineering headcount? | Step 0 Lifecycle Stage Router (`Stage A` vs. `Stage B` vs. `Stage C`). |
| **Google PM Prioritization** | Is this an asymmetric 10x bet or "AI bolt-on theater" where a SQL query suffices? | Hard block when `evoi <= 0` or `deterministic_rule_suffices == True`. |
| **Ramanujam *Monetizing Innovation* + 6-Month Retro-Audit** | Did we validate WTP before building, and did actual 6-month cohort margins match our pricing model? | `MarginGuard` pre-flight check + automated `SixMonthPricingRetroAudit` validator in `platform/metering/margin_guard.py`. |
| **HyperGrowth GTM** | Are customer acquisition loops paying back within 12 months with healthy net dollar expansion? | `CohortPnLValidator` enforcing `cac_payback_months <= 12.0` and `ltv_to_cac_ratio >= 3.0`. |
| **Vercel / Rauch Clarity** | Can a developer clone, understand, and verify the entire factory in 30 seconds? | Deterministic local execution (`pytest -v` + CLI runner) with zero external API keys required. |
| **Google SRE** | Does every production incident permanently immunize the codebase against repeats? | `BlamelessPostMortem` compiling SEV incidents and $3\sigma$ breaches into minimized JSON regression fixtures. |

---

## 3. Contribution Margin & Cohort P&L Invariants

Enforced programmatically in [margin_guard.py](file:///home/antigravity/principled-product-factory/platform/metering/margin_guard.py):

### 3.1 Unit Contribution Margin Gate
For every unit transaction (API call, workflow execution, or seat-month normalized unit):
$$\text{UnitCOGS} = C_{\text{inference}} + C_{\text{data\_api}} + \left(P_{\text{HITL}} \cdot C_{\text{human\_review}}\right) + C_{\text{infra}}$$
$$\text{ContributionMargin} = R_{\text{unit}} - \text{UnitCOGS}$$
$$\text{MarginRatio} = \frac{\text{ContributionMargin}}{R_{\text{unit}}}$$

**Hard Invariants**:
1. $\text{ContributionMargin} \ge M_{\min}$ (`unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`).
2. Every cost component must be non-negative ($\ge 0$), $P_{\text{HITL}} \in [0.0, 1.0]$, and $R_{\text{unit}} > 0$.

### 3.2 Cohort P&L, CAC Payback, and 6-Month Re-Pricing Retro-Audit
For a customer cohort with Monthly Recurring Revenue ($\text{MRR}$), Gross Margin Ratio ($GM\%$), monthly logo/revenue churn rate ($c$), and Customer Acquisition Cost ($\text{CAC}$):
$$\text{MonthlyGrossProfit} = \text{MRR} \cdot GM\%$$
$$\text{CAC Payback (Months)} = \frac{\text{CAC}}{\text{MonthlyGrossProfit}} \le \text{MaxPaybackMonths (default 12.0)}$$
$$\text{LTV} = \frac{\text{MonthlyGrossProfit}}{\max(c, 0.005)}, \quad \frac{\text{LTV}}{\text{CAC}} \ge 3.0$$

**6-Month Re-Pricing Retro-Audit Invariant**:
Every 6 months after launching a pricing tier, compare realized cohort margin $GM_{\text{realized}}\%$ against forecast $GM_{\text{forecast}}\%$. If $GM_{\text{realized}}\% < GM_{\text{forecast}}\% - 0.05$ or realized $P_{\text{HITL}}$ exceeds forecast by $> 50\%$, trigger a mandatory re-pricing or model distillation intervention.

---

## 4. Soccer & Seinfeld Metaphor Bank

Use these canonical metaphors in PR reviews, post-mortems, and architecture decision records (ADRs):

| System Phenomenon | Soccer Metaphor | Seinfeld Metaphor |
| :--- | :--- | :--- |
| **Little's Law WIP Cap (`WIP_LIMIT = 5`)** | **Cruyff's Total Football Spacing**: If all 10 outfield players crowd into the 6-yard box, nobody can complete a pass. Spacing the pitch keeps the ball moving at top speed. | **The Soup Nazi's Queue**: Five customers at the counter max. Step forward, order your bisque, step left. Chaos in the line means "No soup for you!" |
| **Duplicate Error-Signature Halt & Saga Rollback** | **Abandoned Short Corner**: If the defense reads the short-corner routine twice in a row, stop kicking it into the first defender's shins—reset the ball back to the center-backs and reorganize. | **George Parallel Parking**: Don't wedge the Nose-In sedan into the same hydrant 4 times while honking echoes down Amsterdam Ave. Back out immediately (Saga rollback) and call the garage attendant (HITL). |
| **3-Tier SRE Fallback (`primary -> secondary -> tertiary`)** | **Playmaker $\to$ Box-to-Box Midfielder $\to$ Sweeper Keeper**: When the opponent double-teams your #10 (`primary_frontier_model`), pivot through your #8 (`secondary_distilled_model`) or play a safe back-pass to the keeper (`tertiary_cached_deterministic`). | **Jerry's Comedy Club Pivot**: If the new airplane-peanuts bit gets dead silence (`primary` failure), drop smoothly into the battle-tested laundry routine (`secondary`/`tertiary`) so the show never stalls. |
| **Bayesian Kill-Switch (Sunsetting Bad Bets)** | **60th-Minute Tactical Substitution**: Taking off a cold striker with 0.02 xG before he picks up a second yellow card. Save stamina for next Saturday's fixture. | **George's "Do the Opposite"**: Recognizing a dead-end scheme in week 2 instead of dragging it out for a whole season out of sheer stubbornness. |
| **Goodhart's Law & Countervailing Guardrails** | **Sterile 80% Possession**: Passing sideways 900 times between your defenders to juice pass-completion stats while losing 1-0 on a stoppage-time counterattack. | **Kramer & Newman's Michigan Bottle Deposit Run**: Obsessing over gross 10-cent bottle volume while ignoring the postal truck fuel, payload weight, and unit margin math. |
| **AI Bolt-On Theater (`evoi == 0`)** | **Doing Step-Overs in Your Own Penalty Box**: Flashy Ronaldinho tricks 85 yards from the opponent's goal when a simple 5-yard clearance wins the game. | **The Urban Sombrero**: Putting a giant dramatic hat on the J. Peterman catalog cover when customers just wanted a durable umbrella. |
