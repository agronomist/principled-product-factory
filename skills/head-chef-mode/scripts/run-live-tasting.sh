#!/usr/bin/env bash
# Fire Up -> Station Check -> Plate -> Proof -> Dishpit
# End-to-end live tasting harness for principled-product-factory (verify-kitchen-cookbook).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

SCRATCH_DIR="/tmp/kitchen-harness-scratch-$$"
PROOF_DIR="$REPO_ROOT/.audit/evidence"
PROOF_FILE="$PROOF_DIR/proof-kitchen-cookbook.json"

cleanup() {
  rm -rf "$SCRATCH_DIR"
}
trap cleanup EXIT

echo "================================================================"
echo " [1/5] FIRE UP: Preparing scratch station ($SCRATCH_DIR)"
echo "================================================================"
mkdir -p "$SCRATCH_DIR" "$PROOF_DIR"

echo "================================================================"
echo " [2/5] STATION CHECK: Verifying scripts, hooks, and symlinks"
echo "================================================================"
for required in \
  "skills/head-chef-mode/scripts/validate-skills.sh" \
  "skills/head-chef-mode/scripts/log-decision.sh" \
  "hooks/pre-tool-guard.sh" \
  ".claude/skills" \
  ".claude/agents" \
  "features/README.md"
do
  if [[ ! -e "$REPO_ROOT/$required" ]]; then
    echo "FAIL: Missing required station asset: $required" >&2
    exit 1
  fi
done
echo "PASS: Station check verified all required levers and symlinks."

echo "================================================================"
echo " [3/5] PLATE: Driving every feature in features/README.md"
echo "================================================================"

# Feature 1: Cookbook Validation + Negative Mutation Check
echo "-> Feature 1: Cookbook & Station Validation (features/cookbook-validation.md)"
VALIDATE_OUT="$(bash skills/head-chef-mode/scripts/validate-skills.sh)"
echo "$VALIDATE_OUT"

# Negative mutation check in scratch copy to prove the validator catches broken frontmatter
mkdir -p "$SCRATCH_DIR/bad-repo/skills/broken-dish" "$SCRATCH_DIR/bad-repo/agents" "$SCRATCH_DIR/bad-repo/skills/head-chef-mode/scripts"
cp skills/head-chef-mode/scripts/validate-skills.sh "$SCRATCH_DIR/bad-repo/skills/head-chef-mode/scripts/"
cat << 'EOF' > "$SCRATCH_DIR/bad-repo/skills/broken-dish/SKILL.md"
---
name: broken-dish
---
Missing description field should fail validation.
EOF

if bash "$SCRATCH_DIR/bad-repo/skills/head-chef-mode/scripts/validate-skills.sh" > /dev/null 2>&1; then
  echo "FAIL: Negative mutation test failed — validate-skills.sh passed on broken frontmatter!" >&2
  exit 1
fi

# Negative mutation check 1b: Prove validate-skills.sh rejects a pass-inspector holding Edit/Write tongs
cat << 'EOF' > "$SCRATCH_DIR/bad-repo/skills/broken-dish/SKILL.md"
---
name: broken-dish
description: Valid temporary skill so execution reaches agent validation.
---
Valid skill body.
EOF
cat << 'EOF' > "$SCRATCH_DIR/bad-repo/agents/pass-inspector.md"
---
name: pass-inspector
description: Corrupted pass inspector that illegally holds Edit and Write tools.
tools: Read, Grep, Glob, Bash, Edit, Write
---
Body.
EOF
if bash "$SCRATCH_DIR/bad-repo/skills/head-chef-mode/scripts/validate-skills.sh" > /dev/null 2>&1; then
  echo "FAIL: Negative mutation test failed — validate-skills.sh allowed pass-inspector to hold Edit/Write!" >&2
  exit 1
fi
echo "PASS: Negative mutation checks confirmed validate-skills.sh rejects broken frontmatter AND blocks write tools on pass-inspector."

# Feature 2: Service-Door Bouncer Hook (allow + 3 block cases)
echo "-> Feature 2: Service-Door Bouncer Hook (features/service-door-bouncer.md)"
echo '{"tool_name":"Bash","tool_input":{"command":"git status"}}' | bash hooks/pre-tool-guard.sh

set +e
echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' | bash hooks/pre-tool-guard.sh > /dev/null 2>&1
RC_PUSH=$?
echo '{"tool_name":"Bash","tool_input":{"command":"gh pr merge 42 --auto"}}' | bash hooks/pre-tool-guard.sh > /dev/null 2>&1
RC_MERGE=$?
echo '{"tool_name":"Bash","tool_input":{"command":"pytest --no-verify"}}' | bash hooks/pre-tool-guard.sh > /dev/null 2>&1
RC_NOVERIFY=$?
set -e

if [[ "$RC_PUSH" -ne 2 || "$RC_MERGE" -ne 2 || "$RC_NOVERIFY" -ne 2 ]]; then
  echo "FAIL: Bouncer hook did not return exit code 2 (got push=$RC_PUSH, merge=$RC_MERGE, noverify=$RC_NOVERIFY)" >&2
  exit 1
