from __future__ import annotations
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "rfm_customers.csv"
MODEL = ROOT / "models" / "kmeans.joblib"
METRICS = ROOT / "models" / "metrics.json"
FEATURES = ["recency_days", "frequency_12m", "monetary_12m"]


def train(k: int = 3) -> dict:
    if not DATA.exists():
        from .generate_data import generate
        DATA.parent.mkdir(parents=True, exist_ok=True)
        generate().to_csv(DATA, index=False)
    df = pd.read_csv(DATA)
    X = StandardScaler().fit_transform(df[FEATURES])
    km = KMeans(n_clusters=k, n_init=20, random_state=0)
    labels = km.fit_predict(X)
    payload = {
        "k": k,
        "silhouette": round(float(silhouette_score(X, labels)), 4),
        "ari_vs_latent": round(float(adjusted_rand_score(df["true_segment"], labels)), 4),
        "cluster_sizes": {str(i): int((labels == i).sum()) for i in range(k)},
        "n_rows": int(len(df)),
    }
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"kmeans": km, "features": FEATURES}, MODEL)
    METRICS.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    train()
