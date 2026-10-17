"""Synthetic lead scoring data for RE / PM / GC outbound."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "leads.csv"
RNG = np.random.default_rng(7)


def generate(n: int = 3000) -> pd.DataFrame:
    niche = RNG.choice(["real_estate", "property_manager", "contractor"], n, p=[0.4, 0.3, 0.3])
    source = RNG.choice(["linkedin", "referral", "cold_email", "ads", "website"], n, p=[0.25, 0.2, 0.25, 0.15, 0.15])
    employees = RNG.integers(1, 40, n)
    monthly_leads = RNG.integers(5, 400, n)
    books_behind_months = RNG.integers(0, 18, n)
    replied = RNG.binomial(1, 0.35, n)
    booked_call = replied * RNG.binomial(1, 0.55, n)
    # Close likelihood
    niche_w = {"real_estate": 0.1, "property_manager": 0.25, "contractor": 0.05}
    source_w = {"referral": 0.8, "linkedin": 0.2, "website": 0.15, "ads": 0.05, "cold_email": -0.1}
    logit = (
        -2.2
        + np.array([niche_w[x] for x in niche])
        + np.array([source_w[x] for x in source])
        + 0.03 * employees
        + 0.002 * monthly_leads
        + 0.08 * books_behind_months
        + 1.1 * replied
        + 1.4 * booked_call
    )
    won = RNG.binomial(1, 1 / (1 + np.exp(-logit)))
    return pd.DataFrame(
        {
            "lead_id": [f"L{i:05d}" for i in range(n)],
            "niche": niche,
            "source": source,
            "employees": employees,
            "monthly_inbound_leads": monthly_leads,
            "books_behind_months": books_behind_months,
            "replied": replied,
            "booked_call": booked_call,
            "won": won,
        }
    )


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT} win_rate={df.won.mean():.3f}")
