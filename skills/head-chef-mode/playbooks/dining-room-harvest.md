# Playbook: Dining-Room Feedback Harvest, Kitchen Stamping & Recipe Book Update (`dining-room-harvest.md`)

Use this playbook to close the continuous learning loop: mining plates sent back to the pass, graduating recurring guest requests from $N=1 \to N=3 \to N=10$, stamping out new kitchen lines, harvesting shared prep into the central commissary, sharpening kitchen tools, and updating the skills cookbook.

## Todo List Steps (Copy into Todo Tool First)

1. **Coat-Check PII/NDA Scrub & "Say vs. Do" Codebase Check (`dining-room-feedback`)**:
   - Open [`../../dining-room-feedback/SKILL.md`](../../dining-room-feedback/SKILL.md).
   - If a sales call or customer transcript was provided, replace personal names, emails, and phone numbers with an anonymized account tag (`ACCT-042-Vertical`) so NDA details never leak into Git commits or PR descriptions.
   - Cross-check each transcript complaint against the live codebase (`CONFIRMED_MISSING_CAPABILITY`, `CONFIRMED_BUG`, or `CONFIG_OR_UX_MISUNDERSTANDING` solvable by a 1-line fix-naming error message).
2. **Log to Persistent `dining-room-ledger.tsv` & Compute $N=1 \to 3 \to 10$ + Deal ARR Rollup (`log-guest-feedback.sh`)**:
   - For each validated pain point (filtering out polite Mom-Test compliments via [`../../no-empty-calories/SKILL.md`](../../no-empty-calories/SKILL.md)), run:
     ```bash
     bash .claude/skills/head-chef-mode/scripts/log-guest-feedback.sh \
       "<account_tag>" "<arr_usd>" "<topic_slug>" "<mom_test_tier>" "<say_vs_do>" "<quote>" "<the_schmeer>"
     ```
   - Inspect the cross-session rollup printed by the script (`Distinct Accounts N`, `Total ARR at Stake`, and graduation verdict: `N < 3` quarantined unless Option 1 Garnish takes $\le 30$m; `3 <= N < 10` Stage A [`/amuse-bouche`](../../amuse-bouche/SKILL.md); `N >= 10` Stage B full build).
3. **Unbundle the Problem, Add "The Schmeer" & Prep the Sommelier Follow-Up (`opportunity-brief` + `sommelier-table-pitch`)**:
   - Open [`../../opportunity-brief/SKILL.md`](../../opportunity-brief/SKILL.md): unbundle the requested feature into 3 options (Option 1 Garnish/Knife Twist, Option 2 Bistro 80/20 Special, Option 3 Full Build) and define **"The Schmeer"** (the unspoken next step 30 seconds after the feature finishes—or the offhand sigh the Champion made on the sales call—solvable in $\le 15\%$ extra code).
   - If the transcript is an active sales/renewal deal, run [`../../sommelier-table-pitch/SKILL.md`](../../sommelier-table-pitch/SKILL.md) to output the follow-up Deal Desk packet (Cost of Inaction $\ge 3\times \text{ACV}$, stakeholder notes, Give-Get tension script, and JOLT pilot offer).
4. **Cluster Plates Sent Back (`user_correction_diff`) & Update Bayesian Hunger Beliefs (`dining-room-feedback`)**:
   - Query `user_correction_diff` edits for patterns with $\ge 3$ independent occurrences and combine prior Importance/Satisfaction ratings with empirical `observed_workaround_rate` and `observed_task_drop_off_rate`.
5. **Stamp Out New Kitchen Lines, 86 Zombie Dishes & Update the Cookbook (`central-commissary` + `sharpen-the-knives` + `update-the-cookbook`)**:
   - Extract shared Rule-of-Two helpers into `platform/` ([`../../central-commissary/SKILL.md`](../../central-commissary/SKILL.md)), encode recurring mistakes up the 5-level hierarchy ([`../../sharpen-the-knives/SKILL.md`](../../sharpen-the-knives/SKILL.md)), sunset 30-day expired `FIFO-DATE-DOT` dishes below threshold, and propose surgical lessons via [`../../update-the-cookbook/SKILL.md`](../../update-the-cookbook/SKILL.md).
