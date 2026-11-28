#!/usr/bin/env bash
# Reproducible benchmark comparing v0 (commit deba469), v1 (commit 8b0a141, 42 skills),
# and v3 (current HEAD, 5 skills) across 6 real tasks and measuring prompt token footprint.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

score_commit() {
  local ref="$1"
  local label="$2"
  local tmp
  tmp="$(mktemp -d)"
  if [[ "$ref" == "WORKTREE" ]]; then
    cp -R .claude-plugin agents hooks skills install.sh "$tmp/"
  else
    git archive "$ref" | tar -x -C "$tmp"
  fi

  local skill_count agent_count total_bytes approx_tokens passed=0 total=6
  skill_count="$(find "$tmp/skills" -mindepth 2 -maxdepth 2 -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')"
  agent_count="$(find "$tmp/agents" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  total_bytes="$(cat "$tmp"/skills/*/SKILL.md "$tmp"/agents/*.md 2>/dev/null | wc -c | tr -d ' ')"
  approx_tokens=$(( (total_bytes + 3) / 4 ))

  # Task 1: Plugin manifest validity (no ../ parent traversal in .claude-plugin/plugin.json)
  if [[ -f "$tmp/.claude-plugin/plugin.json" ]] && ! grep -q '\.\./' "$tmp/.claude-plugin/plugin.json"; then
    passed=$((passed + 1))
  fi

  # Task 2: Plugin ships hooks/hooks.json and installer wires hook into clean target project
  local ext="$tmp/ext-proj"
  mkdir -p "$ext"
  if [[ -f "$tmp/hooks/hooks.json" ]] && bash "$tmp/install.sh" "$ext" >/dev/null 2>&1 && [[ -f "$ext/.claude/settings.json" ]]; then
    passed=$((passed + 1))
  fi

  # Task 3: Hook blocks quoted branch push (`git push -f origin "main"`) and flag-prefixed push (`git -C . push origin main`)
  local rc1=0 rc2=0
  printf '{"tool_input":{"command":"git push -f origin \\"main\\""}}' | bash "$tmp/hooks/pre-tool-guard.sh" >/dev/null 2>&1 || rc1=$?
  printf '{"tool_input":{"command":"git -C . push origin main"}}' | bash "$tmp/hooks/pre-tool-guard.sh" >/dev/null 2>&1 || rc2=$?
  if [[ "$rc1" -eq 2 && "$rc2" -eq 2 ]]; then
    passed=$((passed + 1))
  fi

  # Task 4: Hook blocks short `-n` bypass (`git commit -n -m x`) AND allows commit message mentioning `--no-verify`
  local rc3=0 rc4=0
  printf '{"tool_input":{"command":"git commit -n -m x"}}' | bash "$tmp/hooks/pre-tool-guard.sh" >/dev/null 2>&1 || rc3=$?
  printf '{"tool_input":{"command":"git commit -m \\"mention --no-verify\\""}}' | bash "$tmp/hooks/pre-tool-guard.sh" >/dev/null 2>&1 || rc4=$?
  if [[ "$rc3" -eq 2 && "$rc4" -eq 0 ]]; then
    passed=$((passed + 1))
  fi

  # Task 5: Hook blocks PR merge via `gh api -X PUT repos/o/r/pulls/1/merge`
  local rc5=0
  printf '{"tool_input":{"command":"gh api -X PUT repos/o/r/pulls/1/merge"}}' | bash "$tmp/hooks/pre-tool-guard.sh" >/dev/null 2>&1 || rc5=$?
  if [[ "$rc5" -eq 2 ]]; then
    passed=$((passed + 1))
  fi

  # Task 6: Hook blocks mutating Bash commands (`git commit`, `sed -i`, `rm`) when agent_type is `reviewer`
  local rc6=0 rc7=0
  printf '{"agent_type":"reviewer","tool_input":{"command":"sed -i s/a/b/ file.txt"}}' | bash "$tmp/hooks/pre-tool-guard.sh" >/dev/null 2>&1 || rc6=$?
  printf '{"agent_type":"reviewer","tool_input":{"command":"git diff main"}}' | bash "$tmp/hooks/pre-tool-guard.sh" >/dev/null 2>&1 || rc7=$?
  if [[ "$rc6" -eq 2 && "$rc7" -eq 0 ]]; then
    passed=$((passed + 1))
  fi

  rm -rf "$tmp"
  printf '| %-24s | %6s | %6s | %14s | %15s |\n' \
    "$label" "$skill_count" "$agent_count" "$passed / $total" "~$approx_tokens tokens"
}

echo "| Setup                    | Skills | Agents | Tasks Passed   | Skill+Agent Size |"
echo "| ------------------------ | ------ | ------ | -------------- | ---------------- |"
score_commit "c92e4ea"  "v0 (initial 33-skill)"
score_commit "8b0a141"  "v1 (full 42-skill)"
score_commit "WORKTREE" "v3 (the-pass 5-skill)"
