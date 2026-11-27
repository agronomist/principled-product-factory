#!/usr/bin/env bash
set -euo pipefail

# Claude Code PreToolUse Guard Hook (principle-plate-at-the-pass)
# Blocks direct git pushes to main/master/production and blocks non-draft PR creation during unattended runs.

COMMAND_STR="${1:-}"
if [ -z "$COMMAND_STR" ] && [ ! -t 0 ]; then
  COMMAND_STR="$(cat)"
fi

# 1. Block direct git push to protected branches (main, master, production, release)
if printf '%s\n' "$COMMAND_STR" | grep -Eq 'git[[:space:]]+push[[:space:]]+[^;|&"]*(origin[[:space:]]+)?(main|master|production|release)([[:space:]"'\'']|$)'; then
  echo "BLOCKED by Kitchen Brigade Hook (principle-plate-at-the-pass): Direct pushes to main/master/production are forbidden. FIX: Push to an isolated 'factory/<ticket-slug>' branch and open a Draft PR." >&2
  exit 2
fi

# 2. Block gh pr merge from agent tool calls (merging stays a human Head Chef decision)
if printf '%s\n' "$COMMAND_STR" | grep -Eq 'gh[[:space:]]+pr[[:space:]]+merge'; then
  echo "BLOCKED by Kitchen Brigade Hook (principle-plate-at-the-pass): Merging pull requests is not in the agent tool surface. FIX: Leave the Draft PR at the pass for the Head Chef to merge." >&2
  exit 2
fi

# 3. Block --no-verify flag so line cooks cannot bypass pre-commit or health-check hooks
if printf '%s\n' "$COMMAND_STR" | grep -Eq '(^|[[:space:]"'\''])--no-verify([[:space:]"'\'']|$)'; then
  echo "BLOCKED by Kitchen Brigade Hook (principle-taste-before-serving): Bypassing verification hooks with --no-verify is forbidden. FIX: Run the full verification check and fix the underlying failure." >&2
  exit 2
fi

exit 0
