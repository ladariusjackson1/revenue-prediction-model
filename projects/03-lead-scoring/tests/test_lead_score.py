from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from generate_data import generate
from train import train, METRICS

def test_generate():
    assert len(generate(100)) == 100

def test_train():
    p = train()
    assert METRICS.exists()
    assert p["roc_auc"] > 0.5