fi
echo "PASS: Service-Door Bouncer allowed safe commands (0) and blocked all 3 forbidden patterns (exit code 2)."

# Feature 3: Prep Log Trail & Formula-Injection Escaping
echo "-> Feature 3: Prep Log Decision Trail (features/prep-log-trail.md)"
SCRATCH_TSV="$SCRATCH_DIR/decisions.tsv"
bash skills/head-chef-mode/scripts/log-decision.sh \
  "$SCRATCH_TSV" \
  "taste-the-dish" \
  "=CMD|'/C calc'!A0" \
  "+malicious-hypothesis" \
  "features/prep-log-trail.md:L1-L20" \
  "verified formula escaping"

if ! grep -q "'=CMD" "$SCRATCH_TSV" || ! grep -q "'+malicious-hypothesis" "$SCRATCH_TSV"; then
  echo "FAIL: log-decision.sh did not prefix formula-injection characters with a leading single quote!" >&2
  cat "$SCRATCH_TSV" >&2
  exit 1
fi
echo "PASS: Prep Log appended TSV row and neutralized formula-injection prefixes."

# Feature 4: Daily Chef Rituals (Pre-Shift Check, FIFO Date-Dots, Clean-As-You-Go + Allergy Scan)
echo "-> Feature 4: Daily Chef Rituals (features/chef-rituals.md)"
bash skills/head-chef-mode/scripts/pre-shift-check.sh

# Negative check 4a: Verify audit-date-dots.sh fails on a spoiled container in scratch
mkdir -p "$SCRATCH_DIR/spoiled-walkin"
cat << 'EOF' > "$SCRATCH_DIR/spoiled-walkin/old_shim.py"
# FIFO-DATE-DOT: expires=2020-01-01 owner=line-cook ticket=TKT-001 action=86-shim
def legacy_shim():
    return True
EOF
if bash skills/head-chef-mode/scripts/audit-date-dots.sh "$SCRATCH_DIR/spoiled-walkin" > /dev/null 2>&1; then
  echo "FAIL: audit-date-dots.sh did not fail on an expired 2020-01-01 FIFO-DATE-DOT container!" >&2
  exit 1
fi
echo "PASS: Walk-In FIFO scanner rejected spoiled container (expires=2020-01-01)."

# Negative check 4b: Verify clean-station.sh fails on a dirty board with scratch droppings & debug crumbs
mkdir -p "$SCRATCH_DIR/dirty-station"
touch "$SCRATCH_DIR/dirty-station/leftover.bak"
if bash skills/head-chef-mode/scripts/clean-station.sh --allergy --dir "$SCRATCH_DIR/dirty-station" > /dev/null 2>&1; then
  echo "FAIL: clean-station.sh did not fail on a dirty cutting board with .bak droppings!" >&2
  exit 1
fi
echo "PASS: Station Sanitizer rejected dirty cutting board with leftover .bak droppings."

echo "================================================================"
echo " [4/5] PROOF: Writing durable verification proof before Dishpit"
echo "================================================================"
SKILL_COUNT="$(find skills -mindepth 2 -maxdepth 2 -name 'SKILL.md' | wc -l | tr -d ' ')"
AGENT_COUNT="$(find agents -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
FEATURE_COUNT="$(find features -maxdepth 1 -name '*.md' ! -name 'README.md' | wc -l | tr -d ' ')"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

cat <<EOF > "$PROOF_FILE"
{
  "harness": "verify-kitchen-cookbook",
  "timestamp_utc": "$TIMESTAMP",
  "status": "PASSED",
  "counts": {
    "skills_validated": $SKILL_COUNT,
    "station_agents_validated": $AGENT_COUNT,
    "features_verified": $FEATURE_COUNT
  },
  "checks": {
    "cookbook_validation": "PASS",
    "negative_mutation_detection": "PASS",
    "bouncer_allow_safe_command": 0,
    "bouncer_block_git_push_main": $RC_PUSH,
    "bouncer_block_gh_pr_merge": $RC_MERGE,
    "bouncer_block_no_verify": $RC_NOVERIFY,
    "prep_log_formula_injection_escaped": "PASS",
    "pre_shift_walk_in_lineup": "PASS",
    "fifo_date_dot_spoilage_rejected": "PASS",
    "clean_station_dirty_board_rejected": "PASS"
  }
}
EOF
echo "Wrote proof artifact: $PROOF_FILE"

echo "================================================================"
echo " [5/5] DISHPIT: Tearing down scratch & verifying proof survival"
echo "================================================================"
rm -rf "$SCRATCH_DIR"
if [[ -d "$SCRATCH_DIR" ]]; then
  echo "FAIL: Scratch directory survived Dishpit teardown!" >&2
  exit 1
fi
if [[ ! -s "$PROOF_FILE" ]]; then
  echo "FAIL: Proof file missing or empty after Dishpit teardown!" >&2
  exit 1
fi

echo "PASS: Dishpit clean, proof artifact survived at .audit/evidence/proof-kitchen-cookbook.json"
echo "Order up! All $FEATURE_COUNT mapped features and $SKILL_COUNT skills verified."
