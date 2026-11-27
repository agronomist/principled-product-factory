---
name: principle-taste-before-serving
description: Apply after completing a task, before ringing the service bell. Taste the real dish directly (Fire Up -> Station Check -> Plate -> Proof -> Dishpit), prove HACCP checks fail on a spoiled mutation, and validate first-tables rollouts with CUPED variance reduction and SRM chi-square checks.
---

# Principle: Taste Before Serving (Prove It Works)

Never send a plate to the dining room without tasting the real dish directly: fire up the application, run the `Station Check`, `Plate` the user journey, capture `Proof` that survives `Dishpit` cleanup, and inspect the actual output. Proxies (*"the recipe compiled"*, cached output, or line-cook self-reports) do not count.

- **Spoiled-Ingredient Sensitivity**: A health check you have never seen fail proves nothing. Confirm every new invariant check fails loudly when run against a spoiled mutation of the code it guards.
- **First-Tables Statistical Integrity**: Before trusting any A/B or first-tables readout, run Pearson's $\chi^2$ Sample Ratio Mismatch test ($p \ge 0.01$ required) and apply CUPED pre-experiment covariate adjustment ($\hat{Y}_{\text{CUPED}} = Y - \theta (X - \bar{X})$) to reduce variance.
