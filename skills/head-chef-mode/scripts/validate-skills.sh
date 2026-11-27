#!/usr/bin/env bash
set -euo pipefail

# Validates all modular kitchen skills in skills/*/SKILL.md:
# 1. Every skill has valid YAML frontmatter with `name:` (matching its directory name) and `description:`.
# 2. Every file listed under `file_names:` in frontmatter exists inside the skill directory.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "ERROR: skills/ directory not found at $SKILLS_DIR" >&2
  exit 1
fi

SKILL_COUNT=0

for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
  skill_dir="$(dirname "$skill_md")"
  dir_name="$(basename "$skill_dir")"
  SKILL_COUNT=$((SKILL_COUNT + 1))

  first_line="$(head -n 1 "$skill_md")"
  if [ "$first_line" != "---" ]; then
    echo "ERROR: $skill_md is missing opening YAML frontmatter '---' on line 1. FIX: Add YAML frontmatter with name and description." >&2
    exit 1
  fi

  frontmatter="$(awk 'NR==1 && /^---$/ {in_fm=1; next} in_fm && /^---$/ {exit} in_fm {print}' "$skill_md")"

  fm_name="$(printf '%s\n' "$frontmatter" | awk -F': *' '/^name:/ {print $2; exit}' | tr -d '"'\''')"
  if [ "$fm_name" != "$dir_name" ]; then
    echo "ERROR: $skill_md frontmatter name '$fm_name' does not match directory '$dir_name'. FIX: Set 'name: $dir_name' in $skill_md." >&2
    exit 1
  fi

  if ! printf '%s\n' "$frontmatter" | grep -q '^description:'; then
    echo "ERROR: $skill_md is missing 'description:' in frontmatter. FIX: Add a routing description to $skill_md." >&2
    exit 1
  fi

  while IFS= read -r rel_file; do
    [ -z "$rel_file" ] && continue
    target_path="$skill_dir/$rel_file"
    if [ ! -e "$target_path" ]; then
      echo "ERROR: $skill_md lists missing resource '$rel_file' under file_names. FIX: Create '$target_path' or remove it from file_names." >&2
      exit 1
    fi
  done < <(printf '%s\n' "$frontmatter" | awk '/^file_names:/ {in_fn=1; next} in_fn && /^  - / {sub(/^  - /, ""); print; next} in_fn && /^[^ ]/ {in_fn=0}')

done

echo "OK: Validated $SKILL_COUNT modular kitchen skills in $SKILLS_DIR (100% frontmatter & resource integrity)."
