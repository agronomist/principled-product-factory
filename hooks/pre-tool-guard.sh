#!/usr/bin/env bash
set -euo pipefail

# Claude Code PreToolUse Guard Hook
# Blocks:
#   1. Direct or bare git push to protected branches (main, master, production, release),
#      including git -C <dir> push, quoted branch names ("main"), or refspecs (HEAD:main).
#   2. Autonomous PR merges via `gh pr merge` or `gh api .../pulls/.../merge`.
#   3. Verification bypass flags (`--no-verify` or `git commit -n`) outside quoted message strings.
# Note: Real enforcement relies on GitHub branch protection rules; this hook prevents accidental agent tool calls.

RAW_INPUT="${1:-}"
if [[ -z "$RAW_INPUT" ]] && [[ ! -t 0 ]]; then
  RAW_INPUT="$(cat)"
fi

# Extract command string from Claude Code PreToolUse JSON payload if JSON was provided
COMMAND_STR="$RAW_INPUT"
if command -v jq >/dev/null 2>&1 && printf '%s' "$RAW_INPUT" | grep -q '^[[:space:]]*{'; then
  EXTRACTED="$(printf '%s' "$RAW_INPUT" | jq -r '.tool_input.command // .command // empty' 2>/dev/null || true)"
  if [[ -n "$EXTRACTED" ]]; then
    COMMAND_STR="$EXTRACTED"
  fi
elif printf '%s' "$RAW_INPUT" | grep -q '"command"'; then
  # Fallback JSON extraction if jq is unavailable
  EXTRACTED="$(printf '%s' "$RAW_INPUT" | sed -nE 's/.*"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p' | sed 's/\\"/"/g; s/\\\\/\\/g')"
  if [[ -n "$EXTRACTED" ]]; then
    COMMAND_STR="$EXTRACTED"
  fi
fi

[[ -z "$COMMAND_STR" ]] && exit 0

# Strip quoted arguments to -m / --message / --title / --body / --notes so commit messages
# that merely mention "--no-verify" or "git push origin main" are never falsely blocked.
SANITIZED_CMD="$(printf '%s\n' "$COMMAND_STR" | sed -E \
  -e 's/(-[a-zA-Z]*m|--message|--title|--body|--notes)(=|[[:space:]]+)("([^"\\]|\\.)*"|'\''[^'\'']*'\'')/\1\2"__MSG__"/g')"

# Helper: iterate over individual shell subcommands split by ; | & or newline
while IFS= read -r subcmd; do
  subcmd_trimmed="$(printf '%s' "$subcmd" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
  [[ -z "$subcmd_trimmed" ]] && continue

  # 1. Inspect any git push command (handling global git flags like `git -C . push`, `git --git-dir=... push`)
  if printf '%s\n' "$subcmd_trimmed" | grep -Eq '(^|[[:space:]])git([[:space:]]+(-[Ccp]|--git-dir|--work-tree|--namespace)([[:space:]]+[^[:space:]]+|=[^[:space:]]+)|[[:space:]]+--[^[:space:]]+)*[[:space:]]+push([[:space:]]|$)'; then
    # Normalize quotes around arguments so `git push -f origin "main"` or `'main'` is caught
    push_unquoted="$(printf '%s' "$subcmd_trimmed" | tr -d '"'\''')"

    # 1a. Block explicit push to main, master, production, or release (including HEAD:main or refs/heads/main)
    if printf '%s\n' "$push_unquoted" | grep -Eq '([[:space:]:/])(main|master|production|release)([[:space:]]|$)'; then
      echo "BLOCKED by safety hook: Direct pushes to main/master/production/release are forbidden. FIX: Push to an isolated 'factory/<ticket-slug>' branch (and enable GitHub branch protection as the server-side lock)." >&2
      exit 2
    fi

    # 1b. Block bare `git push` or `git push [-u|--force] [origin]` that omits an explicit `factory/*` branch target
    if ! printf '%s\n' "$push_unquoted" | grep -Eq '([[:space:]:/])factory/[A-Za-z0-9._-]+'; then
      echo "BLOCKED by safety hook: Bare or non-factory git push detected. FIX: Specify an explicit 'factory/<ticket-slug>' branch (e.g., 'git push -u origin factory/<ticket-slug>')." >&2
      exit 2
    fi
  fi

  # 2. Block PR merges via `gh pr merge` OR `gh api .../pulls/.../merge` / GraphQL mergePullRequest
  if printf '%s\n' "$subcmd_trimmed" | grep -Eq '(^|[[:space:]])gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$)'; then
    echo "BLOCKED by safety hook: Merging pull requests is not in the agent tool surface. FIX: Leave the draft PR for a person to merge." >&2
    exit 2
  fi
  if printf '%s\n' "$subcmd_trimmed" | grep -Eq '(^|[[:space:]])gh[[:space:]]+api[[:space:]].*(/pulls/[0-9]+/merge|mergePullRequest)'; then
    echo "BLOCKED by safety hook: Merging pull requests via 'gh api' is forbidden. FIX: Leave the draft PR for a person to merge." >&2
    exit 2
  fi

  # 3. Block --no-verify flag (outside stripped commit messages) and `git commit -n`
  if printf '%s\n' "$subcmd_trimmed" | grep -Eq '(^|[[:space:]])--no-verify([[:space:]]|$)'; then
    echo "BLOCKED by safety hook: Bypassing verification hooks with --no-verify is forbidden. FIX: Run the full verification check and fix the underlying failure." >&2
    exit 2
  fi
  if printf '%s\n' "$subcmd_trimmed" | grep -Eq '(^|[[:space:]])git([[:space:]]+[^[:space:]]+)*[[:space:]]+commit([[:space:]]|$)'; then
    # Strip quoted strings completely before checking for short `-n` flag on `git commit`
    commit_no_quotes="$(printf '%s' "$subcmd_trimmed" | sed -E 's/"([^"\\]|\\.)*"//g; s/'\''[^'\'']*'\''//g')"
    if printf '%s\n' "$commit_no_quotes" | grep -Eq '(^|[[:space:]])-[a-zA-Z]*n[a-zA-Z]*([[:space:]]|$)'; then
      echo "BLOCKED by safety hook: Bypassing commit hooks with 'git commit -n' is forbidden. FIX: Run 'git commit' without '-n' and fix any pre-commit failure." >&2
      exit 2
    fi
  fi
done < <(printf '%s\n' "$SANITIZED_CMD" | tr ';\n|&' '\n\n\n\n')

exit 0
