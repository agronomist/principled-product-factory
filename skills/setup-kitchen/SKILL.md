---
name: setup-kitchen
description: Configure which AI models run each Kitchen Brigade station (Host Triage, Forager, Sous Chef, Line Cook, Pass Inspector, Cook-Off Tasters), pick a token/reasoning budget (Bistro Fast, Michelin Standard, or Tasting Menu Maximum), and offer to generate a live tasting harness (/taste-the-dish). Use for /setup-kitchen.
---

# Setup the Kitchen (`/setup-kitchen`)

Configures per-station model routing, reasoning budgets, and project verification harnesses for the Kitchen Brigade skill stack.

## 1. Pick a Kitchen Budget Tier

Ask the Head Chef to choose one of three reasoning and token budgets:

| Budget Tier | When to Choose It | Default Station Routing |
| :--- | :--- | :--- |
| **1. Bistro Fast (Economical)** | Routine tickets, small diffs, or keeping token spend tight. | `host-triage`: Haiku / Flash \| `sous-chef-planner`: Sonnet \| `line-cook-implementer`: Sonnet \| `pass-inspector`: GPT / Gemini Fast (cross-vendor) |
| **2. Michelin Standard (Recommended)** | Daily production engineering, multi-file features, and enterprise deal desks. | `host-triage`: Sonnet \| `sous-chef-planner`: Opus \| `line-cook-implementer`: Opus \| `pass-inspector`: Cross-vendor reasoning model (or Sonnet if single-key) |
| **3. Tasting Menu Maximum (High Rigor)** | One-way door architecture, security-critical refactors, and 3-contender `/cook-off` tournaments. | `sous-chef-planner` & `line-cook-implementer`: Opus xhigh \| `cook-off` & `health-inspector`: 3-vendor panel (Anthropic + OpenAI + Gemini) |

## 2. Write the Station Model Rule (`.claude/kitchen-models.md`)

Write the user's chosen station mapping to `.claude/kitchen-models.md` (or `~/.cursor/rules/kitchen-models.mdc` in Cursor) so `/head-chef-mode`, `/kitchen-brigade`, `/cook-off`, and `/health-inspector` read it automatically on every new shift:

```markdown
# Kitchen Brigade Model Assignments
# budget: michelin-standard
- expediter: inherit-parent
- host-triage: claude-sonnet-4-5
- forager-researcher: claude-sonnet-4-5
- sous-chef-planner: claude-opus-4-5
- line-cook-implementer: claude-opus-4-5
- pass-inspector: cross-vendor-reviewer
- cook-off-contenders: claude-opus-4-5, cross-vendor-reviewer
```

**Cross-Vendor Rule (`principle-blind-taste-test`)**: Remind the user that whenever multiple model providers are connected, `pass-inspector` and the `/cook-off` blind taster should run on a different model vendor than `line-cook-implementer`.

## 3. Check for a Live Tasting Harness (`/taste-the-dish`) & HACCP Spec (`/haccp-statechart`)

After saving the model rule, inspect the target repository:
1. If no `verify-*` or project-local tasting harness exists, offer once: *"Would you like me to run `/taste-the-dish` now so line cooks have a scripted way to launch, doctor-check, and taste your app?"*
2. If the repository contains stateful concurrency, retries, or payment/margin gates with no formal verification check, mention `/haccp-statechart` once.
