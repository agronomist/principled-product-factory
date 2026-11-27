---
name: principle-sequence-verifiable-units
description: Apply to multi-step work, hillclimbing loops, migrations, and dynamic workflow synthesis. Order tasks riskiest-unknown-first (EVOI / Cost), break work into atomic brackets (baseline -> 1 change -> check -> keep or hard-revert), and verify each unit before starting the next.
---

# Principle: Sequence Work into Verifiable Units

Order work as small, atomic brackets that each end in a verifiable state, and never advance until the current bracket is green.

- **Riskiest-Unknown-First**: When synthesizing a workflow, place verification harness setup first, then order domain steps by $\frac{\text{EVOI} \times (1 + P_{\text{fail}})}{\text{Cost}}$ so cheap, high-information falsification probes run before expensive buildout steps.
- **Keep-or-Revert Brackets**: Each unit is `known-good baseline -> 1 atomic change -> run live verification check`. If the check is `VERIFIED` and improves the target metric, commit the bracket and log to `decisions.tsv`. If it regresses or is `INCONCLUSIVE`, hard-revert immediately.
