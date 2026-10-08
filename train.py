"""Fit the daily sales models and save the validation winner."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.forecast import (
    DISPLAY_NAMES,
    METRICS_PATH,
    MODEL_PATH,
    format_metrics_table,
    train_and_save,
)


def train() -> dict:
    print("Training daily net-sales models...")
    payload = train_and_save()
    print(
        f"Calendar days: {payload['n_calendar_days']:,} | "
        f"Modeled days: {payload['n_modeled_rows']:,}"
    )
    for name, period in payload["periods"].items():
        print(
            f"  {name:12} {period['rows']:4} days  "
            f"{period['start']} to {period['end']}"
        )
    print("\nValidation scores (fit on the training window only; used to pick the model)")
    print(format_metrics_table(payload["validation"]))
    print("\nTest scores (refit on training + validation; not used to pick the model)")
    print(format_metrics_table(payload["test"]))
    selected = payload["selected_model"]
    print(
        f"\nSelected on validation MAE: {DISPLAY_NAMES[selected]} "
        f"(trained through {payload['trained_through']})"
    )
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")
    return payload


if __name__ == "__main__":
    try:
        train()
    except (FileNotFoundError, ValueError) as error:
        raise SystemExit(f"Training aborted: {error}") from error
