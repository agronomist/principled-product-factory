# Working in this repo

A Claude Code plugin: 5 skills in `skills/`, 2 agents in `agents/`, one safety hook in
`hooks/`. `archive/` is the old version; do not load or maintain it.

- Run `bash tests/check.sh` before committing.
- Add a skill or rule only when a real failed run calls for it (see `evals/`).
- Push to `factory/*` branches and open draft PRs. A person merges.
- The hook only catches accidents. GitHub branch protection is the real lock.
