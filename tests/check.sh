#!/usr/bin/env bash
# Repo checks: layout, frontmatter, hook behavior, reviewer read-only guard, clean install.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
fail() { echo "FAIL: $1" >&2; exit 1; }

for f in skills/*/SKILL.md agents/*.md; do
  case "$f" in skills/*) want="$(basename "$(dirname "$f")")" ;; *) want="$(basename "$f" .md)" ;; esac
  [[ "$(head -n1 "$f")" == "---" ]] || fail "$f: no frontmatter"
  grep -qx "name: $want" "$f" || fail "$f: name must be $want"
  grep -q '^description: .' "$f" || fail "$f: no description"
done
grep -Eq '^tools:.*(Edit|Write)' agents/reviewer.md && fail "reviewer must not have Edit or Write"

hook() { # expected-exit command [agent_type]
  local rc=0
  local agent="${3:-}"
  printf '{"agent_type":"%s","tool_input":{"command":"%s"}}' "$agent" "$2" | bash hooks/pre-tool-guard.sh >/dev/null 2>&1 || rc=$?
  [[ $rc == "$1" ]] || fail "hook returned $rc, expected $1: $2 (agent=$agent)"
}
hook 0 'git status'
hook 0 'git push -u origin factory/x'
hook 0 'git commit -m \"never use --no-verify\"'
hook 0 'git diff main...factory/x' reviewer
hook 0 'bash tests/check.sh' reviewer
hook 2 'git push'
hook 2 'git push origin main'
hook 2 'git push origin HEAD:main'
hook 2 'git push -f origin \"main\"'
hook 2 'git -C . push origin main'
hook 2 'git commit -n -m x'
hook 2 'gh pr merge 1'
hook 2 'gh api -X PUT repos/o/r/pulls/1/merge'
hook 2 'git commit -m \"sneaky fix\"' reviewer
hook 2 'sed -i s/a/b/ file.txt' reviewer
hook 2 'rm -rf src' reviewer

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
./install.sh "$tmp" >/dev/null
for s in skills/*/; do [[ -f "$tmp/.claude/skills/$(basename "$s")/SKILL.md" ]] || fail "install missed $s"; done
for a in agents/*.md; do [[ -f "$tmp/.claude/$a" ]] || fail "install missed $a"; done
for l in .claude/skills .claude/agents .cursor/skills .agents/skills; do [[ -e "$l" ]] || fail "broken link $l"; done
echo "PASS: all checks"
