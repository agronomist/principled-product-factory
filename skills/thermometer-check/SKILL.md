---
name: thermometer-check
description: Vet any performance speedup, latency measurement, token cost reduction, or evaluation lift before reporting or acting on it. Checks the physical limiter, whether the cooking actually happened, error rate, repeatability, CUPED/SRM validity, and dining-room relevance. Use for /thermometer-check.
---

# Thermometer Check — Vet Every Number (`/thermometer-check`)

Before you trust, report, or act on any number you measured—a latency speedup, a token cost drop, a throughput gain, or an eval lift—stick a calibrated meat thermometer into the thickest part of the roast.

## The 7-Point Thermometer Checklist

Never report a number until you can answer all seven checks with evidence:

1. **Did the Cooking Actually Happen?**
   - Rule out that a "10x speedup" came from an early-exit error return, a cached no-op, a mocked handler, or an empty dataset. Inspect the real output payload and row count.
2. **What Is the Physical / Queueing Limiter?**
   - Name what physically bounds the number (network RTT, token generation TPS, SQLite WAL fsync, or Little's Law queueing delay under Kingman's formula $\frac{\rho}{1-\rho} \cdot \frac{c_a^2 + c_s^2}{2} \cdot \tau$). If your story contradicts the limiter, your measurement is wrong.
3. **Is the Error / Spoilage Rate Zero?**
   - A fast kitchen that serves raw chicken is not fast. Report the exact error rate and Liskov postcondition pass rate alongside any speed or cost number.
4. **Is It Repeatable Across Runs?**
   - Report sample size $N$, median/mean, and variance or P99 tail—never a single cherry-picked hero run.
5. **Are Baseline and Treatment on Equal Footing (Tuning Parity)?**
   - Same hardware, same concurrency (`WIP_LIMIT = 5`), same warm/cold cache state, and same input distribution.
6. **Statistical & Experiment Integrity (CUPED & SRM)**:
   - For A/B or canary comparisons, verify Pearson's $\chi^2$ Sample Ratio Mismatch ($p \ge 0.01$) and compute CUPED variance-adjusted lift ($\hat{Y}_{\text{CUPED}} = Y - \theta (X - \bar{X})$).
7. **Does It Matter in the Dining Room (Relevance)?**
   - Shaving 2ms off a step that runs once a week while a 4-second LLM call dominates P99 latency is vanity theater. Connect the number to guest outcome or unit food-cost margin.
