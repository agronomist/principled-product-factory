# Playbook: First Tables Rollout, Spoiled-Batch Post-Mortem & Service Speed (`first-tables-and-service-speed.md`)

Use this playbook when sending a new dish out to the first tables (`1% -> 10% -> 50% -> 100%`), responding to a SEV kitchen incident or Shewhart $\pm 3\sigma$ excursion, or auditing line bottlenecks.

## Todo List Steps (Copy into Todo Tool First)

1. **Run the Blind Mystery-Diner Holdout Before Serving the Dining Room (`central-commissary`)**:
   - Open [`../../central-commissary/SKILL.md`](../../central-commissary/SKILL.md).
   - Replay the candidate build against the **Sealed Mystery-Diner Holdout Twin** (shadow-traffic orders stored outside the Line Cook's repository view so cooks cannot overfit to `golden_cases.jsonl`).
   - Require $100\%$ invariant pass rate and food cost within ceiling before serving the first 1% table.
2. **Serve First Tables Progressively (`1% -> 10% -> 50% -> 100%`) (`central-commissary` + `pantry-backup-and-incident-card`)**:
   - At each seating stage (`1%`, `10%`, `50%`, `100%`), verify three hard gates:
     1. **Shewhart $\pm 3\sigma$ Control Limits**: Observed P99 ticket time and error rates stay within $[\mu - 3\sigma, \mu + 3\sigma]$.
     2. **Sample Ratio Mismatch (SRM) $\chi^2$ Check**: Observed control vs. new-dish table split satisfies Pearson's $\chi^2$ goodness-of-fit ($p \ge 0.01$).
     3. **Live Food-Cost Margin Gate**: Realized ingredient + data + human-review + infra costs satisfy [`../../food-cost-guard/SKILL.md`](../../food-cost-guard/SKILL.md).
   - **Auto-86 Rollback Rule**: On any breach, immediately pull the dish (`0%`), route live orders through the 3-tier pantry backup chain (`primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`), and trigger Step 3.
3. **File a Blameless Incident Card Fixture (`pantry-backup-and-incident-card`)**:
   - Open [`../../pantry-backup-and-incident-card/SKILL.md`](../../pantry-backup-and-incident-card/SKILL.md).
   - Delta-minimize the failure-inducing order payload (stripping volatile timestamps, tokens, and debug noise).
   - Compute the canonical SHA-256 burn signature (`station_id | exception_type | normalized_message`) and commit a permanent minimized JSON regression fixture into the tasting suite.
4. **Measure Kitchen Service OEE & Goldratt Bottleneck Station (`central-commissary`)**:
   - Compute Overall Equipment Effectiveness across all stations:
     $$\text{OEE} = \text{Availability} \times \text{Performance} \times \text{FirstPassYield}$$
   - Identify the **Theory of Constraints Bottleneck Station** (highest mean ticket time $W$ or refire waste) and apply Goldratt's Drum-Buffer-Rope prescription under Little's Law (`WIP_LIMIT = 5`).
