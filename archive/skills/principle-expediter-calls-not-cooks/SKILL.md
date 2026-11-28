---
name: principle-expediter-calls-not-cooks
description: Apply when orchestrating multi-stage kitchen tickets. The Expediter is strictly a routing layer across stateless task-mode line stations (Host Triage -> Sous Chef Planner -> Line Cook -> Pass Inspector); it never cooks directly on the line, never self-delegates, and passes long prep notes by validated ticket ID.
---

# Principle: The Expediter Calls the Tickets, Never Cooks

Keep the Expediter's ticket rail clean and the Brigade de Cuisine pipeline structural rather than optional.

- Disable self-delegation (`disableTool()` on the root agent clone). The Expediter calls the tickets at the pass; it is never a fifth line cook.
- Route every order through the four task-mode line stations in strict order: `host_triage -> sous_chef_planner -> line_cook_implementer -> pass_inspector` (+ optional `forager_researcher`). Never skip a station.
- If `host_triage` returns `needs_clarification: true`, post the clarification questions and stop immediately rather than leaving a stove lit on an unattended shift.
- Pass long foraging and recipe memos between stations by strict regex-validated prep-note ID (`^[a-z0-9]+(?:-[a-z0-9]+)*$`, zero dots or slashes) rather than pasting long prose through the Expediter's context.
