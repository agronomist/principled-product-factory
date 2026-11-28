# Does this beat plain Claude Code?

## 1. Reproducible Repo Benchmark (`bash evals/run.sh`)

Run `bash evals/run.sh` to score `v0` (`c92e4ea`), `v1` (`8b0a141`), and `v3` (`the-pass`)
across 6 real tasks from this repo's history (plugin manifest validity, clean external
hook install, quoted/flag-prefixed push blocks, `-n` vs. commit-message false-positive
handling, `gh api` merge block, and `reviewer` read-only `Bash` enforcement) and
measure total skill + agent prompt token footprint:

| Setup | Skills | Agents | Tasks Passed | Skill+Agent Size |
| --- | --- | --- | --- | --- |
| `v0 (initial 33-skill, c92e4ea)` | 33 | 5 | 0 / 6 | ~25,380 tokens |
| `v1 (full 42-skill, 8b0a141)` | 42 | 5 | 5 / 6 | ~35,932 tokens |
| `v3 (the-pass 5-skill, HEAD)` | 5 | 2 | 6 / 6 | ~2,019 tokens |

`v3` cuts skill + agent context overhead by **94.4%** compared to `v1` while passing
all 6 verification tasks.

## 2. Human-Graded 10-Ticket A/B Protocol (Against Plain Claude Code)

1. Pick 10 real, already-solved tickets. Write pass criteria before running anything.
2. Run each from the same starting commit, same model, three ways: plain Claude Code,
   commit `8b0a141`, and this version.
3. Have a person grade the diffs without knowing which setup made them.

| Ticket | Setup | Criteria passed | Would merge? | Human fixes | Tokens | Minutes |
| --- | --- | --- | --- | --- | --- | --- |

Keep this version if quality holds with fewer tokens and less time. Then remove one
skill at a time and rerun; delete any whose removal changes nothing.
Ten tickets is a small sample, so repeat close calls.
