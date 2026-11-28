#!/usr/bin/env bash
set -euo pipefail

# One-Command Installer for the Kitchen Brigade Skill Stack (principled-product-factory)
# Usage:
#   ./install.sh                  # Install globally into ~/.claude/skills, ~/.claude/agents, ~/.cursor/skills
#   ./install.sh /path/to/project # Install into a specific project's .claude/ and .cursor/ folders

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_BASE="${1:-$HOME}"
TARGET_ABS="$(cd "$TARGET_BASE" 2>/dev/null && pwd || echo "$TARGET_BASE")"

SKILL_COUNT="$(find "$REPO_ROOT/skills" -mindepth 2 -maxdepth 2 -name 'SKILL.md' | wc -l | tr -d ' ')"
AGENT_COUNT="$(find "$REPO_ROOT/agents" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"

# Self-repo idempotency guard: if the caller runs `./install.sh .` inside this repo,
# keep the clean relative directory symlinks (.claude/skills -> ../skills) instead of creating circular links.
if [ "$TARGET_ABS" = "$REPO_ROOT" ]; then
  mkdir -p "$REPO_ROOT/.claude" "$REPO_ROOT/.cursor" "$REPO_ROOT/.agents"
  ln -sfn ../skills "$REPO_ROOT/.claude/skills"
  ln -sfn ../agents "$REPO_ROOT/.claude/agents"
  ln -sfn ../skills "$REPO_ROOT/.cursor/skills"
  ln -sfn ../skills "$REPO_ROOT/.agents/skills"
  echo "Verified in-repo station symlinks for $SKILL_COUNT Kitchen Brigade skills and $AGENT_COUNT station subagents."
  exit 0
fi

if [ "$TARGET_ABS" = "$HOME" ]; then
  CLAUDE_DIR="$HOME/.claude"
  CURSOR_DIR="$HOME/.cursor"
  AGENTS_DIR="$HOME/.agents"
  SCOPE_LABEL="global ($HOME)"
else
  CLAUDE_DIR="$TARGET_BASE/.claude"
  CURSOR_DIR="$TARGET_BASE/.cursor"
  AGENTS_DIR="$TARGET_BASE/.agents"
  SCOPE_LABEL="project ($TARGET_BASE)"
fi

mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/agents" "$CURSOR_DIR/skills" "$AGENTS_DIR/skills"

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

echo "Installed $SKILL_COUNT Kitchen Brigade skills and $AGENT_COUNT station subagents into $SCOPE_LABEL:"
echo "  - Claude Code skills : $CLAUDE_DIR/skills/"
echo "  - Claude Code agents : $CLAUDE_DIR/agents/"
echo "  - Cursor skills      : $CURSOR_DIR/skills/"
echo "  - Agent skills       : $AGENTS_DIR/skills/"
echo ""
echo "Next step in Claude Code: type /setup-kitchen or /head-chef-mode"
