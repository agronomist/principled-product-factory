# Feature: Service-Door Bouncer Hook (`hooks/pre-tool-guard.sh`)

Enforces `principle-plate-at-the-pass` at the OS shell boundary via Claude Code's `PreToolUse` hook in `.claude/settings.json`.

## Sub-features

- Allows git pushes to inert `factory/<ticket-slug>` branches (`exit 0`).
- Blocks direct `git push` to protected branches (`main`, `master`, `production`, `release`) with `exit 2` and a `FIX:` message.
- Blocks `gh pr merge` from agent tool calls with `exit 2` so merging remains a human Head Chef decision.

## How to get to it (user POV)

Triggered automatically by Claude Code before any `Bash` tool execution via `.claude/settings.json`, or invoked directly via `bash hooks/pre-tool-guard.sh "<command>"`.

## Driving it with verify-kitchen-cookbook

```bash
bash hooks/pre-tool-guard.sh "git push origin factory/ticket-101"
! bash hooks/pre-tool-guard.sh "git push origin main"
! bash hooks/pre-tool-guard.sh "gh pr merge 101"
```

Observable end state: `factory/*` push exits `0`; `main` push and `gh pr merge` exit `2` with `BLOCKED by Kitchen Brigade Hook` and `FIX:` instructions on stderr.

## Gotchas

- Accepts the command string either as `$1` or via `stdin` so both CLI arguments and JSON pipe hooks are guarded.
