# Kitchen Brigade Living Menu Map (`features/`)

Maintained by [`skills/verify-kitchen-cookbook/SKILL.md`](../skills/verify-kitchen-cookbook/SKILL.md) and [`skills/taste-the-dish/SKILL.md`](../skills/taste-the-dish/SKILL.md).

## Indexed Diner-Facing Features

- [cookbook-validation.md](cookbook-validation.md) — Structural verification of all modular `skills/*/SKILL.md` files, playbooks, and `.claude/agents/*.md` station subagents.
- [service-door-bouncer.md](service-door-bouncer.md) — Claude Code `PreToolUse` shell safety hook blocking direct pushes to `main`/`master` and blocking autonomous `gh pr merge`.
- [prep-log-trail.md](prep-log-trail.md) — Append-only `decisions.tsv` prep logger with spreadsheet formula-injection sanitization and evidence pointer resolution.
- [chef-rituals.md](chef-rituals.md) — Pre-shift walk-in lineup (`pre-shift-check.sh`), FIFO Date-Dot spoilage scanner (`audit-date-dots.sh`), and "Clean As You Go" + Purple-Board Allergy station sanitizer (`clean-station.sh`).
