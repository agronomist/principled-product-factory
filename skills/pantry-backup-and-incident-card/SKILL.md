---
name: pantry-backup-and-incident-card
description: 3-tier pantry fallback circuit breaker (primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic), Shewhart +/- 3-sigma ticket-time control, SHA-256 duplicate burn-signature Saga pan-dumping, and automated Blameless Incident Card regression fixture generation.
---

# Pantry Backup Substitutions, Saga Cleanup & Incident Cards (`/pantry-backup-and-incident-card`)

Guarantees uninterrupted service during supplier outages and turns every kitchen accident into a permanent regression check.

## 1. 3-Tier Pantry Backup Substitution Chain

Never shut down the dining room just because one specialty purveyor misses a delivery. Wire every model/external dependency through a 3-tier pantry backup chain:
$$\texttt{primary\_frontier\_model} \longrightarrow \texttt{secondary\_distilled\_model} \longrightarrow \texttt{tertiary\_cached\_deterministic}$$
- *Soccer Metaphor*: When your #10 star playmaker gets double-marked (`primary_frontier_model` 503 outage or latency spike), cycle the ball through your #8 box-to-box midfielder (`secondary_distilled_model`) or play a safe back-pass to your sweeper keeper (`tertiary_cached_deterministic`) to keep a clean sheet.
- *Seinfeld Metaphor*: **Jerry's Comedy Club Backup Routine**: When the experimental new bit gets silence, pivot smoothly into proven material so the show never stalls.
- **Burner Breaker States (`CLOSED -> OPEN -> HALF_OPEN -> CLOSED`)**: After `failure_threshold` (default 2) consecutive failures on a tier, trip its breaker to `OPEN` and route orders straight to the backup tier until `recovery_timeout_seconds` elapses.

## 2. Duplicate SHA-256 Burn-Signature Halt & Saga Pan Cleanup

Never burn three pans in a row on the exact same broken step:
1. Normalize every station exception (stripping volatile `0x...` memory addresses and whitespace) and compute:
   $$\text{sig} = \text{SHA256}(\texttt{station\_id} \parallel \texttt{exception\_type} \parallel \texttt{normalized\_message})$$
2. **Turn Off the Burner on the First Duplicate**: The moment the same $\text{sig}$ appears a second time within a station's retry loop (*George Costanza trying to parallel park the same impossible angle three times in a row while traffic honks down the block*), **halt retries immediately**.
3. **Reverse-Order Saga Dishpit Cleanup**: Run the idempotent `compensating_action` of every completed upstream station in **exact reverse topological order** and ring the Head Chef bell (`HITLEscalationTicket`).

## 3. Shewhart $\pm 3\sigma$ Control Charts & Automated Incident Cards

Every SEV kitchen fire or Shewhart $\pm 3\sigma$ ticket-time excursion ($|z| = \frac{|x - \mu|}{\sigma} > 3.0$) must permanently immunize the recipe book:
1. **Trim the Fat (Delta-Minimization)**: Strip volatile noise keys (`debug_trace`, `timestamp_ns`, `ephemeral_session_token`, `raw_html_dump`), trim oversized strings, and shrink lists to minimal failure-reproducing ingredients.
2. **Laminate the Incident Card (JSON Regression Fixture)**: Record `fixture_id`, `incident_id`, `error_signature_sha256`, `shewhart_z_score`, `minimized_input_payload`, and `expected_invariant_assertion` (`required_fallback_tier`), and commit it directly into the Tier A/B tasting suite.
