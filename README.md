# principled-product-factory

A small kitchen for Claude Code: decide what is worth building, build it, and prove it
works before a person merges it.

## Install

```text
/plugin marketplace add agronomist/principled-product-factory
/plugin install kitchen-brigade@principled-product-factory
```

Or clone and run `./install.sh` (global) or `./install.sh /path/to/project`.
The installer wires the safety hook only if the target has no `settings.json` yet, and warns otherwise.

## Five skills

| Skill | Use it to |
| --- | --- |
| `shape` | Decide what to build |
| `ship` | Go from ticket to draft PR |
| `review` | Try to break a change, with proof |
| `verify` | Run the real thing and check numbers |
| `learn` | Stop a mistake from repeating |

Example: `/ship fix issue 202, duplicate webhook notifications on retry`
(plugin installs may show it as `/kitchen-brigade:ship`).

Two agents do the work inside `ship`: `implementer` (Opus) and `reviewer` (Sonnet,
no edit tools). Both are Claude models, and the reviewer keeps Bash.

## Safety

The hook blocks common accidental pushes to protected branches, PR merges and
skipped commit checks. It is pattern matching and can be bypassed, so also turn on
branch protection in GitHub.

## Does it help?

Not yet measured. See [`evals/`](evals/README.md).

The previous 42-skill version is tag `v1-kitchen`.
