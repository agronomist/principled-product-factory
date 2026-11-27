# Feature: Contribution Margin Gate & 3-Tier SRE Fallback

Guards unit economics pre-flight and ensures 99.99% workflow availability across foundation model outages via the 3-tier SRE degradation chain.

## Sub-features

- Pre-flight Contribution Margin Gate (`unit_revenue - (inference_cost + data_api_cost + hitl_prob * human_review_cost + infra_cost) >= min_margin`).
- Automatic model distillation downgrade (`distill_and_proceed` on `secondary_distilled_model`) when frontier inference misses `min_margin` but distilled inference passes.
- 3-Tier SRE Fallback Circuit (`primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic`).

## How to get to it (user POV)

Pass transaction unit economics and optional fault-injection flags (`simulate_primary_failure`, `simulate_secondary_failure`) through `products/demo-decision-engine/harness/drive_cli.py`.

## Driving it with SubprocessCLIHarness

```bash
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-04-exact-margin-boundary-pass
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-05-margin-downgrade-to-distilled
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-10-sre-double-fallback-to-tertiary
```

Observable end state:
- `case-04-exact-margin-boundary-pass`: `"margin_passed": true`, `"selected_tier": "primary_frontier_model"`.
- `case-05-margin-downgrade-to-distilled`: `"triage_action": "distill_and_proceed"`, `"selected_tier": "secondary_distilled_model"`.
- `case-10-sre-double-fallback-to-tertiary`: `"selected_tier": "tertiary_cached_deterministic"`, `"total_cost_usd"` reduced via tertiary multiplier.

## Gotchas

- When both primary and secondary tiers fail consecutively ($\ge \text{failure\_threshold}$), the circuit breaker trips to `CircuitState.OPEN` and fast-fails subsequent calls until `recovery_timeout_seconds` elapses.
