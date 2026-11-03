#!/usr/bin/env python3
"""Write the coverage badge and markdown report from this run's coverage files."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def badge_svg(percent: str) -> str:
    value = int(percent)
    if value >= 90:
        color = "#4c1"
    elif value >= 80:
        color = "#97CA00"
    elif value >= 70:
        color = "#a4a61d"
    elif value >= 60:
        color = "#dfb317"
    else:
        color = "#e05d44"
    right = f"{percent}%"
    left_w = 62
    right_w = 18 + 7 * len(right)
    total = left_w + right_w
    left_x = left_w / 2
    right_x = left_w + right_w / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" '
        f'role="img" aria-label="coverage: {right}" data-coverage="{percent}">\n'
        f"  <title>coverage: {right}</title>\n"
        '  <linearGradient id="a" x2="0" y2="100%">\n'
        '    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>\n'
        '    <stop offset="1" stop-opacity=".1"/>\n'
        "  </linearGradient>\n"
        f'  <clipPath id="c"><rect width="{total}" height="20" rx="3" fill="#fff"/></clipPath>\n'
        '  <g clip-path="url(#c)">\n'
        f'    <rect width="{left_w}" height="20" fill="#555"/>\n'
        f'    <rect x="{left_w}" width="{right_w}" height="20" fill="{color}"/>\n'
        f'    <rect width="{total}" height="20" fill="url(#a)"/>\n'
        "  </g>\n"
        '  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">\n'
        f'    <text x="{left_x:.1f}" y="14">coverage</text>\n'
        f'    <text x="{right_x:.1f}" y="14">{right}</text>\n'
        "  </g>\n"
        "</svg>\n"
    )


def main() -> None:
    summary = json.loads((ROOT / "coverage.json").read_text())
    percent = str(summary["totals"]["percent_covered_display"])
    table = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "coverage",
            "report",
            "--data-file",
            str(ROOT / ".coverage"),
            "-m",
            "--format=markdown",
        ],
        text=True,
    )
    table = "\n".join(
        line for line in table.splitlines() if not line.endswith("empty files skipped.")
    )
    if not table.endswith("\n"):
        table += "\n"
    badge_path = ROOT / "docs" / "badges" / "coverage.svg"
    badge_path.parent.mkdir(parents=True, exist_ok=True)
    badge_path.write_text(badge_svg(percent))
    report = (
        "# Test coverage\n\n"
        "Statement coverage for all seven ML projects. "
        "`scripts/ci_ml.sh` runs data generation, training, and pytest "
        "under `coverage`, combines the seven runs, and rewrites this file "
        "and `docs/badges/coverage.svg`. "
        "GitHub Actions uploads an HTML copy (`htmlcov/`) as the "
        "`coverage-report` artifact and fails if the committed report drifts.\n\n"
        f"Measured total: **{percent}%**.\n\n"
        f"{table}"
    )
    (ROOT / "docs" / "COVERAGE.md").write_text(report)
    print(f"Wrote coverage docs at {percent}%")


if __name__ == "__main__":
    main()
