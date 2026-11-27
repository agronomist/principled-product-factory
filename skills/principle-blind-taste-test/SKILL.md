---
name: principle-blind-taste-test
description: Apply whenever inspecting a plated branch at the pass, judging a Cook-Off, calibrating a taster, or auditing a prep log. The taster must run on a different model vendor family than the Line Cook and must never see the Line Cook's private internal monologue.
---

# Principle: Blind Taste Test at the Pass

A line cook tasting their own sauce—or a taster from the same model vendor family—shares the cook's blind spots and palate fatigue.

- Run `pass_inspector`, the `/cook-off` taster, and the `/prep-log` shift auditor on a **different model vendor family** than the Line Cook that cooked the code.
- **Blind to the Cook's Monologue**: Never pass the Line Cook's internal Chain-of-Thought excuses to the Pass Inspector. Hand the Pass Inspector only the original ticket, the Sous Chef's verbatim plating criteria, the pushed branch diff, and the tasting command output.
- **Bounded Refires**: Cap `request_changes -> line_cook_implementer -> pass_inspector` cycles at **at most 2 refires** (`MAX_REVISION_ROUNDS = 2`), and require automated tasters to maintain Cohen's $\kappa \ge 0.80$ agreement with human Head Chef ratings.
