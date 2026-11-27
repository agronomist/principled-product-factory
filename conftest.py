"""Pytest bootstrap to bind the repository's `platform/` package over stdlib `platform`.

Because `pytest` imports Python's standard library `platform` module during interpreter
startup (before adding `rootdir` to `sys.path`), `sys.modules['platform']` initially points
to the single-file stdlib module rather than the repository's `platform/` package directory.
Our `platform/__init__.py` re-exports 100% of stdlib `platform` symbols while making
`platform.metering`, `platform.telemetry`, `platform.sre`, `platform.orchestrator`, and
`platform.evals` importable as subpackages.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
_PLATFORM_INIT = _REPO_ROOT / "platform" / "__init__.py"

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_existing = sys.modules.get("platform")
if _existing is None or not hasattr(_existing, "__path__"):
    _spec = importlib.util.spec_from_file_location(
        "platform",
        _PLATFORM_INIT,
        submodule_search_locations=[str(_REPO_ROOT / "platform")],
    )
    if _spec and _spec.loader:
        _pkg = importlib.util.module_from_spec(_spec)
        sys.modules["platform"] = _pkg
        _spec.loader.exec_module(_pkg)
