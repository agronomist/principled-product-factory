---
name: kitchen-brigade
description: Brigade de Cuisine 4-station software pipeline (Host Triage -> Sous Chef Planner -> Line Cook Implementer -> Blind Pass Inspector + Forager Researcher). Routes inbound tickets into plated draft pull requests using isolated git worktree cutting boards, pass-by-ID prep notes, anti-poisoning Master Recipe Book memory, and cross-vendor tasting.
---

# Kitchen Brigade 4-Station Pipeline (`/kitchen-brigade`)

Organizes software delivery like the classic **Brigade de Cuisine**: an Expediter calls the tickets and routes work across specialized, stateless line stations while keeping the Head Chef (human) on the final service bell (marking ready and merging).

## 1. The Expediter Calls the Tickets, Never Cooks on the Line

The orchestrator is strictly an **Expediter at the pass**, never a fifth line cook:
- Never write application code or perform deep repo prep inside the Expediter thread.
- Never delegate to an undifferentiated clone of the root agent (self-delegation is structurally disabled).
- Route every order through the four task-mode stations **in strict order**:
  $$\texttt{host\_triage} \longrightarrow (\texttt{forager\_researcher}) \longrightarrow \texttt{sous\_chef\_planner} \longrightarrow \texttt{line\_cook\_implementer} \longleftrightarrow \texttt{pass\_inspector}$$

## 2. The Four Task-Mode Line Stations

Every station runs in a fresh, stateless shift starting with `Read <path>/station-brief.md before anything else.` and returns a strict structured dish schema without pausing for interactive questions:

| Station | Owns | Hands Back |
| :--- | :--- | :--- |
| **`host_triage` (`classifier`)** | Ticket triage: `work_type`, `priority`, `complexity`, `affected_area`, repo labels, and `needs_clarification`. | Structured ticket classification. If `needs_clarification == true`, posts the questions and **halts immediately**. |
| **`forager_researcher`** *(optional)* | External ingredient sourcing (upstream bugs, library versions) not in the walk-in pantry. | Cited findings with confidence levels, open gaps, and a pass-by-ID prep note (`memo_artifact_id`). |
| **`sous_chef_planner` (`analyst`)** | Recipe planning against a live checkout: approach, ordered prep steps, risks, and **verbatim plating criteria**. | Structured recipe plan + plating criteria contract + `analysis_artifact_id`. |
| **`line_cook_implementer`** | Cooking the dish on an isolated `git worktree` cutting board on branch `factory/<ticket-id>`, running the tasting harness and tests, committing, and pushing. | `branch_name`, per-file change summary, and tasting command output. |
| **`pass_inspector` (`reviewer`)** | Independent blind tasting of the pushed `factory/<ticket-id>` branch against the Sous Chef's verbatim plating criteria, running on a **different model vendor** than the Line Cook. | `approve`, `request_changes` (refire), or `reject` (86), with pass/fail + `file:line` proof for every criterion. |

## 3. Three Rules That Hold the Brigade Together

1. **The Tasting Is Blind & Independent (`principle-blind-taste-test`)**:
   - The Pass Inspector never sees the Line Cook's internal Chain-of-Thought monologue—only the original ticket, the Sous Chef's plating criteria, the pushed branch diff, and tasting outputs.
   - `pass_inspector` always runs on a different model vendor family than `line_cook_implementer`.
2. **The Plating Criteria Are the Verbatim Contract**:
   - The Sous Chef writes them; the Pass Inspector grades each one verbatim. `approve` is forbidden if any criterion fails.
3. **Refires Are Bounded (`MAX_REVISION_ROUNDS = 2`)**:
   - On `request_changes`, send the Pass Inspector's blocking findings to a fresh Line Cook and re-taste, **at most twice**. If the dish still fails after 2 refires, 86 the ticket and report the unresolved findings rather than putting a bad plate in the window.
   - Similarly, automated Red-CI kitchen-fire repair loops only touch `factory/*` branches and halt after **at most 2 attempts**.

## 4. Pass-by-ID Prep Notes & Anti-Poisoning Master Recipe Book

- **Pass-by-ID Prep Notes**: Long research and recipe memos travel between stations by strict regex-anchored ticket ID (`^[a-z0-9]+(?:-[a-z0-9]+)*$`, zero dots or slashes, preventing `../` traversal). Saves never overwrite and mint a unique suffixed ID (`prep-dedupe-emails-k3f9qz`).
- **Anti-Poisoning Master Recipe Book**: Shared kitchen notes live at `factory-brain/<sha256(FACTORY_REPO)>.md` (key derived purely from static repo config, never from model input). Unattended runs from labeled public issues may **read** the Master Recipe Book but are **denied writes** so prompt-injected order tickets cannot poison future shifts.
- **Service-Door Brokered Git Credentials**: Git tokens never enter the kitchen sandbox. Pushes validate `branch_name` (`factory/*` only; refusing `main`, `master`, `HEAD`, `refs/*`, `..`) and target literal `https://github.com/<FACTORY_REPO>.git` with auth headers injected at the service-door firewall.
