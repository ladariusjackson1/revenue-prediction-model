"""One command for the revenue-quality case study.

    python -m finance.run
    python -m finance.run --uci /path/to/Online\\ Retail.xlsx

The default command runs the offline fixture tests and rebuilds the static
explorer from the committed UCI snapshot. It does not download anything.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

from finance.pipeline import build
from finance.publish import sha256_file, write_demo, write_outputs
from finance.uci import read_uci_rows


def _test() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "finance/tests", "-q"],
        cwd=Path(__file__).resolve().parents[1],
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def _uci(path: Path) -> None:
    rows = read_uci_rows(path)
    work = Path(__file__).resolve().parent / "build" / "uci"
    connection = build(rows, work, source_name=path.name, sha256=sha256_file(path))
    try:
        snapshot = write_outputs(connection, path, retrieved_on=date.today().isoformat())
    finally:
        connection.close()
    demo = write_demo(snapshot)
    print(f"Wrote snapshot and {demo}")
    print(f"Net merchandise pence: {snapshot['net_pence']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--uci",
        type=Path,
        help="Path to Online Retail.xlsx. Rewrites finance/outputs and the static explorer.",
    )
    args = parser.parse_args()
    if args.uci:
        _uci(args.uci)
        return
    _test()
    snapshot_path = Path(__file__).resolve().parent / "outputs" / "uci_snapshot.json"
    if not snapshot_path.exists():
        raise SystemExit(f"Missing {snapshot_path}. Rebuild with --uci after downloading the workbook.")
    import json

    snapshot = json.loads(snapshot_path.read_text())
    demo = write_demo(snapshot)
    print(f"Fixture tests passed. Explorer rewritten at {demo}")


if __name__ == "__main__":
    main()
