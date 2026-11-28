# the-pass

[![CI](https://github.com/agronomist/the-pass/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/agronomist/the-pass/actions/workflows/ci.yml)

**Nothing leaves the kitchen untasted.** The pass is where a kitchen checks each
dish before it goes out. These five Claude Code skills take an idea to a verified
draft pull request that a person decides whether to merge.

**Real run from this repo ([PR #1](https://github.com/agronomist/the-pass/pull/1) $\to$ `commit 9152a13`):**
```text
Task:    Fix 5 plugin validation errors and 6 hook bypasses found by adversarial review
Branch:  factory/simplify-5-skills
Verify:  bash tests/check.sh -> PASS: all checks (16/16 hook & clean-install assertions)
Proof:   - plugin.json: removed ../ parent traversal (0 claude plugin validate errors)
         - hooks/pre-tool-guard.sh: blocked bare git push, git push -f origin "main",
           git -C . push origin main, git commit -n, and gh api .../pulls/1/merge (exit 2)
         - allowed commit messages mentioning "--no-verify" (exit 0)
```

## Quick start

You need [Claude Code](https://code.claude.com/docs), Git, and a way for Claude to
open pull requests, such as the [GitHub CLI](https://cli.github.com) signed in.

1. In Claude Code, install the plugin:

   ```text
   /plugin marketplace add agronomist/the-pass
   /plugin install the-pass@the-pass
   ```

2. Open your repository and give it one task (use one of your own):

   ```text
   /the-pass:ship fix issue 202, duplicate webhooks on retry
   ```

3. Expect a `factory/*` branch and a draft PR describing what changed, proof for
   each acceptance criterion, risks, and decisions for you. If the task is unclear
   or the review keeps failing, it is instructed to stop and tell you instead.

Prefer files over a plugin? Clone this repo and run `./install.sh` (global) or
`./install.sh /path/to/project`. Commands then have no prefix, such as `/ship`. The
installer wires the safety hook only if the target has no `settings.json` yet, and
warns otherwise.

## Five skills

| Command | Use it to | Example task |
| --- | --- | --- |
| `/the-pass:shape` | Decide what to build | should we add a CSV export? |
| `/the-pass:ship` | Go from ticket to draft PR | fix issue 202 |
| `/the-pass:review` | Try to break a change, with proof | this branch against main |
| `/the-pass:verify` | Run the real thing and check numbers | the claimed 2x speedup |
| `/the-pass:learn` | Stop a mistake from repeating | we broke the same migration twice |

```text
idea -> shape -> ship (implement -> verify -> review) -> draft PR -> you merge
                                          mistakes -> learn
```

`ship` hands work to an `implementer` agent (Opus) and a separate `reviewer` agent
(Sonnet). The reviewer is given the task, criteria, branch and test output, not the
implementer's reasoning.

## When not to use it

- Typos and other tiny edits: just ask Claude directly.
- Quick questions or throwaway exploration with nothing to ship.
- Changes that must be pushed straight to a protected branch.

## Safety

- The hook blocks common accidental pushes outside `factory/*`, PR merges, skipped
  commit checks, and mutating git/file commands when called by the `reviewer` agent.
  It is pattern matching and can be bypassed, so also turn on branch protection in
  GitHub.
- Both agents are Claude models by default; if `codex` or `gemini` is on `PATH`,
  `reviewer` can pipe the diff to it for a cross-vendor second opinion.

## Does it help?

Run `bash evals/run.sh` to reproduce the 6-task regression and token-footprint
benchmark across this repository's versions (~94% smaller prompt footprint than the
42-skill v1 stack while passing 6/6 structural & hook tasks). See
[`evals/`](evals/README.md) for the 10-ticket human-graded A/B protocol against plain
Claude Code.

## Upgrading

From an earlier name (`kitchen-brigade` or `principled-product-factory`), remove the
old marketplace, which also removes its plugins, then follow the quick start:

```text
/plugin marketplace remove principled-product-factory
```

Version 1 skills, including sales call harvesting, are in `archive/` and not loaded.
The full runnable version is commit `8b0a141`.

## Contributing

Run `bash tests/check.sh` before committing.
