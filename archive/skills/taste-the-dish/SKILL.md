---
name: taste-the-dish
description: Generate and maintain a project-local live tasting harness skill (Fire Up -> Station Check -> Plate -> Proof -> Dishpit Cleanup) and living diner-POV menu map (features/) that drives the real application the way a guest does. Use for /taste-the-dish.
---

# Taste the Dish — Live Verification Harness (`/taste-the-dish`)

Every kitchen line in the repository needs a scripted way to taste the real dish the way a diner does and capture durable proof (`principle-taste-before-serving`).

## 1. Inspect the Kitchen Line First
Determine from the codebase:
- **Dining Surface**: CLI/TUI, HTTP API, web UI, or background worker.
- **Fire Up & Isolate**: Exact command to boot from an empty scratch prep directory or isolated port so parallel Cook-Off contenders never bump elbows.
- **Plate & Observe**: Programmatic handles (CLI arguments, HTTP routes, UI selectors) and observable proof (exit codes, JSON bodies, SQLite WAL rows, files written).

## 2. Generate the Five Mandatory Tasting Primitives
1. **Fire Up (`Launch`)**: Exact command that boots the application from an empty scratch folder to a genuinely ready state.
2. **Station Check (`Doctor`)**: One read-only check answering *"Is this station clean and ready to cook?"* (process alive, right build/version, port/scratch owned by this shift).
3. **Plate (`Drive`)**: Real commands exercising diner journeys from the menu map.
4. **Proof (`Evidence`)**: What tasting proof artifacts are saved to a durable `evidence/` directory outside the scratch tub.
5. **Dishpit (`Cleanup`)**: Deterministic teardown of only the PIDs and scratch directories created by `Fire Up`.

## 3. Hold Three Live-Tasting Invariants
1. **Mandatory Station-Check Gate**: Never `Plate` on a station that hasn't passed `Station Check` since `Fire Up` or since its last failed dish.
2. **Proof Survival Across Dishpit Cleanup**: After `Dishpit` finishes, confirm the proof files in `evidence/` still exist on disk (*a dishpit cleanup that throws out the tasting proof fails the check*).
3. **Zero Dirty Dishes Outliving the Shift**: Confirm the ephemeral scratch folder is completely removed after `Dishpit`.

## 4. Seed & Maintain the Living Menu Map (`features/`)
Maintain `features/README.md` plus one file per diner-facing dish (`features/<dish>.md`), each with four mandatory H2 sections:
- `## Sub-features`
- `## How to get to it (user POV)`
- `## Driving it with <harness>`
- `## Gotchas`
