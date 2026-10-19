from pathlib import Path
import sys
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from train import DATA, FEATURES, MODEL, train, METRICS

def test_train():
    p = train()
    assert METRICS.exists()
    assert p["silhouette"] > 0.2

def test_saved_bundle_can_score_raw_features():
    """The clusterer is fit on scaled columns, so the dump must include that scaler."""
    train()
    bundle = joblib.load(MODEL)
    assert bundle["features"] == FEATURES
    scaler = bundle["scaler"]
    kmeans = bundle["kmeans"]
    raw = pd.read_csv(DATA)[FEATURES]
    scaled_labels = kmeans.predict(scaler.transform(raw))
    raw_labels = kmeans.predict(raw.to_numpy())
    assert len(scaled_labels) == len(raw)
    assert not (scaled_labels == raw_labels).all()
