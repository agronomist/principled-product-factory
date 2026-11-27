---
name: sre-fallback-and-postmortem
description: 3-tier SRE graceful degradation circuit breaker (primary_frontier_model -> secondary_distilled_model -> tertiary_cached_deterministic), Shewhart +/- 3-sigma statistical process control, SHA-256 duplicate error-signature Saga rollbacks, and automated BlamelessPostMortem regression fixture generation.
---

# SRE Fallback Circuits, Saga Rollbacks & Blameless Post-Mortems (`/sre-fallback-and-postmortem`)

Ensures 99.99% reliability and self-immunizing incident recovery across every workflow in the software factory.

## 1. 3-Tier Graceful Degradation Circuit Breaker

Never allow a single foundation model vendor outage or latency spike to take down a product workflow. Wire every inference dependency through a 3-tier fallback chain:
$$\texttt{primary\_frontier\_model} \longrightarrow \texttt{secondary\_distilled\_model} \longrightarrow \texttt{tertiary\_cached\_deterministic}$$
- *Soccer Metaphor*: When your #10 star playmaker gets double-marked (`primary_frontier_model` 503 or latency spike), pivot through your #8 box-to-box midfielder (`secondary_distilled_model`) or play a safe back-pass to your sweeper keeper (`tertiary_cached_deterministic`) to keep a clean sheet.
- *Seinfeld Metaphor*: **Jerry's Comedy Club Backup Routine**: When the experimental new bit bombs, pivot smoothly into proven material so the set never dies on stage.
- **Circuit Breaker States (`CLOSED -> OPEN -> HALF_OPEN -> CLOSED`)**: After `failure_threshold` (default 2) consecutive failures on a tier, trip its circuit to `OPEN` and fast-fail directly to the next tier until `recovery_timeout_seconds` elapses.

## 2. Duplicate SHA-256 Error-Signature Halt & Saga Compensating Rollback

Never burn tokens retrying an identical deterministic failure:
1. Normalize every node exception (stripping volatile `0x...` memory addresses and whitespace) and compute:
   $$\text{sig} = \text{SHA256}(\texttt{node\_id} \parallel \texttt{exception\_type} \parallel \texttt{normalized\_message})$$
2. **Immediate Halt on First Duplicate**: The moment the same $\text{sig}$ appears a second time within a node's retry loop (*George Costanza trying to parallel park the same impossible angle three times in a row while traffic piles up*), **halt retries immediately**.
3. **Reverse-Topological Saga Rollback**: Execute the idempotent `compensating_action` of every completed upstream node in **exact reverse topological order** and emit a structured Human-In-The-Loop (`HITLEscalationTicket`) payload.

## 3. Shewhart $\pm 3\sigma$ Control Charts & Automated `BlamelessPostMortem` Fixtures

Every production SEV incident or Shewhart $\pm 3\sigma$ control-limit breach ($|z| = \frac{|x - \mu|}{\sigma} > 3.0$) must permanently immunize the repository:
1. **Delta-Minimize the Payload**: Strip volatile noise keys (`debug_trace`, `timestamp_ns`, `ephemeral_session_token`, `raw_html_dump`), truncate oversized strings, and shrink lists to minimal failure-inducing elements.
2. **Compile into a Permanent JSON Regression Fixture**: Record `fixture_id`, `incident_id`, `error_signature_sha256`, `shewhart_z_score`, `minimized_input_payload`, and `expected_invariant_assertion` (`required_fallback_tier`), and commit the fixture directly to the Tier A/B evaluation suite.
