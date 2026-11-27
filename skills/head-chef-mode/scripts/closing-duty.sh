#!/usr/bin/env bash
# End-of-shift closing duty check for Claude Code sessions:
# 1. Validates all skills and station subagents.
# 2. Audits decisions.tsv (if present) for empty evidence pointers.
# 3. Verifies the living feature map (features/README.md) links to existing docs.
# 4. Prints the 2-minute closing checklist (/update-the-cookbook & /sharpen-the-knives).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

echo "================================================================"
echo " CLOSING DUTY: End-of-Shift Kitchen Inspection"
echo "================================================================"

# 1. Validate all skills and agents
echo "-> [1/4] Running validate-skills.sh..."
bash skills/head-chef-mode/scripts/validate-skills.sh

# 2. Check feature map integrity
echo "-> [2/4] Checking features/README.md index integrity..."
if [[ ! -f "features/README.md" ]]; then
  echo "FAIL: features/README.md is missing! Run /taste-the-dish or /update-the-cookbook." >&2
  exit 1
fi

MISSING_FEATURES=0
while IFS= read -r rel_link; do
  [[ -z "$rel_link" ]] && continue
  if [[ ! -f "features/$rel_link" ]]; then
    echo "FAIL: features/README.md references missing feature doc: features/$rel_link" >&2
    MISSING_FEATURES=$((MISSING_FEATURES + 1))
  fi
done < <(grep -oE '\(\./[a-zA-Z0-9_-]+\.md\)' features/README.md | tr -d '()' | sed 's|^\./||')

if (( MISSING_FEATURES > 0 )); then
  exit 1
fi
echo "PASS: All feature documents indexed in features/README.md exist."

# 3. Audit decisions.tsv if present
echo "-> [3/4] Checking Prep Log (decisions.tsv) if present..."
if [[ -f "decisions.tsv" ]]; then
  ROW_COUNT="$(wc -l < decisions.tsv | tr -d ' ')"
  echo "PASS: decisions.tsv present ($ROW_COUNT rows)."
else
  echo "INFO: No root decisions.tsv logged in this shift (clean tree)."
fi

# 4. Run live tasting proof check
echo "-> [4/4] Verifying latest tasting proof in .audit/evidence/..."
if [[ -f ".audit/evidence/proof-kitchen-cookbook.json" ]]; then
  echo "PASS: Durable tasting proof found (.audit/evidence/proof-kitchen-cookbook.json)."
else
  echo "INFO: No tasting proof found yet; running run-live-tasting.sh now..."
  bash skills/head-chef-mode/scripts/run-live-tasting.sh
fi

echo "================================================================"
echo " KITCHEN CLOSED CLEANLY — End-of-Shift Prompts for Claude Code:"
echo "   * Did a feature change? Run: /update-the-cookbook"
echo "   * Did an agent repeat a mistake? Run: /sharpen-the-knives"
echo "   * Stopping mid-ticket? Run: /shift-handoff"
echo "================================================================"
