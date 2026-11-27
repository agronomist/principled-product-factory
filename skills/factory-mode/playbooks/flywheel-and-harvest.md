# Playbook: Customer Adaptation Flywheel, Product Stamping & Rule-of-Two Harvest (`flywheel-and-harvest.md`)

Use this playbook to close the continuous learning loop: mining passive customer correction diffs, graduating accumulated sales objections from $N=1 \to N=3 \to N=10$, stamping out new vertical product lines, harvesting shared primitives into `platform/`, and sunsetting zombie features.

## Todo List Steps (Copy into Todo Tool First)

1. **Cluster Passive Customer Correction Diffs (`customer-flywheel`)**:
   - Open [`../../customer-flywheel/SKILL.md`](../../customer-flywheel/SKILL.md).
   - Query the idempotent learning ledger for recurring `(field_name, system_default -> customer_preferred)` edits across independent runs.
   - For every pattern with $\ge 3$ independent occurrences, auto-synthesize a new golden test case assertion and a Foreman adaptation work item.
2. **Evaluate Accumulated Demand & Sales Objections ($N=1 \to N=3 \to N=10$) (`customer-flywheel`)**:
   - Group rejected sales requests and customer workarounds by `topic_slug` across distinct `customer_account_id`s:
     - **$N < 3$**: Keep quarantined (`QUARANTINED_NOISE_OR_ONE_OFF`) to protect against the Build Trap.
     - **$3 \le N < 10$** (with $\ge \text{time\_commitment}$ and Ulwick score $\ge 10.0$): Promote to `Stage A Discovery Probe`.
     - **$N \ge 10$** (with $\ge \text{reputation\_commitment}$ or `financial_or_pain_commitment`): Graduate to `Stage B Production Build`.
3. **Update Bayesian JTBD Beliefs from Live Customer Workarounds (`customer-flywheel`)**:
   - Combine prior Importance/Satisfaction ratings with empirical `observed_workaround_rate` and `observed_task_drop_off_rate` via conjugate Bayesian updating. Escalate any job whose posterior Ulwick Opportunity Score crosses $\ge 10.0$.
4. **Stamp Out New Product Lines or Harvest Rule-of-Two Primitives (`factory-floor-ops` + `correct`)**:
   - Open [`../../factory-floor-ops/SKILL.md`](../../factory-floor-ops/SKILL.md).
   - When a graduated opportunity warrants a new vertical product, run the **Product-Line Stamping Press** to scaffold `products/<product-slug>/` (`skills/`, `workflows/`, `evals/`, `features/`).
   - Run the **Rule-of-Two AST Harvester** across all `products/*`: whenever $\ge 2$ products contain structurally duplicate functions, extract the shared primitive into `platform/` behind a frozen data contract and delete the product copies.
   - Run [`../../correct/SKILL.md`](../../correct/SKILL.md) to encode recurring agent mistakes into architecture, types, or fix-naming lints.
5. **Run Post-Ship Zombie Feature Sunset Audit (`escape-the-build-trap`)**:
   - Audit features past their `evaluation_window_days` (default 30 days). Any feature with $< 40\%$ of target adoption and $< 25\%$ of promised customer outcome lift is flagged `SUNSET_AND_DELETE_CODE` and removed from the repository.
