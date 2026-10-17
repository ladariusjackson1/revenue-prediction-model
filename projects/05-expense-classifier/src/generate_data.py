"""Synthetic bank memo lines for chart-of-accounts classification."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "transactions.csv"
RNG = np.random.default_rng(21)

TEMPLATES = {
    "Advertising": [
        "FACEBOOK ADS {n}",
        "GOOGLE ADS {n}",
        "META BUSINESS {n}",
        "LINKEDIN CAMPAIGN {n}",
    ],
    "Software": [
        "QUICKBOOKS ONLINE {n}",
        "GOHIGHLEVEL SUB {n}",
        "OPENAI API {n}",
        "GITHUB TEAM {n}",
        "SLACK INC {n}",
    ],
    "Fuel": [
        "SHELL OIL {n}",
        "CHEVRON {n}",
        "EXXONMOBIL {n}",
    ],
    "Office Supplies": [
        "STAPLES {n}",
        "OFFICE DEPOT {n}",
        "AMAZON OFFICE {n}",
    ],
    "Contractor Labor": [
        "SUBCONTRACTOR PAY {n}",
        "HIRED LABOR CREW {n}",
        "DAY LABOR PAYROLL {n}",
    ],
    "Rent": [
        "OXFORD OFFICE RENT {n}",
        "WAREHOUSE LEASE {n}",
    ],
}


def generate(n: int = 2000) -> pd.DataFrame:
    cats = list(TEMPLATES)
    rows = []
    for i in range(n):
        cat = RNG.choice(cats)
        tmpl = RNG.choice(TEMPLATES[cat])
        memo = tmpl.format(n=RNG.integers(1000, 9999))
        # noise tokens
        if RNG.random() < 0.2:
            memo += " CONF " + str(RNG.integers(10000, 99999))
        amount = float(np.round(RNG.uniform(15, 2500), 2))
        rows.append({"txn_id": f"T{i:05d}", "memo": memo, "amount": amount, "category": cat})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT} cats={df.category.nunique()}")
