"""Train a churn classifier; save model + metrics."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "customers_churn.csv"
MODEL = ROOT / "models" / "churn_model.joblib"
METRICS = ROOT / "models" / "metrics.json"
FEATURES = [
    "tenure_months",
    "mrr",
    "support_tickets_90d",
    "late_payments_12m",
    "feature_usage_pct",
    "nps",
]
TARGET = "churned"


def train() -> dict:
    if not DATA.exists():
        from .generate_data import generate

        DATA.parent.mkdir(parents=True, exist_ok=True)
        generate().to_csv(DATA, index=False)

    df = pd.read_csv(DATA)
    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pre = ColumnTransformer([("num", StandardScaler(), FEATURES)])
    candidates = {
        "logreg": Pipeline(
            [("pre", pre), ("clf", LogisticRegression(max_iter=1000, random_state=42))]
        ),
        "rf": Pipeline(
            [
                ("pre", pre),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=200, max_depth=6, min_samples_leaf=5, random_state=42
                    ),
                ),
            ]
        ),
        "gbm": Pipeline(
            [
                ("pre", pre),
                (
                    "clf",
                    GradientBoostingClassifier(random_state=42),
                ),
            ]
        ),
    }

    rows = []
    best_name, best_auc, best_model = None, -1.0, None
    for name, pipe in candidates.items():
        pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        auc = roc_auc_score(y_test, proba)
        metrics = {
            "model": name,
            "roc_auc": round(float(auc), 4),
            "avg_precision": round(float(average_precision_score(y_test, proba)), 4),
            "f1": round(float(f1_score(y_test, pred)), 4),
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        }
        rows.append(metrics)
        if auc > best_auc:
            best_name, best_auc, best_model = name, auc, pipe

    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": best_model, "features": FEATURES}, MODEL)
    payload = {
        "selected_model": best_name,
        "test_metrics": rows,
        "n_rows": int(len(df)),
        "churn_rate": round(float(y.mean()), 4),
    }
    METRICS.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    train()
