#!/usr/bin/env bash
# End-of-shift closing duty check for Claude Code sessions.
# Works inside the cookbook repo AND inside any external project where the plugin is installed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COOKBOOK_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
WORK_REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$WORK_REPO"

echo "================================================================"
echo " CLOSING DUTY: End-of-Shift Kitchen Inspection ($WORK_REPO)"
echo "================================================================"

# 1. Validate all skills, station subagents, and plugin manifests
echo "-> [1/4] Running validate-skills.sh on cookbook ($COOKBOOK_ROOT)..."
bash "$SCRIPT_DIR/validate-skills.sh"

# 2. Check feature map integrity if the working project has a features/README.md map
echo "-> [2/4] Checking features/README.md index integrity..."
if [[ -f "$WORK_REPO/features/README.md" ]]; then
  MISSING_FEATURES=0
  while IFS= read -r rel_link; do
    [[ -z "$rel_link" ]] && continue
    if [[ ! -f "$WORK_REPO/features/$rel_link" ]]; then
      echo "FAIL: features/README.md references missing feature doc: features/$rel_link" >&2
      MISSING_FEATURES=$((MISSING_FEATURES + 1))
    fi
  done < <(grep -oE '\(\./[a-zA-Z0-9_-]+\.md\)' "$WORK_REPO/features/README.md" | tr -d '()' | sed 's|^\./||')

  if (( MISSING_FEATURES > 0 )); then
    exit 1
  fi
  echo "PASS: All feature documents indexed in features/README.md exist."
else
  echo "INFO: No features/README.md in $WORK_REPO yet (run /taste-the-dish to generate a project tasting map)."
fi

# 3. Audit decisions.tsv if present
echo "-> [3/4] Checking Prep Log (decisions.tsv) if present..."
if [[ -f "$WORK_REPO/decisions.tsv" ]]; then
  ROW_COUNT="$(wc -l < "$WORK_REPO/decisions.tsv" | tr -d ' ')"
  echo "PASS: decisions.tsv present ($ROW_COUNT rows)."
else
  echo "INFO: No root decisions.tsv logged in this shift (clean tree)."
fi

# 4. Run station surface & FIFO date-dot checks on the active repo
echo "-> [4/4] Verifying station surface & walk-in FIFO date dots..."
bash "$SCRIPT_DIR/clean-station.sh" --dir "$WORK_REPO"
bash "$SCRIPT_DIR/audit-date-dots.sh" "$WORK_REPO"

echo "================================================================"
echo " KITCHEN CLOSED CLEANLY — End-of-Shift Prompts for Claude Code:"
echo "   * Did a feature change? Run: /update-the-cookbook"
echo "   * Did an agent repeat a mistake? Run: /sharpen-the-knives"
echo "   * Stopping mid-ticket? Run: /shift-handoff"
echo "================================================================"
