#!/usr/bin/env bash
# Thomas Keller's "Clean As You Go" Station Sanitizer + Purple-Board Allergy Scanner
# Usage: bash skills/head-chef-mode/scripts/clean-station.sh [--allergy] [--full] [--dir <target-dir>]
#
# By default inside a Git worktree, inspects:
#   1. All untracked / scratch droppings in the worktree (*.bak, *.orig, *.tmp, debug_*, test_scratch*)
#   2. Only the files modified or added on the active cutting board (git diff / git status),
#      so a Line Cook is judged on the pans they touched this shift, not legacy code from 2021.
# When --dir <non-git-scratch> or --full is passed, scans all files in TARGET_DIR.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TARGET_DIR="$REPO_ROOT"
ALLERGY_MODE=0
FULL_SCAN=0
EXPLICIT_DIR=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --allergy)
      ALLERGY_MODE=1
      shift
      ;;
    --full)
      FULL_SCAN=1
      shift
      ;;
    --dir)
      TARGET_DIR="$2"
      EXPLICIT_DIR=1
      shift 2
      ;;
    *)
      TARGET_DIR="$1"
      EXPLICIT_DIR=1
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

# Determine the list of files touched on this cutting board (or all files for non-git scratch dirs)
FILES_TO_CHECK=()
if (( FULL_SCAN == 0 )) && git -C "$TARGET_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 && [[ "$(cd "$TARGET_DIR" && pwd)" == "$(git -C "$TARGET_DIR" rev-parse --show-toplevel)" ]]; then
  while IFS= read -r rel_path; do
    [[ -z "$rel_path" ]] && continue
    # Skip markdown docs & this scanner script itself when checking code crumbs
    case "$rel_path" in
      *.md|skills/head-chef-mode/scripts/clean-station.sh) continue ;;
    esac
    if [[ -f "$TARGET_DIR/$rel_path" ]]; then
      FILES_TO_CHECK+=("$TARGET_DIR/$rel_path")
    fi
  done < <(
    {
      git -C "$TARGET_DIR" diff --name-only HEAD 2>/dev/null || true
      git -C "$TARGET_DIR" diff --name-only --cached 2>/dev/null || true
      git -C "$TARGET_DIR" ls-files --others --exclude-standard 2>/dev/null || true
    } | sort -u
  )
else
  while IFS= read -r fpath; do
    [[ -z "$fpath" ]] && continue
    case "$fpath" in
      *.md|*/clean-station.sh) continue ;;
    esac
    FILES_TO_CHECK+=("$fpath")
  done < <(find "$TARGET_DIR" -path "$TARGET_DIR/.git" -prune -o -path "$TARGET_DIR/.audit" -prune -o -type f -print 2>/dev/null || true)
fi

if (( ${#FILES_TO_CHECK[@]} > 0 )); then
  # 2. Check for unresolved merge conflict markers
  CONFLICTS="$(grep -nHI -E '^(<<<<<<< |>>>>>>> )' "${FILES_TO_CHECK[@]}" 2>/dev/null || true)"
  if [[ -n "$CONFLICTS" ]]; then
    echo "DIRTY CUTTING BOARD: Found unresolved merge conflict markers:" >&2
    echo "$CONFLICTS" >&2
    VIOLATIONS=$((VIOLATIONS + 1))
  fi

  # 3. Check for leftover debug print/breakpoint crumbs
  DEBUG_CRUMBS="$(grep -nHI -E '(console\.log\("HERE|pdb\.set_trace\(\)|breakpoint\(\))' "${FILES_TO_CHECK[@]}" 2>/dev/null || true)"
  if [[ -n "$DEBUG_CRUMBS" ]]; then
    echo "DIRTY CUTTING BOARD: Found leftover debug crumbs/breakpoints:" >&2
    echo "$DEBUG_CRUMBS" >&2
    VIOLATIONS=$((VIOLATIONS + 1))
  fi

  # 4. Purple-Board Allergen Scan (hardcoded credentials / private keys)
  ALLERGEN_LEAKS="$(grep -nHI -E '(AKIA[0-9A-Z]{16}|-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----)' "${FILES_TO_CHECK[@]}" 2>/dev/null || true)"
  if [[ -n "$ALLERGEN_LEAKS" ]]; then
    echo "PURPLE-BOARD ALLERGY ALERT: Detected hardcoded credential or private key pattern:" >&2
    echo "$ALLERGEN_LEAKS" >&2
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
fi

if (( VIOLATIONS > 0 )); then
  echo "FAIL: Station failed 'Clean As You Go' inspection ($VIOLATIONS violation group(s)). Wipe the board before calling Pass Inspector!" >&2
  exit 1
fi

if (( ALLERGY_MODE == 1 )); then
  echo "PASS: Station wiped down with sanitizer + Purple-Board Allergy Scan passed (${#FILES_TO_CHECK[@]} active code file(s) inspected)."
else
  echo "PASS: Station wiped down with sanitizer (zero scratch droppings, conflict markers, or debug crumbs across ${#FILES_TO_CHECK[@]} active code file(s))."
fi
