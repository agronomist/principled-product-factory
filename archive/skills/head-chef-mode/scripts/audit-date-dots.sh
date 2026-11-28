#!/usr/bin/env bash
# Green Painter's Tape & FIFO Date-Dot Walk-In Scanner (/fifo-walk-in)
# Usage: bash skills/head-chef-mode/scripts/audit-date-dots.sh [target-dir]
# Scans for "FIFO-DATE-DOT: expires=YYYY-MM-DD" tags and fails if any container is past its expiration date.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TARGET_DIR="${1:-$REPO_ROOT}"
TODAY_UTC="${KITCHEN_TODAY_UTC:-$(date -u +%Y-%m-%d)}"

echo "================================================================"
echo " WALK-IN FIFO DATE-DOT AUDIT (Today UTC: $TODAY_UTC)"
echo "================================================================"

SPOILED_COUNT=0
ACTIVE_DOTS=0

# Find lines with an actual FIFO-DATE-DOT assignment (expires=20YY-MM-DD)
while IFS= read -r match; do
  [[ -z "$match" ]] && continue
  # Skip documentation examples that use placeholder YYYY-MM-DD or this script itself
  if [[ "$match" == *"audit-date-dots.sh"* ]] || [[ "$match" == *"run-live-tasting.sh"* ]] || [[ "$match" == *"fifo-walk-in/SKILL.md"* ]] || [[ "$match" == *"amuse-bouche/SKILL.md"* ]] || [[ "$match" == *"chef-rituals.md"* ]]; then
    continue
  fi

  EXP_DATE="$(printf '%s\n' "$match" | grep -oE 'expires=[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -n1 | cut -d= -f2 || true)"
  [[ -z "$EXP_DATE" ]] && continue

  ACTIVE_DOTS=$((ACTIVE_DOTS + 1))
  if [[ "$EXP_DATE" < "$TODAY_UTC" ]]; then
    echo "SPOILED CONTAINER (Expired $EXP_DATE < $TODAY_UTC): $match" >&2
    SPOILED_COUNT=$((SPOILED_COUNT + 1))
  else
    echo "FRESH CONTAINER (Use by $EXP_DATE): $match"
  fi
done < <(grep -rnI --exclude-dir=.git --exclude-dir=.audit "FIFO-DATE-DOT:.*expires=[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" "$TARGET_DIR" 2>/dev/null || true)

if (( SPOILED_COUNT > 0 )); then
  echo "FAIL: Found $SPOILED_COUNT spoiled FIFO-DATE-DOT container(s) in the walk-in! 86 or graduate them immediately." >&2
  exit 1
fi

echo "PASS: Walk-in FIFO check clean ($ACTIVE_DOTS active date-dot container(s), 0 spoiled)."
