# principled-product-factory

Five Claude Code skills that take an idea to a verified draft pull request: decide
what is worth building, build it, prove it works, and let a person merge it.

```text
idea -> shape -> ship (implement -> verify -> review) -> draft PR -> you merge
                                          mistakes -> learn
```

## Install

In Claude Code:

```text
/plugin marketplace add agronomist/principled-product-factory
/plugin install kitchen-brigade@principled-product-factory
```

Or clone the repo and run `./install.sh` (global) or `./install.sh /path/to/project`.
The installer wires the safety hook only if the target has no `settings.json` yet,
and warns otherwise.

## Five skills

| Skill | Use it to | Try |
| --- | --- | --- |
| `shape` | Decide what to build | `/shape should we add a CSV export?` |
| `ship` | Go from ticket to draft PR | `/ship fix issue 202, duplicate webhooks on retry` |
| `review` | Try to break a change, with proof | `/review this branch against main` |
| `verify` | Run the real thing and check numbers | `/verify the claimed 2x speedup` |
| `learn` | Stop a mistake from repeating | `/learn we broke the same migration twice` |

Plugin installs may show these as `/kitchen-brigade:ship` and so on.

## Two agents

`ship` hands work to an `implementer` (Opus) and an independent `reviewer` (Sonnet,
no edit tools). The reviewer sees the task, criteria, diff and test output, not the
implementer's reasoning. Both are Claude models, and the reviewer keeps Bash.

## Safety

The hook blocks common accidental pushes outside `factory/*`, PR merges and skipped
commit checks. It is pattern matching and can be bypassed, so also turn on branch
protection in GitHub.

## Layout

| Path | Contents |
| --- | --- |
| `skills/`, `agents/`, `hooks/` | What gets installed |
| `tests/check.sh` | Layout, hook and install checks, also run in CI |
| `evals/` | How to test whether this beats plain Claude Code |
| `archive/` | The previous 42-skill version, not loaded |

## Status

Version 2.0. Whether it improves results has not been measured yet; see
[`evals/`](evals/README.md). If you used version 1, its skills (including sales call
harvesting) are in `archive/`, and the full runnable version is commit `8b0a141`.
