---
name: principle-no-build-trap
description: Apply before approving any feature, product bet, or bespoke prospect request. Never build because 'someone at some point will like it'; require an underserved customer job (Ulwick Opportunity Score >= 10.0), real skin-in-the-game commitment (The Mom Test), and a post-ship zombie-feature deletion threshold.
---

# Principle: No Build Trap

Making software 10x cheaper to build makes **Melissa Perri's Build Trap** (shipping code nobody uses) 10x more dangerous.

- Reject any feature backed only by internal speculation (*"someone at some point will like it"*) or polite compliments (*The Mom Test*).
- Require Tony Ulwick's JTBD Opportunity Score $\text{Importance} + \max(\text{Importance} - \text{Satisfaction}, 0) \ge 10.0$ and verifiable customer skin-in-the-game (time commitment for Stage A probes; reputation or financial/pain commitment for Stage B/C builds).
- Every feature must state a falsifiable customer behavior shift (`baseline -> target` within 30 days). If post-ship adoption is $< 40\%$ of target and outcome lift is $< 25\%$ of promise, sunset the feature and delete the code.
