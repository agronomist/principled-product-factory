---
name: principle-orchestrator-routes-not-writes
description: Apply when orchestrating multi-stage work items. The orchestrator is strictly a routing layer across stateless task-mode stations (Classifier -> Analyst -> Implementer -> Reviewer); it never writes code directly, never self-delegates, and passes long documents by validated artifact ID.
---

# Principle: The Orchestrator Routes, Not Writes

Keep the orchestrator context window clean and the station pipeline structural rather than optional (Vercel `eve` / Foreman).

- Disable self-delegation (`disableTool()` on the root agent clone). The orchestrator is a routing layer, not a fifth coding station.
- Route every work item through the four task-mode stations in strict order: `classifier -> analyst -> implementer -> reviewer` (+ optional `researcher`). Never skip a station.
- If `classifier` returns `needs_clarification: true`, post the clarification questions and stop immediately rather than stranding an unattended run.
- Pass long research and analysis documents between stations by strict regex-validated ID (`^[a-z0-9]+(?:-[a-z0-9]+)*$`, zero dots or slashes) rather than pasting long prose through the orchestrator's context.
