"""Synthetic SaaS churn dataset for Double Eagle / agency-style retainers."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "customers_churn.csv"
RNG = np.random.default_rng(42)


def generate(n: int = 2500) -> pd.DataFrame:
    tenure = RNG.integers(1, 36, n)
    mrr = RNG.choice([99, 149, 350, 550, 699], n, p=[0.15, 0.15, 0.3, 0.25, 0.15])
    tickets = RNG.poisson(lam=np.clip(3 - tenure / 18, 0.3, 4), size=n)
    late_payments = RNG.binomial(3, 0.12, n)
    usage = RNG.beta(2, 5, n) * 100
    nps = RNG.normal(35, 25, n).clip(-100, 100)
    # Higher churn when short tenure, many tickets, late pays, low usage/NPS
    logit = (
        -1.8
        - 0.06 * tenure
        + 0.002 * mrr
        + 0.35 * tickets
        + 0.55 * late_payments
        - 0.02 * usage
        - 0.015 * nps
    )
    prob = 1 / (1 + np.exp(-logit))
    churned = RNG.binomial(1, prob)
    return pd.DataFrame(
        {
            "customer_id": [f"C{i:05d}" for i in range(n)],
            "tenure_months": tenure,
            "mrr": mrr,
            "support_tickets_90d": tickets,
            "late_payments_12m": late_payments,
            "feature_usage_pct": usage.round(2),
            "nps": nps.round(1),
            "churned": churned,
        }
    )


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT} rows={len(df)} churn_rate={df.churned.mean():.3f}")
