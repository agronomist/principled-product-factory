---
name: dining-room-feedback
description: Continuous dining-room learning and recipe adaptation flywheel. Clusters plates sent back to the pass (user_correction_diff) into Brigade tickets, graduates rejected N=1 table requests into Stage A Pop-Ups (N=3) and Stage B Menu Builds (N=10), and runs Bayesian hunger belief updates from live diner workarounds.
---

# Dining-Room Feedback & Recipe Adaptation Flywheel (`/dining-room-feedback`)

Keeping empty calories off the menu is only half of running a great kitchen; the other half is **watching what diners actually eat, what they send back to the pass, and how they season their own plates** (Teresa Torres *Continuous Discovery Habits* + Eric Ries *Validated Learning*).

## 1. Plates Sent Back to the Pass (`user_correction_diff` Clustering)

Never interrupt a diner's meal with a table-tent survey. Passively capture idempotent 4-tuples during normal service:
$$(\texttt{input\_state},\; \texttt{system\_output},\; \texttt{user\_correction\_diff},\; \texttt{verified\_outcome})$$
- Content-address each 4-tuple by its canonical SHA-256 hash so network retries are deduplicated.
- **Clustering Rule**: Group all non-empty `user_correction_diff` edits by `(field_name, house_default_value -> guest_preferred_value)` across distinct orders.
- **Autonomous Recipe Adaptation**: The moment $\ge 3$ independent tables season or override a house default in the same direction:
  1. Synthesize a new golden tasting case asserting the guest-preferred plating.
  2. Synthesize a [`../kitchen-brigade/SKILL.md`](../kitchen-brigade/SKILL.md) ticket backed by the empirical plate-back evidence so the house recipe adapts automatically.

## 2. Off-Menu Request Accumulator ($N=1 \to N=3 \to N=10$)

When a single table asks for an off-menu dish in [`../sommelier-table-pitch/SKILL.md`](../sommelier-table-pitch/SKILL.md), we refuse to derail tonight's service at $N=1$—**but we record the request on the chalkboard**. Track every hunger observation by `(topic_slug, customer_account_id)`:

| Distinct Tables ($N$) | Required Commitment & Ulwick Score | Graduation Action |
| :--- | :--- | :--- |
| **$N < 3$** | Any | **`QUARANTINED_NOISE_OR_ONE_OFF`** (No-Empty-Calories shield stays up). |
| **$3 \le N < 10$** | $\ge \texttt{time\_commitment}$ & Ulwick Score $\ge 10.0$ | **`PROMOTED_TO_STAGE_A_DISCOVERY_PROBE`**: Auto-generates a valid `CustomerEvidenceArtifact` unlocking a Stage A Test-Kitchen pop-up. |
| **$N \ge 10$** | $\ge \texttt{reputation\_commitment}$ or $\texttt{financial\_or\_pain\_commitment}$ & Ulwick Score $\ge 10.0$ | **`GRADUATED_TO_STAGE_B_PRODUCTION_BUILD`**: Unlocks full menu buildout via [`../kitchen-brigade/SKILL.md`](../kitchen-brigade/SKILL.md) or stamps a new kitchen line. |

## 3. Bayesian Hunger Belief Updating from Diner Workarounds

Menu surveys often underestimate a hunger until diners actually sit at the table. Watch two behavioral signals across sample size $N$:
1. **`observed_workaround_rate`** (fraction of diners bringing their own hot sauce, exporting CSVs, or writing manual scripts) $\implies$ empirical proof of **High Importance**:
   $$I_{\text{emp}} = 1.0 + 9.0 \cdot \text{observed\_workaround\_rate}$$
2. **`observed_task_drop_off_rate`** (fraction of diners leaving the course unfinished) $\implies$ empirical proof of **Low Satisfaction**:
   $$S_{\text{emp}} = 10.0 - 9.0 \cdot \text{observed\_task\_drop_off\_rate}$$

Update prior beliefs $(I_{\text{prior}}, S_{\text{prior}})$ with prior weight $w_0$ via conjugate shrinkage:
$$\theta_{\text{post}} = \frac{w_0 \cdot \theta_{\text{prior}} + N \cdot \theta_{\text{emp}}}{w_0 + N}$$
If the posterior Ulwick Opportunity Score crosses $\ge 10.0$, escalate the dish onto the active Test-Kitchen prep list immediately.
