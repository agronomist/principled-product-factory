# Playbook: Progressive Canary Rollout, Incident Post-Mortem & Factory OEE (`canary-and-oee.md`)

Use this playbook when promoting a merged change to production (`1% -> 10% -> 50% -> 100%`), responding to a SEV incident or Shewhart $\pm 3\sigma$ excursion, or auditing factory floor bottlenecks.

## Todo List Steps (Copy into Todo Tool First)

1. **Replay Sealed Holdout Digital Twin Before Canary (`factory-floor-ops`)**:
   - Open [`../../factory-floor-ops/SKILL.md`](../../factory-floor-ops/SKILL.md).
   - Replay the candidate build against the **Sealed Holdout Digital Twin** (shadow-traffic scenarios stored outside the implementer agent's repository view so agents cannot overfit to `golden_cases.jsonl`).
   - Require $100\%$ invariant pass rate and unit cost within ceiling before starting the 1% canary.
2. **Drive Progressive Canary Stages (`1% -> 10% -> 50% -> 100%`) (`factory-floor-ops` + `sre-fallback-and-postmortem`)**:
   - At each traffic stage (`1%`, `10%`, `50%`, `100%`), verify three hard gates:
     1. **Shewhart $\pm 3\sigma$ Control Limits**: Observed P99 latency and error rates stay within $[\mu - 3\sigma, \mu + 3\sigma]$.
     2. **Sample Ratio Mismatch (SRM) $\chi^2$ Check**: Observed control vs. canary traffic split satisfies Pearson's $\chi^2$ goodness-of-fit ($p \ge 0.01$).
     3. **Live Contribution Margin Gate**: Realized inference + data + HITL + infra costs satisfy [`../../margin-guard/SKILL.md`](../../margin-guard/SKILL.md).
   - **Auto-Rollback Rule**: On any breach, immediately roll traffic back to `0%`, route live traffic through the 3-tier SRE fallback circuit (`primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`), and trigger Step 3.
3. **Compile Blameless Post-Mortem Regression Fixture (`sre-fallback-and-postmortem`)**:
   - Open [`../../sre-fallback-and-postmortem/SKILL.md`](../../sre-fallback-and-postmortem/SKILL.md).
   - Delta-minimize the failure-inducing payload (stripping volatile timestamps, session tokens, and debug blobs).
   - Compute the canonical SHA-256 error signature (`node_id | exception_type | normalized_message`) and emit a permanent minimized JSON regression fixture into the product's eval suite.
4. **Measure Factory Floor OEE & Goldratt Bottleneck (`factory-floor-ops`)**:
   - Compute Overall Equipment Effectiveness across all stations:
     $$\text{OEE} = \text{Availability} \times \text{Performance} \times \text{FirstPassYield}$$
   - Identify the **Theory of Constraints Bottleneck Station** (highest mean cycle time $W$ or rework cost) and apply Goldratt's Drum-Buffer-Rope prescription under Little's Law (`WIP_LIMIT = 5`).
