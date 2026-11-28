---
name: shape
description: Decide what to build before building it. Use for a new feature idea, a vague or oversized ticket, "should we build X?", or a request that prescribes a solution without naming the problem.
---

# Shape

Output a short brief. Do not write production code here.

## 1. Find the problem
- Who has it, and what are they doing today instead?
- What measurable behavior should change, from what baseline to what target, by when?
- What evidence exists? Time spent, a workaround, money or a repeated complaint counts.
  Compliments and "someone might want this" do not. With no evidence, say so and
  recommend not building, or the cheapest way to find out.

## 2. Offer three options
1. The smallest lever: a default, an error message, a deleted step.
2. A focused version with no new infrastructure.
3. What was asked for.

Recommend the smallest one that can move the metric.

## 3. Check four risks
| Risk | Question |
| --- | --- |
| Value | Will people use it? |
| Usability | Can they reach first value in about three steps? |
| Feasibility | Does the real code support it? Read the files. |
| Viability | Do cost, legal, privacy and margins work? Would plain code beat a model call? |

For the riskiest unknown, propose one small test (a one-file prototype on fixture
data counts) and run it before planning the full build.

## 4. Finish
State: problem, metric, chosen option, open risks, and what happens right after the
user gets the result (include that step only if it is cheap).
