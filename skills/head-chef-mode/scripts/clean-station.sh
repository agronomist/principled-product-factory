#!/usr/bin/env bash
# Thomas Keller's "Clean As You Go" Station Sanitizer + Purple-Board Allergy Scanner
# Usage: bash skills/head-chef-mode/scripts/clean-station.sh [--allergy] [--dir <target-dir>]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TARGET_DIR="$REPO_ROOT"
ALLERGY_MODE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --allergy)
      ALLERGY_MODE=1
      shift
      ;;
    --dir)
      TARGET_DIR="$2"
      shift 2
      ;;
    *)
      TARGET_DIR="$1"
      shift
      ;;
  esac
done

echo "================================================================"
echo " STATION SANITIZER ('Clean As You Go' & Allergy Check)"
echo "================================================================"

VIOLATIONS=0

# 1. Check for scratch droppings (*.bak, *.orig, *.tmp, debug_*, test_scratch*)
DROPPINGS="$(find "$TARGET_DIR" \
  -path "$TARGET_DIR/.git" -prune -o \
  -path "$TARGET_DIR/.audit" -prune -o \
  -type f \( -name "*.bak" -o -name "*.orig" -o -name "*.tmp" -o -name "debug_*" -o -name "test_scratch*" \) \
  -print 2>/dev/null || true)"

if [[ -n "$DROPPINGS" ]]; then
  echo "DIRTY CUTTING BOARD: Found leftover scratch droppings on the station:" >&2
  echo "$DROPPINGS" >&2
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 2. Check for unresolved merge conflict markers
CONFLICTS="$(grep -rnI --exclude-dir=.git --exclude-dir=.audit --exclude="clean-station.sh" -E '^(<<<<<<< |>>>>>>> )' "$TARGET_DIR" 2>/dev/null || true)"
if [[ -n "$CONFLICTS" ]]; then
  echo "DIRTY CUTTING BOARD: Found unresolved merge conflict markers:" >&2
  echo "$CONFLICTS" >&2
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 3. Check for leftover debug print/breakpoint crumbs
DEBUG_CRUMBS="$(grep -rnI --exclude-dir=.git --exclude-dir=.audit --exclude="clean-station.sh" --exclude="README.md" --exclude="SKILL.md" --exclude="chef-rituals.md" -E '(console\.log\("HERE|pdb\.set_trace\(\)|breakpoint\(\))' "$TARGET_DIR" 2>/dev/null || true)"
if [[ -n "$DEBUG_CRUMBS" ]]; then
  echo "DIRTY CUTTING BOARD: Found leftover debug crumbs/breakpoints:" >&2
  echo "$DEBUG_CRUMBS" >&2
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 4. Purple-Board Allergen Scan (always checks high-risk secret patterns; mandatory on --allergy tickets)
ALLERGEN_LEAKS="$(grep -rnI --exclude-dir=.git --exclude-dir=.audit --exclude="clean-station.sh" --exclude="SKILL.md" --exclude="chef-rituals.md" -E '(AKIA[0-9A-Z]{16}|-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----)' "$TARGET_DIR" 2>/dev/null || true)"
if [[ -n "$ALLERGEN_LEAKS" ]]; then
  echo "PURPLE-BOARD ALLERGY ALERT: Detected hardcoded credential or private key pattern:" >&2
  echo "$ALLERGEN_LEAKS" >&2
  VIOLATIONS=$((VIOLATIONS + 1))
fi

if (( VIOLATIONS > 0 )); then
  echo "FAIL: Station failed 'Clean As You Go' inspection ($VIOLATIONS violation group(s)). Wipe the board before calling Pass Inspector!" >&2
  exit 1
fi

if (( ALLERGY_MODE == 1 )); then
  echo "PASS: Station wiped down with sanitizer + Purple-Board Allergy Scan passed."
else
  echo "PASS: Station wiped down with sanitizer (zero scratch droppings, conflict markers, or debug crumbs)."
fi
