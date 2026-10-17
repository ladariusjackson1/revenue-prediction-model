from __future__ import annotations
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "appointments.csv"
MODEL = ROOT / "models" / "noshow.joblib"
METRICS = ROOT / "models" / "metrics.json"


def train() -> dict:
    if not DATA.exists():
        from .generate_data import generate
        DATA.parent.mkdir(parents=True, exist_ok=True)
        generate().to_csv(DATA, index=False)
    df = pd.read_csv(DATA)
    num, cat = ["lead_time_hours", "weekday", "prior_noshows", "reminder_sent"], ["channel"]
    X, y = df[num + cat], df["noshow"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=1, stratify=y)
    pipe = Pipeline(
        [
            (
                "pre",
                ColumnTransformer(
                    [("n", StandardScaler(), num), ("c", OneHotEncoder(handle_unknown="ignore"), cat)]
                ),
            ),
            ("clf", RandomForestClassifier(n_estimators=200, max_depth=6, random_state=1)),
        ]
    )
    pipe.fit(Xtr, ytr)
    auc = roc_auc_score(yte, pipe.predict_proba(Xte)[:, 1])
    payload = {"roc_auc": round(float(auc), 4), "n_rows": int(len(df)), "noshow_rate": round(float(y.mean()), 4)}
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL)
    METRICS.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    train()
