from __future__ import annotations
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "transactions.csv"
MODEL = ROOT / "models" / "expense_clf.joblib"
METRICS = ROOT / "models" / "metrics.json"


def train() -> dict:
    if not DATA.exists():
        from .generate_data import generate
        DATA.parent.mkdir(parents=True, exist_ok=True)
        generate().to_csv(DATA, index=False)
    df = pd.read_csv(DATA)
    Xtr, Xte, ytr, yte = train_test_split(
        df["memo"], df["category"], test_size=0.25, random_state=0, stratify=df["category"]
    )
    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=2000, random_state=0)),
        ]
    )
    pipe.fit(Xtr, ytr)
    pred = pipe.predict(Xte)
    f1 = f1_score(yte, pred, average="macro")
    payload = {
        "macro_f1": round(float(f1), 4),
        "n_rows": int(len(df)),
        "n_classes": int(df.category.nunique()),
        "report": classification_report(yte, pred, output_dict=True),
    }
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL)
    # Store lighter metrics without full report nested floats issues
    light = {k: payload[k] for k in ("macro_f1", "n_rows", "n_classes")}
    METRICS.write_text(json.dumps(light, indent=2))
    print(json.dumps(light, indent=2))
    return light


if __name__ == "__main__":
    train()
