from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "appointments.csv"
RNG = np.random.default_rng(99)


def generate(n: int = 2200) -> pd.DataFrame:
    lead_hours = RNG.integers(1, 240, n)
    weekday = RNG.integers(0, 7, n)
    channel = RNG.choice(["phone", "sms", "web", "referral"], n)
    prior_noshows = RNG.poisson(0.4, n)
    reminder_sent = RNG.binomial(1, 0.7, n)
    ch_w = {"referral": -0.8, "phone": -0.2, "web": 0.1, "sms": 0.0}
    logit = (
        -0.9
        + 0.004 * lead_hours
        + 0.15 * (weekday >= 5).astype(int)
        + np.array([ch_w[c] for c in channel])
        + 0.45 * prior_noshows
        - 0.7 * reminder_sent
    )
    noshow = RNG.binomial(1, 1 / (1 + np.exp(-logit)))
    return pd.DataFrame(
        {
            "appt_id": [f"A{i:05d}" for i in range(n)],
            "lead_time_hours": lead_hours,
            "weekday": weekday,
            "channel": channel,
            "prior_noshows": prior_noshows,
            "reminder_sent": reminder_sent,
            "noshow": noshow,
        }
    )


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    generate().to_csv(OUT, index=False)
    print("wrote", OUT)
