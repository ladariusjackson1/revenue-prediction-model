from __future__ import annotations
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "leads.csv"
MODEL = ROOT / "models" / "lead_score.joblib"
METRICS = ROOT / "models" / "metrics.json"
NUM = ["employees", "monthly_inbound_leads", "books_behind_months", "replied", "booked_call"]
CAT = ["niche", "source"]


def train() -> dict:
    if not DATA.exists():
        from .generate_data import generate
        DATA.parent.mkdir(parents=True, exist_ok=True)
        generate().to_csv(DATA, index=False)
    df = pd.read_csv(DATA)
    X, y = df[NUM + CAT], df["won"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
    pipe = Pipeline(
        [
            (
                "pre",
                ColumnTransformer(
                    [
                        ("num", StandardScaler(), NUM),
                        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
                    ]
                ),
            ),
            ("clf", GradientBoostingClassifier(random_state=0)),
        ]
    )
    pipe.fit(Xtr, ytr)
    proba = pipe.predict_proba(Xte)[:, 1]
    payload = {
        "roc_auc": round(float(roc_auc_score(yte, proba)), 4),
        "avg_precision": round(float(average_precision_score(yte, proba)), 4),
        "n_rows": int(len(df)),
        "win_rate": round(float(y.mean()), 4),
    }
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": pipe, "num": NUM, "cat": CAT}, MODEL)
    METRICS.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    train()
