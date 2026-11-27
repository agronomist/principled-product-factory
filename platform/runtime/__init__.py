"""Unified Software Factory Master Runtime (`platform/runtime/`).

Connects all 11 platform modules into a single end-to-end execution loop:
Intake -> BuildTrapGate -> ContributionMarginGate -> Foreman 4-Station Pipeline ->
Real Git Worktree Sandbox -> Structural Ratchet Linter -> Decision Trail TSV Audit ->
SQLite WAL Persistence -> Factory OEE Telemetry.
"""

from platform.runtime.factory_master import (
    EndToEndFactoryReport,
    FactoryStatusSnapshot,
    SoftwareFactoryRuntime,
)

__all__ = [
    "EndToEndFactoryReport",
    "FactoryStatusSnapshot",
    "SoftwareFactoryRuntime",
]
