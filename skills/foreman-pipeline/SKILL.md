---
name: foreman-pipeline
description: Vercel Eve / Foreman 4-station software factory pipeline (Classifier -> Analyst -> Implementer -> Reviewer + Researcher). Routes inbound issues into reviewed draft pull requests using isolated git worktrees, pass-by-ID handoff artifacts, anti-poisoning Factory Brain memory, and cross-vendor review.
---

# Foreman 4-Station Pipeline (`/foreman-pipeline`)

Foreman puts an autonomous station on every stage of the development loop while keeping humans on the irreversible judgment calls (marking ready and merging).

## 1. The Orchestrator Routes, Not Writes (Zero Self-Delegation)

The orchestrator is strictly a routing layer, never a fifth coding station:
- Never write application code or perform deep repo analysis inside the orchestrator thread.
- Never delegate to a generic clone of the root agent (`disableTool()` on self-delegation).
- Route every work item through the four task-mode stations **in strict order**:
  $$\texttt{classifier} \longrightarrow (\texttt{researcher}) \longrightarrow \texttt{analyst} \longrightarrow \texttt{implementer} \longleftrightarrow \texttt{reviewer}$$

## 2. The Four Task-Mode Stations

Every station runs in a fresh, stateless session starting with `Read <path>/worker.md before anything else.` and returns a strict structured output schema without pausing for interactive questions:

| Station | Owns | Hands Back |
| :--- | :--- | :--- |
| **`classifier`** | Triage: `work_type`, `priority`, `complexity`, `affected_area`, repo labels, and `needs_clarification`. | Structured classification. If `needs_clarification == true`, the pipeline posts the questions and **halts immediately**. |
| **`researcher`** *(optional)* | External fact-finding (upstream bugs, library versions) not present in the repo. | Cited findings with confidence levels, open gaps, and a pass-by-ID memo (`memo_artifact_id`). |
| **`analyst`** | Planning against a live checkout: approach, ordered steps, risks, and **verbatim acceptance criteria**. | Structured plan + acceptance criteria contract + `analysis_artifact_id`. |
| **`implementer`** | Executing the plan in an isolated `git worktree` on branch `factory/<item-id>`, running the repo's `verify-*` harness and tests, committing, and pushing. | `branch_name`, per-file change summary, and verification command output. |
| **`reviewer`** | Independent judgment of the pushed `factory/<item-id>` branch against the analyst's verbatim acceptance criteria, running on a **different model vendor** than `implementer`. | `approve`, `request_changes`, or `reject`, with pass/fail + `file:line` evidence for every criterion. |

## 3. Three Rules That Hold the Line Together

1. **The Review Is Independent (`principle-cross-vendor-blind-review`)**:
   - The reviewer never sees the implementer's internal Chain-of-Thought reasoning—only the original work item, the analyst's acceptance criteria, the pushed branch diff, and verification outputs.
   - `reviewer` always runs on a different model vendor family than `implementer`.
2. **The Acceptance Criteria Are the Verbatim Contract**:
   - The analyst writes them; the reviewer grades each one verbatim. `approve` is forbidden if any criterion fails.
3. **Revisions Are Bounded (`MAX_REVISION_ROUNDS = 2`)**:
   - On `request_changes`, send the reviewer's blocking findings to a fresh `implementer` and re-run `reviewer`, **at most twice**. If the branch still fails after 2 revisions, halt the line and report the unresolved findings rather than opening a bad PR.
   - Similarly, automated Red-CI fix loops only touch `factory/*` branches and halt after **at most 2 attempts**.

## 4. Pass-by-ID Handoff Artifacts & Anti-Poisoning Factory Brain

- **Pass-by-ID Artifacts**: Long memos travel between stations by strict regex-anchored ID (`^[a-z0-9]+(?:-[a-z0-9]+)*$`, zero dots or slashes, preventing `../` path traversal). Saves never overwrite and mint a unique suffixed ID (`analysis-dedupe-emails-k3f9qz`).
- **Anti-Poisoning Factory Brain**: Shared repository notes live at `factory-brain/<sha256(FACTORY_REPO)>.md` (key derived purely from static repo config, never from model input). Unattended runs from labeled public issues may **read** the Factory Brain but are **denied writes** so prompt-injected issue bodies cannot poison future runs.
- **Firewall-Brokered Git Credentials**: Git tokens never enter the sandbox environment. Pushes validate `branch_name` (`factory/*` only; refusing `main`, `master`, `HEAD`, `refs/*`, `..`) and target literal `https://github.com/<FACTORY_REPO>.git` with auth headers injected at the sandbox egress firewall.
