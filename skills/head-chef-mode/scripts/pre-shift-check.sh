#!/usr/bin/env bash
# The 4:30 PM Pre-Shift Lineup & Walk-In Inventory Check (/pre-shift-lineup)
# Inspects base stockpot health, active factory/* cutting boards against Little's Law,
# walk-in FIFO date dots, and station cleanliness before dinner service opens.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

WIP_LIMIT="${KITCHEN_WIP_LIMIT:-5}"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")"
DIRTY_FILES="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
ACTIVE_WORKTREES="$(git worktree list --porcelain 2>/dev/null | grep -c '^branch refs/heads/factory/' || true)"
FACTORY_BRANCHES="$(git branch --list 'factory/*' 2>/dev/null | wc -l | tr -d ' ')"

echo "================================================================"
echo " 4:30 PM PRE-SHIFT LINEUP & WALK-IN CHECK"
echo "================================================================"
echo "-> [1/4] Base Stockpot Status:"
echo "   Current Branch : $CURRENT_BRANCH"
if (( DIRTY_FILES == 0 )); then
  echo "   Working Tree   : CLEAN (0 uncommitted files)"
else
  echo "   Working Tree   : $DIRTY_FILES uncommitted file(s) from prior prep"
fi

echo "-> [2/4] Cutting Board Inventory (Little's Law WIP Guard):"
echo "   Active factory/* worktrees : $ACTIVE_WORKTREES / $WIP_LIMIT"
echo "   Local factory/* branches   : $FACTORY_BRANCHES"
if (( ACTIVE_WORKTREES >= WIP_LIMIT )); then
  echo "   WARNING: Kitchen is at max WIP ($ACTIVE_WORKTREES/$WIP_LIMIT). Plate or prune a board before firing new tickets." >&2
fi

echo "-> [3/4] Walk-In Cooler FIFO Date-Dot Scan:"
bash skills/head-chef-mode/scripts/audit-date-dots.sh "$REPO_ROOT"

echo "-> [4/4] Station Surface Check ('Clean As You Go'):"
bash skills/head-chef-mode/scripts/clean-station.sh --dir "$REPO_ROOT"

echo "================================================================"
echo " LINEUP COMPLETE — The kitchen is prepped and ready for service!"
echo "================================================================"
