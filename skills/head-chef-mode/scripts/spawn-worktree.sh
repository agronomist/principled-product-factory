#!/usr/bin/env bash
# Enforces Little's Law (WIP <= 5) and principle-clean-cutting-boards
# by spawning an isolated git worktree on a factory/<ticket-slug> branch.

set -euo pipefail

WIP_LIMIT="${KITCHEN_WIP_LIMIT:-5}"
TICKET_SLUG="${1:-}"
BASE_REF="${2:-HEAD}"

if [[ -z "$TICKET_SLUG" ]]; then
  echo "Usage: bash skills/head-chef-mode/scripts/spawn-worktree.sh <ticket-slug> [base-ref]" >&2
  echo "Example: bash skills/head-chef-mode/scripts/spawn-worktree.sh TKT-104-auth-boundary main" >&2
  exit 1
fi

# Strip accidental factory/ prefix if passed by caller
TICKET_SLUG="${TICKET_SLUG#factory/}"

if [[ ! "$TICKET_SLUG" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "ERROR: Invalid ticket slug '$TICKET_SLUG'. Use only alphanumeric characters, dots, underscores, or hyphens." >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
ACTIVE_FACTORY_WORKTREES="$(git worktree list --porcelain | grep -c '^branch refs/heads/factory/' || true)"

if (( ACTIVE_FACTORY_WORKTREES >= WIP_LIMIT )); then
  echo "==================================================================" >&2
  echo " KITCHEN BACKED UP (Little's Law WIP Guard Triggered)" >&2
  echo " Active factory/* cutting boards: $ACTIVE_FACTORY_WORKTREES (Limit: $WIP_LIMIT)" >&2
  echo " Plate, inspect, or prune an existing worktree before firing a new ticket:" >&2
  echo "   git worktree list" >&2
  echo "   git worktree remove <path>" >&2
  echo "==================================================================" >&2
  exit 2
fi

WORKTREE_ROOT="${KITCHEN_WORKTREE_DIR:-$(dirname "$REPO_ROOT")/.kitchen-cutting-boards}"
mkdir -p "$WORKTREE_ROOT"

TARGET_DIR="$WORKTREE_ROOT/$TICKET_SLUG"
BRANCH_NAME="factory/$TICKET_SLUG"

if [[ -d "$TARGET_DIR" ]]; then
  echo "Cutting board already exists at: $TARGET_DIR (branch: $BRANCH_NAME)"
  exit 0
fi

git worktree add -b "$BRANCH_NAME" "$TARGET_DIR" "$BASE_REF"

echo "=================================================================="
echo " NEW CUTTING BOARD READY"
echo "   Station Worktree : $TARGET_DIR"
echo "   Branch           : $BRANCH_NAME"
echo "   Active WIP       : $((ACTIVE_FACTORY_WORKTREES + 1)) / $WIP_LIMIT"
echo "=================================================================="
