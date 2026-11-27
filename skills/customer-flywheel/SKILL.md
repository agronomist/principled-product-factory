---
name: customer-flywheel
description: Continuous customer learning and adaptation flywheel. Clusters passive user_correction_diff tuples into Foreman work items, accumulates rejected N=1 sales requests into Stage A (N=3) and Stage B (N=10) opportunities, and runs Bayesian JTBD belief updates from live customer workarounds.
---

# Continuous Customer Learning & Adaptation Flywheel (`/customer-flywheel`)

Filtering out bad ideas is only half of product building; the other half is **maximizing validated learning and adapting to how customers actually work** (Teresa Torres *Continuous Discovery Habits* + Eric Ries *Validated Learning*).

## 1. Zero-Friction Correction-Diff Clustering $\to$ Auto-Synthesized Work Items

Never nag customers with thumbs-up/thumbs-down modal surveys. Capture passive, idempotent 4-tuples during normal workflow usage:
$$(\texttt{input\_state},\; \texttt{system\_output},\; \texttt{user\_correction\_diff},\; \texttt{verified\_outcome})$$
- Content-address each 4-tuple by its canonical SHA-256 hash so network retries are deduplicated.
- **Clustering Rule**: Group all non-empty `user_correction_diff` edits by `(field_name, system_default_value -> customer_preferred_value)` across distinct runs.
- **Autonomous Adaptation**: The moment $\ge 3$ independent customer runs override a system default in the same direction:
  1. Synthesize a new golden evaluation case asserting the customer-preferred output.
  2. Synthesize a [`../foreman-pipeline/SKILL.md`](../foreman-pipeline/SKILL.md) work item backed by the empirical diff evidence so the product adapts automatically.

## 2. Emergent Demand & Sales Objection Accumulator ($N=1 \to N=3 \to N=10$)

When a single prospect asks for a new capability in [`../challenger-deal-desk/SKILL.md`](../challenger-deal-desk/SKILL.md), we refuse to derail the roadmap at $N=1$—**but we never throw the signal away**. Record every pain observation by `(topic_slug, customer_account_id)`:

| Distinct Accounts ($N$) | Required Commitment & Ulwick Score | Graduation Action |
| :--- | :--- | :--- |
| **$N < 3$** | Any | **`QUARANTINED_NOISE_OR_ONE_OFF`** (Build-Trap shield stays up). |
| **$3 \le N < 10$** | $\ge \texttt{time\_commitment}$ & Ulwick Score $\ge 10.0$ | **`PROMOTED_TO_STAGE_A_DISCOVERY_PROBE`**: Auto-generates a valid `CustomerEvidenceArtifact` unlocking a fast Stage A prototype. |
| **$N \ge 10$** | $\ge \texttt{reputation\_commitment}$ or $\texttt{financial\_or\_pain\_commitment}$ & Ulwick Score $\ge 10.0$ | **`GRADUATED_TO_STAGE_B_PRODUCTION_BUILD`**: Unlocks full production buildout via [`../foreman-pipeline/SKILL.md`](../foreman-pipeline/SKILL.md) or stamps a new product line. |

## 3. Bayesian JTBD Belief Updating from Live Customer Workarounds

Surveys often underestimate a problem until customers touch the software. Watch two behavioral telemetry signals across sample size $N$:
1. **`observed_workaround_rate`** (fraction of users exporting CSVs, running manual scripts, or hacking around a step) $\implies$ empirical proof of **High Importance**:
   $$I_{\text{emp}} = 1.0 + 9.0 \cdot \text{observed\_workaround\_rate}$$
2. **`observed_task_drop_off_rate`** (fraction of users abandoning or failing the step) $\implies$ empirical proof of **Low Satisfaction**:
   $$S_{\text{emp}} = 10.0 - 9.0 \cdot \text{observed\_task\_drop\_off\_rate}$$

Update prior beliefs $(I_{\text{prior}}, S_{\text{prior}})$ with prior weight $w_0$ via conjugate shrinkage:
$$\theta_{\text{post}} = \frac{w_0 \cdot \theta_{\text{prior}} + N \cdot \theta_{\text{emp}}}{w_0 + N}$$
If the posterior Ulwick Opportunity Score crosses $\ge 10.0$, escalate the job onto the active roadmap immediately.
