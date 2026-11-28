#!/usr/bin/env bash
set -euo pipefail

# Installer for the-pass
# Usage:
#   ./install.sh                  # Install globally into ~/.claude/{skills,agents,hooks}, ~/.cursor/skills
#   ./install.sh /path/to/project # Install into a specific project's .claude/ and .cursor/ folders

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_BASE="${1:-$HOME}"
mkdir -p "$TARGET_BASE"
TARGET_ABS="$(cd "$TARGET_BASE" 2>/dev/null && pwd || echo "$TARGET_BASE")"

SKILL_COUNT="$(find "$REPO_ROOT/skills" -mindepth 2 -maxdepth 2 -name 'SKILL.md' | wc -l | tr -d ' ')"
AGENT_COUNT="$(find "$REPO_ROOT/agents" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"

# Self-repo idempotency guard: if the caller runs `./install.sh .` inside this repo,
# keep the clean relative directory symlinks (.claude/skills -> ../skills) instead of creating circular links.
if [ "$TARGET_ABS" = "$REPO_ROOT" ]; then
  mkdir -p "$REPO_ROOT/.claude" "$REPO_ROOT/.cursor" "$REPO_ROOT/.agents"
  ln -sfn ../skills "$REPO_ROOT/.claude/skills"
  ln -sfn ../agents "$REPO_ROOT/.claude/agents"
  ln -sfn ../hooks "$REPO_ROOT/.claude/hooks"
  ln -sfn ../skills "$REPO_ROOT/.cursor/skills"
  ln -sfn ../skills "$REPO_ROOT/.agents/skills"
  echo "Verified in-repo links for $SKILL_COUNT skills, $AGENT_COUNT agents and the safety hook."
  exit 0
fi

if [ "$TARGET_ABS" = "$HOME" ]; then
  CLAUDE_DIR="$HOME/.claude"
  CURSOR_DIR="$HOME/.cursor"
  AGENTS_DIR="$HOME/.agents"
  HOOK_CMD="bash \"\$HOME/.claude/hooks/pre-tool-guard.sh\""
  SCOPE_LABEL="global ($HOME)"
else
  CLAUDE_DIR="$TARGET_ABS/.claude"
  CURSOR_DIR="$TARGET_ABS/.cursor"
  AGENTS_DIR="$TARGET_ABS/.agents"
  HOOK_CMD='bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-guard.sh\"'
  SCOPE_LABEL="project ($TARGET_ABS)"
fi

mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents" "$CLAUDE_DIR/hooks" "$CURSOR_DIR/skills" "$AGENTS_DIR/skills"

# Remove links left by an earlier version of this repo whose targets no longer exist
for link in "$CLAUDE_DIR"/skills/* "$CLAUDE_DIR"/agents/* "$CURSOR_DIR"/skills/* "$AGENTS_DIR"/skills/*; do
  if [ -L "$link" ] && [ ! -e "$link" ]; then
    case "$(readlink "$link")" in "$REPO_ROOT"/*) rm "$link" ;; esac
  fi
done

for skill_dir in "$REPO_ROOT"/skills/*/; do
  skill_name="$(basename "$skill_dir")"
  ln -sfn "$skill_dir" "$CLAUDE_DIR/skills/$skill_name"
  ln -sfn "$skill_dir" "$CURSOR_DIR/skills/$skill_name"
  ln -sfn "$skill_dir" "$AGENTS_DIR/skills/$skill_name"
done

for agent_md in "$REPO_ROOT"/agents/*.md; do
  agent_name="$(basename "$agent_md")"
  ln -sfn "$agent_md" "$CLAUDE_DIR/agents/$agent_name"
done

# Install the PreToolUse safety hook & hooks.json manifest
ln -sfn "$REPO_ROOT/hooks/pre-tool-guard.sh" "$CLAUDE_DIR/hooks/pre-tool-guard.sh"
ln -sfn "$REPO_ROOT/hooks/hooks.json" "$CLAUDE_DIR/hooks/hooks.json"

# Wire .claude/settings.json if not already present so the PreToolUse safety hook runs automatically
if [ ! -f "$CLAUDE_DIR/settings.json" ]; then
  cat <<EOF > "$CLAUDE_DIR/settings.json"
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$HOOK_CMD"
          }
        ]
      }
    ]
  }
}
EOF
fi

echo "Installed $SKILL_COUNT skills and $AGENT_COUNT agents into $SCOPE_LABEL."
if grep -q 'pre-tool-guard' "$CLAUDE_DIR/settings.json"; then
  echo "Safety hook is wired in $CLAUDE_DIR/settings.json"
else
  echo "WARNING: safety hook NOT wired: $CLAUDE_DIR/settings.json already exists. Add the PreToolUse hook yourself."
fi
echo "Next: run /ship with a task."
