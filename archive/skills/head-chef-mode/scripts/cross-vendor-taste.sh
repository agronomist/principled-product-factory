#!/usr/bin/env bash
# Prepares a reasoning-stripped blind tasting packet for pass-inspector
# or an external cross-vendor model CLI (principle-blind-taste-test).
# Also records a working-tree SHA-256 integrity fingerprint so the Expediter can verify
# that pass-inspector's Bash tool did not mutate any files during inspection.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$WORK_REPO"

BASE_REF="${1:-HEAD~1}"
ACCEPTANCE_CRITERIA="${2:-Verify all acceptance criteria, check for regressions, and ensure durable test evidence exists.}"
OUT_FILE="${3:-.audit/evidence/blind-tasting-packet.md}"

mkdir -p "$(dirname "$OUT_FILE")"

# Enforce "Clean As You Go" rule before calling Pass Inspector
bash "$SCRIPT_DIR/clean-station.sh" --dir "$WORK_REPO"

# Resolve diff target gracefully even on initial or clean trees
if git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
  DIFF_STAT="$(git diff --stat "$BASE_REF")"
  DIFF_BODY="$(git diff "$BASE_REF")"
else
  DIFF_STAT="$(git status --short)"
  DIFF_BODY="$(git diff)"
fi

# Compute pre-inspection working-tree fingerprint so any unauthorized file mutation by a reviewer with Bash is detected
TREE_FINGERPRINT="$({ git status --porcelain 2>/dev/null; git diff HEAD 2>/dev/null; } | sha256sum | awk '{print $1}')"

cat <<EOF > "$OUT_FILE"
# Blind Tasting Packet (Reasoning-Stripped Review Bundle)

> **Instruction for the Pass Inspector / Cross-Vendor Taster**:
> You are receiving ONLY the verbatim acceptance criteria and the raw code diff.
> The Line Cook's internal reasoning, excuses, and self-grades have been stripped.
> Grade every criterion strictly as \`PASS\`, \`FAIL\`, or \`MISSING_EVIDENCE\`.
> **Read-Only Invariant**: Do not mutate any tracked or untracked files. Pre-inspection working-tree SHA-256: \`$TREE_FINGERPRINT\`.

## 1. Acceptance Criteria
$ACCEPTANCE_CRITERIA

## 2. Changed Files Summary
\`\`\`text
${DIFF_STAT:-No committed diff against $BASE_REF (working tree clean or identical).}
\`\`\`

## 3. Raw Unified Diff
\`\`\`diff
${DIFF_BODY:-No diff lines found against $BASE_REF.}
\`\`\`
EOF

echo "Blind tasting packet plated at: $OUT_FILE (Tree SHA-256: $TREE_FINGERPRINT)"
echo "Feed this file directly to the pass-inspector subagent or a cross-vendor CLI reviewer (e.g., codex / gemini)."
