# Feature: Cookbook & Station Subagent Structural Validation

Verifies that every skill in `skills/*/SKILL.md` and every Claude Code subagent in `agents/*.md` has valid YAML frontmatter, matching directory/file names, tool allowlists, and resolvable `file_names` pointers.

## Sub-features

- YAML frontmatter `name:` and `description:` verification across all skills in `skills/`.
- `file_names:` existence check for playbooks, scripts, and reference files.
- Claude Code subagent `name:` and `tools:` allowlist verification across `agents/*.md` (including verifying `pass-inspector.md` omits `Edit` and `Write`).

## How to get to it (user POV)

Run `bash skills/head-chef-mode/scripts/validate-skills.sh` from the repository root or invoke `bash skills/head-chef-mode/scripts/run-live-tasting.sh`.

## Driving it with verify-kitchen-cookbook

```bash
bash skills/head-chef-mode/scripts/validate-skills.sh
```

Observable end state: Exit code `0` and stdout printing `OK: Validated 34 modular kitchen skills and 5 Claude Code station subagents (100% frontmatter & resource integrity).`

## Gotchas

- Every error message printed by `validate-skills.sh` must include `FIX:` naming the exact file and field to repair (`/sharpen-the-knives` Level 3 rule).
