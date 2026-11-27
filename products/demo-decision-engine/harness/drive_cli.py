"""Live CLI Harness Driver for `products/demo-decision-engine`.

Allows `SubprocessCLIHarness` (`/create-verification-skill`) to drive the real product
surface in an isolated subprocess and capture deterministic JSON evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# Ensure repository root and platform package are bound before imports
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_existing_plat = sys.modules.get("platform")
if _existing_plat is None or not hasattr(_existing_plat, "__path__"):
    _spec = importlib.util.spec_from_file_location(
        "platform",
        _REPO_ROOT / "platform" / "__init__.py",
        submodule_search_locations=[str(_REPO_ROOT / "platform")],
    )
    if _spec and _spec.loader:
        _pkg = importlib.util.module_from_spec(_spec)
        sys.modules["platform"] = _pkg
        _spec.loader.exec_module(_pkg)

from platform.evals.runner import load_golden_cases_jsonl  # noqa: E402
from products.demo_decision_engine.skills.decision_triage import (  # noqa: E402
    evaluate_golden_case_with_dag,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Drive demo-decision-engine CLI journey.")
    parser.add_argument(
        "--case-id",
        default="case-01-stage-a-discovery",
        help="Golden case ID from evals/golden_cases.jsonl to drive.",
    )
    args = parser.parse_args(argv)

    product_root = Path(__file__).resolve().parents[1]
    golden_path = product_root / "evals" / "golden_cases.jsonl"
    dag_path = product_root / "workflows" / "factory_dag.yaml"

    cases = load_golden_cases_jsonl(golden_path)
    matched = [c for c in cases if c.case_id == args.case_id]
    if not matched:
        print(json.dumps({"error": f"Unknown case_id: {args.case_id}"}), file=sys.stderr)
        return 2

    outcome = evaluate_golden_case_with_dag(matched[0], dag_path=dag_path)
    print(json.dumps(outcome, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
