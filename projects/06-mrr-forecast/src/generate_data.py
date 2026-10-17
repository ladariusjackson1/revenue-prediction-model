"""Synthetic monthly MRR series with trend + seasonality + noise."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "monthly_mrr.csv"
RNG = np.random.default_rng(3)


def generate(months: int = 48) -> pd.DataFrame:
    dates = pd.date_range("2022-01-01", periods=months, freq="MS")
    t = np.arange(months)
    base = 800 + 45 * t
    season = 120 * np.sin(2 * np.pi * t / 12)
    noise = RNG.normal(0, 60, months)
    mrr = np.clip(base + season + noise, 200, None)
    return pd.DataFrame({"month": dates.strftime("%Y-%m-%d"), "mrr": mrr.round(2)})


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")
