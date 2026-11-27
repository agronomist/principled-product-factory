---
name: create-verification-skill
description: Generate and maintain a project-local verification skill (verify-<app>) that launches, doctor-checks, drives the real app surface, captures durable evidence that survives cleanup, and keeps a living user-POV feature map. Use for /create-verification-skill or /maintain-verification-skill.
---

# Create & Maintain a Verification Skill (`/create-verification-skill`)

Every product in the factory needs a scripted way to drive the real application the way a user does and prove behavior on the real artifact (`principle-prove-it-works`).

## 1. Interview the Repo, Not the User
Inspect the codebase to determine:
- **Surface**: CLI/TUI, HTTP API, web UI, background worker, or library.
- **Run & Isolate**: Exact command to boot from an empty data/scratch directory on an isolated port or temp folder so parallel Arena workers never collide.
- **Drive & Observe**: Programmatic handles (CLI flags, HTTP endpoints, Playwright selectors) and observable side effects (exit codes, JSON bodies, SQLite WAL rows, files written).

## 2. Generate `skills/verify-<app>/SKILL.md` with Five Mandatory Primitives
1. **Launch**: Exact command that boots the app from an empty scratch directory to a genuinely ready state.
2. **Doctor**: One read-only check answering *"Is this instance worth driving?"* (process alive, right build/version, port/scratch owned by this session).
3. **Drive**: Real commands/selectors exercising user journeys from the feature map.
4. **Evidence**: What proof artifacts are written to a durable `evidence/` path outside the scratch directory.
5. **Cleanup**: Deterministic teardown of only the PIDs and scratch directories created by `Launch`.

## 3. Hold Three Live-Pass Invariants
1. **Mandatory Doctor Gate**: Never `Drive` an instance that hasn't passed `Doctor` since launch or since its last failed drive.
2. **Evidence Survival Across Cleanup**: After `Cleanup` finishes, verify that the proof files in `evidence/` still exist on disk (*a cleanup that eats the proof fails the verification*).
3. **Zero Residue Outliving Drive**: Verify the ephemeral scratch directory is completely removed after `Cleanup`.

## 4. Seed & Maintain the Living Feature Map (`features/`)
Create `features/README.md` plus one file per user-facing feature (`features/<feature>.md`), each containing four required H2 sections:
- `## Sub-features`
- `## How to get to it (user POV)`
- `## Driving it with <harness>`
- `## Gotchas`

During maintenance passes (`/maintain-verification-skill`), spawn one read-only source reader per feature file, reconcile drift, drive every feature live, and classify findings into **Doc drift** (update the map), **Harness gap** (fix the driver and re-prove live), or **Product regression** (report and file a regression fixture).
