# Feature: Prep-Log TSV Decision Trail (`log-decision.sh`)

Appends single-line, tab-separated decision checkpoints (`ts | phase | decision | why | evidence | result`) to `decisions.tsv` during multi-step or overnight runs (`/prep-log`).

## Sub-features

- Automatic TSV header creation (`ts\tphase\tdecision\twhy\tevidence\tresult`) on first write.
- Tab/newline stripping so every row remains strictly single-line.
- Spreadsheet formula-injection sanitization (prefixing cells starting with `=`, `+`, `-`, or `@` with `'`).

## How to get to it (user POV)

Run `bash skills/head-chef-mode/scripts/log-decision.sh <logfile> <phase> <decision> <why> <evidence> <result>`.

## Driving it with verify-kitchen-cookbook

```bash
bash skills/head-chef-mode/scripts/log-decision.sh \
  /tmp/test-decisions.tsv "taste" "=SUM(A1:A5) dangerous" "+faster" "CLAUDE.md:1" "VERIFIED"
```

Observable end state: `/tmp/test-decisions.tsv` contains the header row plus 1 data row where `=SUM(A1:A5) dangerous` is escaped as `'=SUM(A1:A5) dangerous` and `+faster` is escaped as `'+faster`.

## Gotchas

- `decisions.tsv` is append-only; never edit or delete historical rows—append a `SUPERSEDE:` or `REVERTED:` row instead.
