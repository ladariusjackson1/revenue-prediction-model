from __future__ import annotations
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "monthly_mrr.csv"
MODEL = ROOT / "models" / "mrr_model.joblib"
METRICS = ROOT / "models" / "metrics.json"


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month_dt"] = pd.to_datetime(out["month"])
    out = out.sort_values("month_dt")
    out["lag_1"] = out["mrr"].shift(1)
    out["lag_3"] = out["mrr"].shift(3)
    out["lag_12"] = out["mrr"].shift(12)
    out["roll_3"] = out["mrr"].shift(1).rolling(3).mean()
    out["month_num"] = out["month_dt"].dt.month
    return out.dropna().reset_index(drop=True)


def train() -> dict:
    if not DATA.exists():
        from .generate_data import generate
        DATA.parent.mkdir(parents=True, exist_ok=True)
        generate().to_csv(DATA, index=False)
    raw = pd.read_csv(DATA)
    feat = make_features(raw)
    cols = ["lag_1", "lag_3", "lag_12", "roll_3", "month_num"]
    # time split: last 8 months test
    train_df, test_df = feat.iloc[:-8], feat.iloc[-8:]
    Xtr, ytr = train_df[cols], train_df["mrr"]
    Xte, yte = test_df[cols], test_df["mrr"]

    models = {
        "seasonal_naive_lag12": None,
        "ridge": Ridge(alpha=1.0),
        "random_forest": RandomForestRegressor(
            n_estimators=200, max_depth=5, random_state=0
        ),
    }
    scores = []
    best_name, best_mae, best_est = None, 1e18, None
    for name, est in models.items():
        if name == "seasonal_naive_lag12":
            pred = Xte["lag_12"].values
        else:
            est.fit(Xtr, ytr)
            pred = est.predict(Xte)
        mae = mean_absolute_error(yte, pred)
        scores.append(
            {
                "model": name,
                "mae": round(float(mae), 2),
                "r2": round(float(r2_score(yte, pred)), 4),
            }
        )
        if mae < best_mae:
            best_name, best_mae, best_est = name, mae, est

    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": best_est, "features": cols, "name": best_name}, MODEL)
    payload = {"selected_model": best_name, "test_scores": scores, "n_rows": int(len(feat))}
    METRICS.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    train()
