"""RFM-style customer table for clustering."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "rfm_customers.csv"
RNG = np.random.default_rng(11)


def generate(n: int = 1200) -> pd.DataFrame:
    # Three latent segments
    seg = RNG.choice([0, 1, 2], n, p=[0.4, 0.35, 0.25])
    recency = np.where(seg == 0, RNG.integers(1, 30, n), np.where(seg == 1, RNG.integers(20, 90, n), RNG.integers(60, 180, n)))
    frequency = np.where(seg == 0, RNG.integers(8, 40, n), np.where(seg == 1, RNG.integers(3, 12, n), RNG.integers(1, 5, n)))
    monetary = np.where(seg == 0, RNG.normal(8000, 1500, n), np.where(seg == 1, RNG.normal(2500, 600, n), RNG.normal(700, 200, n)))
    monetary = np.clip(monetary, 50, None)
    return pd.DataFrame(
        {
            "customer_id": [f"R{i:05d}" for i in range(n)],
            "recency_days": recency,
            "frequency_12m": frequency,
            "monetary_12m": monetary.round(2),
            "true_segment": seg,  # for evaluation only; not used in fit
        }
    )


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")
