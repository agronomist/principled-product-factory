#!/usr/bin/env bash
# Enforces Little's Law (WIP <= 5) and principle-clean-cutting-boards
# by spawning, listing, or bussing (cleaning up) isolated git worktrees on factory/<ticket-slug>.
#
# Usage:
#   bash skills/head-chef-mode/scripts/spawn-worktree.sh <ticket-slug> [base-ref]
#   bash skills/head-chef-mode/scripts/spawn-worktree.sh --list
#   bash skills/head-chef-mode/scripts/spawn-worktree.sh --bus <ticket-slug>

set -euo pipefail

WIP_LIMIT="${KITCHEN_WIP_LIMIT:-5}"
REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_ROOT="${KITCHEN_WORKTREE_DIR:-$(dirname "$REPO_ROOT")/.kitchen-cutting-boards}"

ACTION="spawn"
if [[ "${1:-}" == "--list" ]]; then
  ACTION="list"
elif [[ "${1:-}" == "--bus" || "${1:-}" == "--prune" ]]; then
  ACTION="bus"
  shift
fi

ACTIVE_FACTORY_WORKTREES="$(git worktree list --porcelain | grep -c '^branch refs/heads/factory/' || true)"

if [[ "$ACTION" == "list" ]]; then
  echo "=================================================================="
  echo " ACTIVE CUTTING BOARDS (WIP: $ACTIVE_FACTORY_WORKTREES / $WIP_LIMIT)"
  echo "=================================================================="
  git worktree list
  exit 0
fi

TICKET_SLUG="${1:-}"
BASE_REF="${2:-HEAD}"

if [[ -z "$TICKET_SLUG" ]]; then
  echo "Usage:" >&2
  echo "  Spawn board : bash skills/head-chef-mode/scripts/spawn-worktree.sh <ticket-slug> [base-ref]" >&2
  echo "  List boards : bash skills/head-chef-mode/scripts/spawn-worktree.sh --list" >&2
  echo "  Bus board   : bash skills/head-chef-mode/scripts/spawn-worktree.sh --bus <ticket-slug>" >&2
  exit 1
fi

# Strip accidental factory/ prefix if passed by caller
TICKET_SLUG="${TICKET_SLUG#factory/}"

if [[ ! "$TICKET_SLUG" =~ ^[A-Za-z0-9._-]+$ ]]; then
  echo "ERROR: Invalid ticket slug '$TICKET_SLUG'. Use only alphanumeric characters, dots, underscores, or hyphens." >&2
  exit 1
fi

TARGET_DIR="$WORKTREE_ROOT/$TICKET_SLUG"
BRANCH_NAME="factory/$TICKET_SLUG"

if [[ "$ACTION" == "bus" ]]; then
  if [[ -d "$TARGET_DIR" ]]; then
    git worktree remove --force "$TARGET_DIR"
  fi
  git worktree prune
  NEW_COUNT="$(git worktree list --porcelain | grep -c '^branch refs/heads/factory/' || true)"
  echo "=================================================================="
  echo " BUSSED CUTTING BOARD TO DISHPIT: $TICKET_SLUG"
  echo "   Active WIP : $NEW_COUNT / $WIP_LIMIT"
  echo "=================================================================="
  exit 0
fi

if (( ACTIVE_FACTORY_WORKTREES >= WIP_LIMIT )); then
  echo "==================================================================" >&2
  echo " KITCHEN BACKED UP (Little's Law WIP Guard Triggered)" >&2
  echo " Active factory/* cutting boards: $ACTIVE_FACTORY_WORKTREES (Limit: $WIP_LIMIT)" >&2
  echo " Bus a finished worktree to the dishpit before firing a new ticket:" >&2
  echo "   bash skills/head-chef-mode/scripts/spawn-worktree.sh --list" >&2
  echo "   bash skills/head-chef-mode/scripts/spawn-worktree.sh --bus <ticket-slug>" >&2
  echo "==================================================================" >&2
  exit 2
fi

mkdir -p "$WORKTREE_ROOT"

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
