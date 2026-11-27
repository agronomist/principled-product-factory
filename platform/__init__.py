"""Shared multi-product platform substrate for principled-product-factory (v10).

Note: Because Python's standard library includes a built-in `platform` module,
this package re-exports all standard-library `platform` attributes (such as
`python_version`, `system`, `machine`, `uname`, etc.) so tools like `pytest`
and `hypothesis` work seamlessly when the repository root is on `sys.path`.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import sysconfig

# Load and re-export attributes from Python's stdlib `platform.py`
_stdlib_dir = sysconfig.get_path("stdlib")
_stdlib_platform_path = os.path.join(_stdlib_dir, "platform.py") if _stdlib_dir else None

if _stdlib_platform_path and os.path.exists(_stdlib_platform_path):
    _spec = importlib.util.spec_from_file_location("_stdlib_platform", _stdlib_platform_path)
    if _spec and _spec.loader:
        _stdlib_platform = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_stdlib_platform)
        for _attr in dir(_stdlib_platform):
            if not _attr.startswith("__"):
                globals()[_attr] = getattr(_stdlib_platform, _attr)

__factory_version__ = "10.0.0"
