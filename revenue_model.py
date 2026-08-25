"""Shared configuration and helpers for the revenue prediction model.

Every assumption that used to be a magic number inside train.py or app.py lives
here, so the training pipeline and the Streamlit app read from one source.
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent

# --- File locations -------------------------------------------------------
TRAINING_DATA_CSV = PROJECT_ROOT / "mock_revenue_data.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "revenue_prediction_model.pkl"
LOG_DB_PATH = PROJECT_ROOT / "app_logs.db"

# --- Model inputs ---------------------------------------------------------
FEATURE_COLUMNS = ["gross_revenue", "is_recurring", "prev_revenue_lag1"]

# --- Business assumptions -------------------------------------------------
# UNRESOLVED: train.py and app.py have always used different growth rates.
# Both are preserved exactly as they were rather than silently reconciled.
# See "anything I should double-check" in the handover notes.
TRAINING_GROWTH_RATE = 1.08      # train.py target: 8% growth on gross revenue
TRAINING_RECURRING_BONUS = 200.0  # train.py target: flat premium for recurring
APP_GROWTH_RATE = 1.05           # app.py on-screen forecast: 5% growth

# --- Model hyperparameters ------------------------------------------------
RIDGE_ALPHA = 1.0
MIN_ROWS_TO_RETRAIN = 3  # minimum verified rows before the app refits


class MissingColumnsError(ValueError):
    """Raised when a dataframe is missing columns the pipeline requires."""


def require_columns(df: pd.DataFrame, columns, source: str) -> None:
    """Fail with an actionable message instead of a raw pandas KeyError."""
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise MissingColumnsError(
            f"{source} is missing required column(s): {', '.join(missing)}. "
            f"Found: {', '.join(map(str, df.columns))}"
        )


def training_target(gross_revenue, is_recurring):
    """Target revenue used to fit the model (train.py's original formula)."""
    # is_recurring may arrive as bool, 0/1 int, or a bool Series; cast so the
    # arithmetic is identical in every case.
    recurring_flag = pd.to_numeric(is_recurring, errors="coerce")
    return gross_revenue * TRAINING_GROWTH_RATE + recurring_flag * TRAINING_RECURRING_BONUS


def app_forecast(gross_revenue):
    """Forecast shown in the Streamlit UI (app.py's original formula)."""
    return gross_revenue * APP_GROWTH_RATE


def load_training_frame(csv_path=TRAINING_DATA_CSV) -> pd.DataFrame:
    """Load the training CSV, drop exact duplicates, and validate columns.

    Deduplication was documented in the README but never actually performed;
    mock_revenue_data.csv contains T101 twice.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Could not find {csv_path}. Make sure it is in your project folder!"
        )

    df = pd.read_csv(csv_path)
    df = df.drop_duplicates()
    require_columns(df, FEATURE_COLUMNS, source=str(csv_path))
    return df.dropna(subset=FEATURE_COLUMNS)
