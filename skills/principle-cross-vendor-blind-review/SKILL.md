---
name: principle-cross-vendor-blind-review
description: Apply whenever reviewing a code branch, scoring an Arena bakeoff, calibrating a Tier B evaluator, or auditing a decision trail. The reviewer must run on a different model vendor family than the implementer and must never see the implementer's private Chain-of-Thought reasoning.
---

# Principle: Cross-Vendor Blind Review

Self-review on the same model vendor shares the generator's blind spots and self-preference bias.

- Run `reviewer`, the `/arena` cross-judge, and the `/show-me-your-work` trail auditor on a **different model vendor family** than the agent that wrote the code (e.g., Anthropic implementer reviewed by OpenAI or Gemini).
- **Blind to Reasoning**: Never pass the implementer's internal Chain-of-Thought rationale to the reviewer. Hand the reviewer only the original work item, the analyst's verbatim acceptance criteria, the pushed branch diff, and the verification command output.
- **Bounded Revisions**: Cap `request_changes -> implementer -> reviewer` cycles at **at most 2 rounds** (`MAX_REVISION_ROUNDS = 2`), and require Tier B automated judges to maintain Cohen's $\kappa \ge 0.80$ agreement with human reference labels.
