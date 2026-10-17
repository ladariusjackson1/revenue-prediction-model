from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from generate_data import generate
from train import train, METRICS


def test_generate_shape():
    df = generate(200)
    assert len(df) == 200
    assert set(df["churned"].unique()).issubset({0, 1})


def test_train_writes_metrics():
    payload = train()
    assert METRICS.exists()
    assert payload["selected_model"] in {"logreg", "rf", "gbm"}
    assert payload["test_metrics"]
