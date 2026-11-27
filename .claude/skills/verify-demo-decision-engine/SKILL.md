---
name: verify-demo-decision-engine
description: >-
  Project-local verification skill for products/demo-decision-engine. Launches an
  isolated harness session, runs a read-only doctor check, drives the CLI surface
  across mapped user journeys, captures durable JSON proof artifacts, and verifies
  that evidence survives cleanup.
---

# Verify `demo-decision-engine`

This skill drives `products/demo-decision-engine/` the way a user or downstream orchestrator does—as an isolated black-box CLI subprocess—and captures durable evidence via `SubprocessCLIHarness` ([platform/harness/control_harness.py](file:///home/antigravity/principled-product-factory/platform/harness/control_harness.py)).

## Launch

Provision an isolated scratch workspace (`HARNESS_SCRATCH_DIR`) from an empty directory before driving any journey:

```bash
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-01-stage-a-discovery
```

When driven programmatically via `SubprocessCLIHarness.launch(session_id)`, an isolated scratch directory `<scratch_root>/harness-scratch-<session_id>/` is created from a clean state with `session_ready.json`.

## Doctor

Before every drive—and immediately after any failed drive—run the read-only health check (`harness.doctor()`):
- Confirms `session_ready.json` exists in the isolated scratch directory.
- Confirms `products/demo-decision-engine/harness/drive_cli.py` is present and executable.
- Attempting to invoke `harness.drive()` without a green `doctor()` raises `HarnessStateError`.

## Drive

Drive mapped journeys from [products/demo-decision-engine/features/README.md](file:///home/antigravity/principled-product-factory/products/demo-decision-engine/features/README.md):

```bash
# Journey 1: Stage A 0-to-1 discovery fast-track
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-01-stage-a-discovery

# Journey 2: Exact Contribution Margin boundary check (0.2000 == 0.2000)
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-04-exact-margin-boundary-pass

# Journey 3: 3-tier SRE double fallback to tertiary_cached_deterministic
python3 products/demo-decision-engine/harness/drive_cli.py --case-id case-10-sre-double-fallback-to-tertiary
```

## Evidence

- `harness.capture_evidence(journey_id, output)` writes deterministic JSON proof to `<evidence_root>/proof-<journey_id>.json`.
- Proof includes the exact command array, subprocess exit code (`0`), selected SRE tier, unit cost, and triage action.

## Cleanup

- `harness.cleanup()` deletes the ephemeral `<scratch_root>/harness-scratch-<session_id>/` directory so zero residue outlives the drive.
- **Evidence Survival Invariant**: `<evidence_root>/proof-<journey_id>.json` MUST remain intact after `cleanup()` completes.

## Helpers

- CLI Driver: `products/demo-decision-engine/harness/drive_cli.py`
- Feature Map Auditor (`/maintain-verification-skill`): `FeatureMapAuditor().audit_feature_map(Path("products/demo-decision-engine/features"))`
