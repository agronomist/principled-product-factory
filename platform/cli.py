"""Unified CLI Front Door for `principled-product-factory` (`python3 -m platform.cli`).

Commands:
- `python3 -m platform.cli status`: Inspect SQLite WAL ledger, decision trail rows, and AST structural ratchet.
- `python3 -m platform.cli intake --id <id> --title <title> --body <body>`: Run an item end-to-end through
  Margin Guard, Build Trap Guard, Foreman 4-Stations, a real Git Worktree checkout, and TSV Audit Trail.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from platform.foreman.stations import CallerPrincipalClass, WorkItemIntake
from platform.metering.margin_guard import UnitEconomicsInput
from platform.runtime.factory_master import SoftwareFactoryRuntime


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="principled-product-factory",
        description="Unified CLI for the principled-product-factory software factory.",
    )
    parser.add_argument(
        "--state-dir",
        default=None,
        help="Directory for SQLite WAL state and decisions.tsv (defaults to a temp state dir).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Print live factory SQLite WAL and AST structural ratchet status.")

    intake_p = sub.add_parser(
        "intake",
        help="Run a work item through Foreman stations and a real Git worktree sandbox.",
    )
    intake_p.add_argument("--id", default="issue-501", help="Work item ID.")
    intake_p.add_argument(
        "--title",
        default="Fix duplicate reset email on webhook retry",
        help="Work item title.",
    )
    intake_p.add_argument(
        "--body",
        default="Ensure SHA-256 idempotency key deduplicates webhook retries.",
        help="Work item description body.",
    )

    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    state_dir = (
        Path(args.state_dir)
        if args.state_dir
        else Path(tempfile.mkdtemp(prefix="factory-cli-state-"))
    )

    runtime = SoftwareFactoryRuntime(repo_root=repo_root, state_dir=state_dir)

    if args.command == "status":
        snap = runtime.status_snapshot()
        print(snap.model_dump_json(indent=2))
        return 0

    if args.command == "intake":
        report = runtime.process_work_item(
            WorkItemIntake(
                item_id=args.id,
                title=args.title,
                body=args.body,
                caller_class=CallerPrincipalClass.UNATTENDED_AUTONOMOUS,
            ),
            UnitEconomicsInput(
                transaction_id=f"tx-{args.id}",
                unit_revenue=0.80,
                inference_cost=0.10,
                data_api_cost=0.04,
                hitl_prob=0.05,
                human_review_cost=1.00,
                infra_cost=0.03,
                min_margin=0.25,
            ),
        )
        print(json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
