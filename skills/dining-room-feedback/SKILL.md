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

## 2. Persistent Gong & Customer Call Ledger ($N=1 \to N=3 \to N=10$ + Deal ARR Rollup)

Because Claude Code sessions are ephemeral, off-menu requests from Gong sales calls, renewal reviews, and support tickets MUST be written to the persistent **`dining-room-ledger.tsv`** file on disk using [`log-guest-feedback.sh`](../head-chef-mode/scripts/log-guest-feedback.sh):

```bash
bash .claude/skills/head-chef-mode/scripts/log-guest-feedback.sh \
  "ACCT-042-Fintech" \
  "60000" \
  "webhook-replay-cli" \
  "financial_or_pain_commitment" \
  "CONFIRMED_IN_CODE" \
  "Analysts spend 6 hours every Friday reconciling failed webhooks" \
  "Auto-generate copy-paste curl replay command + 1-line CFO summary flag"
```

### The 5 Rules of Gong Call & Transcript Harvesting
1. **Coat-Check PII & NDA Scrub First**:
   - Before any customer transcript quote crosses into `dining-room-ledger.tsv`, prep notes, branch names, or GitHub PRs, replace person names, raw emails, and phone numbers with an anonymized account tag (`ACCT-042-Fintech`). `log-guest-feedback.sh` automatically scrubs email addresses (`[REDACTED_EMAIL]`), phone numbers (`[REDACTED_PHONE]`), and formula-injection prefixes.
2. **The "Say vs. Do" Codebase & Telemetry Check**:
   - Buyers on sales calls frequently misdiagnose technical root causes. Cross-check what they *said* on the Gong call against the live codebase and logs (`CONFIRMED_MISSING_CAPABILITY`, `CONFIRMED_BUG`, or `CONFIG_OR_UX_MISUNDERSTANDING` solvable by a 1-line fix-naming error message).
3. **Deal ARR at Stake vs. Engineering Build Cost**:
   - Weigh total `arr_usd` unlocked across $N$ accounts in `dining-room-ledger.tsv` against estimated build shifts:
     $$\text{DealDeskROI} = \frac{\sum_{i=1}^{N} \text{ARR}_i}{\text{BuildShifts} + \text{AnnualMaintenanceCost}}$$
4. **Automatic $N=1 \to 3 \to 10$ Graduation**:
   - **$N < 3$**: `QUARANTINED_ONE_OFF` (hold the menu shield unless an Option 1 Garnish/Knife Twist takes $\le 30$ minutes).
   - **$3 \le N < 10$** (with $\ge \texttt{time\_commitment}$ & Ulwick $\ge 10.0$): `PROMOTED_TO_STAGE_A_DISCOVERY_PROBE` (serve a 5-minute [`/amuse-bouche`](../amuse-bouche/SKILL.md)).
   - **$N \ge 10$** (with $\ge \texttt{reputation\_commitment}$ or $\texttt{financial\_or\_pain\_commitment}$): `GRADUATED_TO_STAGE_B_PRODUCTION_BUILD`.
5. **Billy Crystal's "The Schmeer" Column (`the_schmeer`)**:
   - For every real pain point extracted from a Gong transcript, log not only what the customer asked for (the bagel), but **"The Schmeer"**—the unspoken next step 30 seconds after their request (or the offhand sigh the Champion made on the call) that we can solve in $\le 15\%$ extra code to blow their mind on the follow-up demo.

## 3. Bayesian Hunger Belief Updating from Diner Workarounds

Menu surveys often underestimate a hunger until diners actually sit at the table. Watch two behavioral signals across sample size $N$:
1. **`observed_workaround_rate`** (fraction of diners bringing their own hot sauce, exporting CSVs, or writing manual scripts) $\implies$ empirical proof of **High Importance**:
   $$I_{\text{emp}} = 1.0 + 9.0 \cdot \text{observed\_workaround\_rate}$$
2. **`observed_task_drop_off_rate`** (fraction of diners leaving the course unfinished) $\implies$ empirical proof of **Low Satisfaction**:
   $$S_{\text{emp}} = 10.0 - 9.0 \cdot \text{observed\_task\_drop\_off\_rate}$$

Update prior beliefs $(I_{\text{prior}}, S_{\text{prior}})$ with prior weight $w_0$ via conjugate shrinkage:
$$\theta_{\text{post}} = \frac{w_0 \cdot \theta_{\text{prior}} + N \cdot \theta_{\text{emp}}}{w_0 + N}$$
If the posterior Ulwick Opportunity Score crosses $\ge 10.0$, escalate the dish onto the active Test-Kitchen prep list immediately.
