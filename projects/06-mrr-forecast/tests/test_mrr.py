from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from train import train, METRICS

def test_train():
    p = train()
    assert METRICS.exists()
    assert p["selected_model"]
