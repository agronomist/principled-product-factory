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

  # If this repo has a local .claude/skills rack, verify the skill is actually on the rack
  if [ -d "$REPO_ROOT/.claude/skills" ] && [ ! -e "$REPO_ROOT/.claude/skills/$dir_name/SKILL.md" ]; then
    echo "ERROR: Skill '$dir_name' is in skills/ but missing from .claude/skills/$dir_name. FIX: Run './install.sh .' to sync station symlinks." >&2
    exit 1
  fi

done

AGENTS_DIR="$REPO_ROOT/agents"
AGENT_COUNT=0
if [ -d "$AGENTS_DIR" ]; then
  for agent_md in "$AGENTS_DIR"/*.md; do
    [ -e "$agent_md" ] || continue
    AGENT_COUNT=$((AGENT_COUNT + 1))
    base_name="$(basename "$agent_md" .md)"
    first_line="$(head -n 1 "$agent_md")"
    if [ "$first_line" != "---" ]; then
      echo "ERROR: $agent_md is missing opening YAML frontmatter '---' on line 1. FIX: Add YAML frontmatter with name, description, and tools." >&2
      exit 1
    fi
    frontmatter="$(awk 'NR==1 && /^---$/ {in_fm=1; next} in_fm && /^---$/ {exit} in_fm {print}' "$agent_md")"
    fm_name="$(printf '%s\n' "$frontmatter" | awk -F': *' '/^name:/ {print $2; exit}' | tr -d '"'\''')"
    if [ "$fm_name" != "$base_name" ]; then
      echo "ERROR: $agent_md frontmatter name '$fm_name' does not match filename '$base_name'. FIX: Set 'name: $base_name' in $agent_md." >&2
      exit 1
    fi
    if ! printf '%s\n' "$frontmatter" | grep -q '^tools:'; then
      echo "ERROR: $agent_md is missing 'tools:' allowlist in frontmatter. FIX: Add a 'tools:' line to $agent_md." >&2
      exit 1
    fi

    # Lock on the knife drawer: read-only / inspection stations must NEVER hold Edit or Write tools
    tools_line="$(printf '%s\n' "$frontmatter" | awk -F': *' '/^tools:/ {print $2; exit}')"
    case "$base_name" in
      host-triage|forager-researcher|sous-chef-planner|pass-inspector)
        if printf '%s\n' "$tools_line" | grep -Eq '(^|[[:space:],])(Edit|Write)([[:space:],]|$)'; then
          echo "ERROR: Read-only/inspection station '$base_name' holds write tools ($tools_line)! FIX: Confiscate Edit and Write from $agent_md." >&2
          exit 1
        fi
        ;;
    esac

    if [ -d "$REPO_ROOT/.claude/agents" ] && [ ! -e "$REPO_ROOT/.claude/agents/$base_name.md" ]; then
      echo "ERROR: Agent '$base_name' is in agents/ but missing from .claude/agents/$base_name.md. FIX: Run './install.sh .' to sync station symlinks." >&2
      exit 1
    fi
  done
fi

echo "OK: Validated $SKILL_COUNT modular kitchen skills and $AGENT_COUNT Claude Code station subagents (100% frontmatter, symlink rack & tool-boundary integrity)."
