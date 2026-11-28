# the-pass

[![CI](https://github.com/agronomist/the-pass/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/agronomist/the-pass/actions/workflows/ci.yml)

**Nothing leaves the kitchen untasted.** The pass is where a kitchen checks each
dish before it goes out. These five Claude Code skills take an idea to a verified
draft pull request that a person decides whether to merge.

<!-- EXAMPLE: add a real run here (ticket, command, excerpt of the draft PR with
     proof for each criterion). Do not use a mock-up. -->

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

- The hook blocks common accidental pushes outside `factory/*`, PR merges and
  skipped commit checks. It is pattern matching and can be bypassed, so also turn on
  branch protection in GitHub.
- The reviewer has no edit tools but keeps Bash, so it can still write files. Both
  agents are Claude models.

## Does it help?

Not yet measured. [`evals/`](evals/README.md) describes how to compare it with
plain Claude Code. CI checks the layout, hook, install and plugin manifest, not
the quality of the work.

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
