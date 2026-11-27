# Copy-Paste Recipe Prompts for Claude Code (`recipe-prompts.md`)

Copy and paste these prompts directly into Claude Code, Cursor, or Antigravity to drive the Kitchen Brigade:

## 1. Turn an Issue or Bug Report into a Blind-Inspected Draft PR
```text
/head-chef-mode Run the ticket-to-pass playbook on issue #202 ("Duplicate webhook notifications on retry"). Route through host-triage, sous-chef-planner, line-cook-implementer (on an isolated git worktree branch factory/issue-202), and pass-inspector. Stop at a Draft PR and log every station to decisions.tsv.
```

## 2. Triage a New Feature Idea Against the Build Trap & Food-Cost Margin
```text
/head-chef-mode Run the test-kitchen-tasting playbook on this proposal: "<describe feature>". Score it with /no-empty-calories (Ulwick JTBD Opportunity Score + Mom Test commitment tier) and /food-cost-guard (4-axis AI filter + unit contribution margin). Tell me plainly if we should cook it, run a Stage A pop-up, or 86 it.
```

## 3. Run a 3-Cook Bakeoff (`/cook-off`) on a One-Way Door Architecture Decision
```text
/cook-off We need to design the state persistence and retry boundary for <module>. Spawn 3 contenders on isolated git worktrees, judge them blind against a 4-criterion rubric (Liskov contracts, food-cost efficiency, failure recovery, smallest API surface), pick the cleanest base, and graft the best edge-case guards from the runners-up.
```

## 4. Hillclimb a Slow Endpoint or Evaluation Score (`/recipe-reduction-loop`)
```text
/head-chef-mode Run the recipe-reduction-loop playbook to improve <metric> from <baseline> to <target>. Capture the baseline with /taste-the-dish and /thermometer-check first, run one atomic hypothesis bracket at a time (commit if VERIFIED, hard-revert if regressed or INCONCLUSIVE), enforce /principle-check-the-oven after 2 failed tweaks, and log every bracket to decisions.tsv.
```

## 5. Build an Enterprise Challenger Sales Pitch & Push Back on an Off-Menu Demand
```text
/sommelier-table-pitch Prepare an enterprise deal desk playbook for <Prospect Name> ($60k ACV). Write the 6-step Commercial Teaching choreography quantifying their annual Cost of Inaction (>= 3x ACV), tailor briefs for the CFO, VP Eng, Champion, and Operator, write a Constructive Tension pushback script for their custom feature/discount request, and include a JOLT playbook to close within 14 days.
```

## 6. Adversarial Pre-Merge Health Inspection (`/health-inspector` + `/cross-contamination`)
```text
/health-inspector Stress-test the current branch diff against main. Only report violations you prove with a real failing command or repro script. Then run /cross-contamination to identify the single safety fact downstream callers depend on and prove it by running real code.
```

## 7. Morning Catch-Up After an Overnight Shift (`/shift-handoff`)
```text
/shift-handoff Catch me up on everything that changed in the kitchen since my last message. Read decisions.tsv and active factory/* branches, summarize what passed tasting and what was dumped, and list every Draft PR waiting at the pass with everything I need to decide right here.
```

## 8. Harvest Dining-Room Feedback & Sharpen the Knives
```text
/head-chef-mode Run the dining-room-harvest playbook. Cluster recent user_correction_diff overrides, check which off-menu requests crossed N=3 (Stage A) or N=10 (Stage B), scan products/* for Rule-of-Two mother-sauce extraction into platform/, and run /sharpen-the-knives to turn our last 2 bug classes into fix-naming lints.
```
