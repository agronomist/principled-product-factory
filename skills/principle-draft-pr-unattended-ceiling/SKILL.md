---
name: principle-draft-pr-unattended-ceiling
description: Apply to all git operations, tool approval policies, and unattended background runs. Draft pull requests on factory/* branches are the unattended ceiling; unattended runs are denied (never parked) on shipping actions or Factory Brain writes, and git credentials never enter a sandbox.
---

# Principle: Draft PR Is the Unattended Ceiling

Gate actions on what the tool call *does* and who the caller *is*, so unattended runs cannot ship unreviewed code, poison shared memory, or strand on interactive prompts.

- **Draft PR Ceiling**: `create_pull_request(draft: true)` runs ungated for authorized sessions, while `draft: false` or marking a PR ready is **denied** on unattended runs (never parked on an approval card where nobody is watching) and waits for human approval on interactive runs. `merge_pull_request` stays out of the agent tool surface entirely.
- **Anti-Poisoning Factory Brain**: Derive the Factory Brain key purely from `SHA256(FACTORY_REPO)` at load time. Deny Factory Brain writes from unattended issue runs so prompt-injected issue bodies cannot poison future runs.
- **Inert Branches & Firewall Credentials**: Validate that pushes target only `factory/*` branches (refusing `main`, `master`, `HEAD`, `refs/*`, `..`). Inject GitHub installation tokens only at the sandbox firewall egress layer to literal `https://github.com/<FACTORY_REPO>.git`, never inside the sandbox or to model-writable `origin` remotes.
