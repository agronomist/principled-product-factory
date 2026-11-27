---
name: principle-prove-it-works
description: Apply after completing a task, before declaring done. Verify against the real running artifact (Launch -> Doctor -> Drive -> Evidence -> Cleanup), prove checks can fail on a broken mutation, and validate experiments with CUPED variance reduction and SRM chi-square checks.
---

# Principle: Prove It Works

Verify every output by driving the real artifact directly: launch the app, run the `Doctor` health check, `Drive` the user journey, capture `Evidence` that survives `Cleanup`, and read the actual output. Proxies (*"it compiles"*, cached output, or self-reports) do not count.

- **Mutation Sensitivity**: A check you have never seen fail proves nothing. Confirm every new invariant check fails loudly when run against a broken mutation of the code it guards.
- **Tier C Experiment Integrity**: Before trusting any A/B or canary readout, run Pearson's $\chi^2$ Sample Ratio Mismatch test ($p \ge 0.01$ required) and apply CUPED pre-experiment covariate adjustment ($\hat{Y}_{\text{CUPED}} = Y - \theta (X - \bar{X})$) to reduce variance.
