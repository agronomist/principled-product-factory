# Playbook: Dining-Room Feedback Harvest, Kitchen Stamping & Recipe Book Update (`dining-room-harvest.md`)

Use this playbook to close the continuous learning loop: mining plates sent back to the pass, graduating recurring guest requests from $N=1 \to N=3 \to N=10$, stamping out new kitchen lines, harvesting shared prep into the central commissary, sharpening kitchen tools, and updating the skills cookbook.

## Todo List Steps (Copy into Todo Tool First)

1. **Cluster Plates Sent Back (`user_correction_diff`) (`dining-room-feedback`)**:
   - Open [`../../dining-room-feedback/SKILL.md`](../../dining-room-feedback/SKILL.md).
   - Query the idempotent learning ledger for recurring `(field_name, house_default -> guest_preferred)` edits across independent tickets.
   - For every pattern with $\ge 3$ independent occurrences, auto-synthesize a new golden tasting assertion and a [`../../kitchen-brigade/SKILL.md`](../../kitchen-brigade/SKILL.md) ticket so the house recipe adapts automatically.
2. **Graduate Accumulated Off-Menu Requests ($N=1 \to N=3 \to N=10$) (`dining-room-feedback`)**:
   - Group rejected table requests and diner workarounds by `topic_slug` across distinct `customer_account_id`s:
     - **$N < 3$**: Keep quarantined (`QUARANTINED_NOISE_OR_ONE_OFF`) so one loud table never derails service.
     - **$3 \le N < 10$** (with $\ge \text{time\_commitment}$ and Ulwick score $\ge 10.0$): Promote to `Stage A Test Kitchen Tasting`.
     - **$N \ge 10$** (with $\ge \text{reputation\_commitment}$ or `financial_or_pain_commitment`): Graduate to `Stage B Signature Menu Build`.
3. **Update Bayesian Hunger Beliefs from Diner Workarounds (`dining-room-feedback`)**:
   - Combine prior Importance/Satisfaction ratings with empirical `observed_workaround_rate` and `observed_task_drop_off_rate` via conjugate Bayesian updating. Escalate any job whose posterior Ulwick Opportunity Score crosses $\ge 10.0$.
4. **Stamp Out New Kitchen Lines & Harvest Rule-of-Two Prep (`central-commissary` + `sharpen-the-knives`)**:
   - Open [`../../central-commissary/SKILL.md`](../../central-commissary/SKILL.md).
   - When a graduated opportunity warrants a new vertical kitchen line, run the **Kitchen Line Stamping Press** to scaffold `products/<product-slug>/`.
   - Run the **Rule-of-Two Prep Harvester** across all `products/*`: whenever $\ge 2$ kitchen lines prepare the exact same mother sauce or helper function, extract it into the central commissary (`platform/`) and delete the duplicate product copies.
   - Run [`../../sharpen-the-knives/SKILL.md`](../../sharpen-the-knives/SKILL.md) to encode recurring kitchen mistakes into architecture, container types, or fix-naming alarms.
5. **86 Untouched Zombie Dishes & Update the Cookbook (`no-empty-calories` + `update-the-cookbook`)**:
   - Audit dishes past their 30-day evaluation window: any dish with $< 40\%$ target orders and $< 25\%$ outcome lift is 86'd (`SUNSET_AND_DELETE_CODE`).
   - Run [`../../update-the-cookbook/SKILL.md`](../../update-the-cookbook/SKILL.md) to mine the shift transcript for durable lessons and propose surgical updates to `skills/*/SKILL.md`.
