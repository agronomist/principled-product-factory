---
name: principle-plate-at-the-pass
description: Apply to all git operations, tool approval policies, and unattended overnight shifts. Plated Draft pull requests on factory/* branches sit under the heat lamp at the pass waiting for the Head Chef; unattended runs are denied (never parked) on dining-room service or Master Recipe Book writes, and git credentials never enter a station sandbox.
---

# Principle: Plate at the Pass (Draft PR Unattended Ceiling)

Gate kitchen actions on what the call *does* and who the caller *is*, so unattended overnight shifts cannot serve uninspected dishes to the dining room, poison the Master Recipe Book, or hang waiting for an approval card.

- **Heat Lamp at the Pass (Draft PR Ceiling)**: `create_pull_request(draft: true)` runs ungated for authorized shifts, while `draft: false` or ringing the service bell (`mark_pr_ready`) is **denied** on unattended runs (never parked on an approval card when no Head Chef is on duty) and waits for human approval on interactive shifts. `merge_pull_request` stays out of the agent tool surface entirely.
- **Anti-Poisoning Master Recipe Book**: Derive the Master Recipe Book key purely from `SHA256(FACTORY_REPO)` at load time. Deny Master Recipe Book writes from unattended ticket runs so prompt-injected order tickets cannot poison future shifts.
- **Inert Branches & Service-Door Credentials**: Validate that pushes target only `factory/*` branches (refusing `main`, `master`, `HEAD`, `refs/*`, `..`). Inject GitHub installation tokens only at the service-door firewall egress layer to literal `https://github.com/<FACTORY_REPO>.git`, never inside the station sandbox or to model-writable `origin` remotes.
