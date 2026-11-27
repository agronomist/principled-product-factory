---
name: stage-tryout
description: The Stagiaire Trail Shift — audition a new model vendor, third-party dependency, MCP tool, or skill rewrite by replaying one solved historical ticket on an isolated git worktree cutting board and scoring it head-to-head against the incumbent kitchen baseline before hiring it onto the main line. Use for /stage-tryout, "audition this model/library", or evaluating tooling changes.
---

# The Kitchen *Stage* / Trail Shift (`/stage-tryout`)

> *"You never hire a new Sous Chef or switch your flour purveyor based on a glossy brochure. You bring them in for a one-night Stage (trail shift): hand them a 50-pound sack of onions, ask them to cook one staff-meal omelette during the Friday rush, and watch how clean they keep their board before giving them a station."*

## When to Run a *Stage* Tryout

Run `/stage-tryout` whenever someone proposes:
- Switching a station subagent (`sous-chef-planner`, `line-cook-implementer`, `pass-inspector`) to a new LLM model or reasoning budget.
- Replacing a core library, test runner, ORM, or third-party API purveyor.
- Rewriting a core skill or playbook in `skills/*/SKILL.md`.

Never roll out a new cook or purveyor globally across the kitchen without a 1-ticket *Stage* tryout first.

---

## The 4-Step *Stage* Audition Protocol

### Step 1: Pick the Reference Dish (A Solved Historical Ticket)
Select **one real, previously merged commit or closed ticket** from `git log` (ideally one that had clear acceptance criteria and a non-trivial verification check, or a bug fix with a known regression test).
- Record the reference commit SHA (`REF_SHA`), its parent (`BASE_SHA = REF_SHA~1`), and the incumbent stats (lines changed, test runtime, token/food cost).

### Step 2: Set Up the Stagiaire's Isolated Cutting Board
Spawn a throwaway worktree starting at `BASE_SHA` using [`spawn-worktree.sh`](../head-chef-mode/scripts/spawn-worktree.sh):

```bash
bash skills/head-chef-mode/scripts/spawn-worktree.sh stage-tryout-<candidate-slug> <BASE_SHA>
```

### Step 3: Hand the Stagiaire Only the Original Ticket Brief
Give the candidate model, library, or skill **only** the original ticket prompt and `BASE_SHA` checkout (strip the historical solution diff so the *stagiaire* cannot peek at the answer).
- Require the candidate to run the live tasting harness ([`/taste-the-dish`](../taste-the-dish/SKILL.md)) and [`clean-station.sh`](../head-chef-mode/scripts/clean-station.sh).

### Step 4: Blind Head-to-Head Scorecard (Incumbent vs. Stagiaire)
Have a cross-vendor [`pass-inspector`](../../agents/pass-inspector.md) score the Stagiaire's worktree diff against the Incumbent (`REF_SHA`) across five dimensions:

| Dimension | Incumbent (`REF_SHA`) | Stagiaire Candidate | Winner |
| :--- | :--- | :--- | :--- |
| **1. First-Pass Tasting Verdict** | Did it pass all verbatim criteria on try #1? | Pass / Fail | |
| **2. Station Cleanliness (`clean-station.sh`)** | Zero scratch droppings or debug crumbs? | Clean / Dirty | |
| **3. Recipe Simplicity (Diff Size)** | Total lines added + deleted (`git diff --shortstat`) | Lines $\Delta$ | |
| **4. Service Speed (Wall-Clock Time)** | Seconds to verified commit | Seconds | |
| **5. Food Cost ([`/food-cost-guard`](../food-cost-guard/SKILL.md))** | Total tokens + API spend per ticket | $\$$ / ticket | |

### Hiring Rule
- **Hire onto the Line**: Only if the Stagiaire matches or beats the Incumbent on **First-Pass Tasting Verdict** AND improves either **Food Cost ($\ge 20\%$ cheaper)**, **Service Speed ($\ge 25\%$ faster)**, or **Recipe Simplicity (smaller, cleaner diff)**.
- **Thank Them & Send Them Home**: If the Stagiaire leaves a dirty board, breaks an invariant, or burns $3\times$ the token food cost for the same omelette, prune the worktree (`git worktree remove`) and log the rejection to `decisions.tsv` via [`/prep-log`](../prep-log/SKILL.md).
