"""Daily net-sales forecasting without same-day leakage.

The target on day t is that day's net merchandise sales. Every sales feature
is taken from days before t. Calendar fields (weekday) are known before the
day begins. Models are fit on earlier days and scored on later days.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "daily_revenue.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "revenue_model.joblib"
METRICS_PATH = PROJECT_ROOT / "models" / "metrics.json"

TARGET_COLUMN = "revenue"
NUMERIC_FEATURES = [
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_mean_7",
    "rolling_mean_28",
]
CATEGORICAL_FEATURES = ["day_of_week"]
FEATURE_COLUMNS = [*NUMERIC_FEATURES, *CATEGORICAL_FEATURES]

# rolling_mean_28 needs 28 completed days before the forecast date.
HISTORY_DAYS = 28
VALID_FRACTION = 0.20
TEST_FRACTION = 0.20

# The UCI extract stops at 12:50 on its last calendar day. A full trading
# day in this file runs into the afternoon or evening, so a last timestamp
# before 16:00 is treated as a partial day and left out of the series.
PARTIAL_DAY_CUTOFF_HOUR = 16

RIDGE_ALPHA = 1.0
FOREST_TREES = 300
FOREST_MAX_DEPTH = 6
FOREST_MIN_LEAF = 5
RANDOM_STATE = 0

# Codes that are not unit merchandise: postage, fees, discounts, samples,
# manual adjustments, and gift vouchers. Product codes in this file start
# with a digit (for example 85123A). A handful of letter-prefixed goods
# (DCGS...) are excluded with them; their total is a few hundred pounds.
NON_PRODUCT_CODE_PATTERN = r"^\d"

DISPLAY_NAMES = {
    "seasonal_naive": "Seasonal naive",
    "ridge": "Ridge",
    "random_forest": "Random forest",
}
# On a validation-MAE tie, prefer the simpler model.
MODEL_PREFERENCE = {"seasonal_naive": 0, "ridge": 1, "random_forest": 2}


class MissingColumnsError(ValueError):
    """Raised when a table is missing columns the pipeline requires."""


def require_columns(df: pd.DataFrame, columns, source: str) -> None:
    """Fail with an actionable message instead of a raw pandas KeyError."""
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise MissingColumnsError(
            f"{source} is missing required column(s): {', '.join(missing)}. "
            f"Found: {', '.join(map(str, df.columns))}"
        )


def merchandise_lines(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return one row per kept invoice line, with columns date and line.

    line = Quantity * UnitPrice. Negative quantities (returns and
    cancellations) reduce the day's net sales. Non-positive prices and
    non-product stock codes are dropped.
    """
    require_columns(
        transactions,
        ["StockCode", "Quantity", "InvoiceDate", "UnitPrice"],
        source="transactions",
    )
    frame = transactions.copy()
    frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce")
    frame = frame.dropna(subset=["InvoiceDate"])
    if frame.empty:
        raise ValueError("No invoice rows with a usable InvoiceDate.")

    last_timestamp = frame["InvoiceDate"].max()
    if last_timestamp.hour < PARTIAL_DAY_CUTOFF_HOUR:
        last_day = last_timestamp.normalize()
        frame = frame.loc[frame["InvoiceDate"] < last_day]
    if frame.empty:
        raise ValueError("No invoice rows remain after dropping a partial final day.")

    codes = frame["StockCode"].astype(str).str.strip()
    prices = pd.to_numeric(frame["UnitPrice"], errors="coerce")
    quantities = pd.to_numeric(frame["Quantity"], errors="coerce")
    keep = (
        codes.str.match(NON_PRODUCT_CODE_PATTERN, na=False)
        & prices.notna()
        & quantities.notna()
        & (prices > 0)
    )
    kept = frame.loc[keep].copy()
    if kept.empty:
        raise ValueError("No merchandise lines remain after cleaning.")

    kept["date"] = kept["InvoiceDate"].dt.normalize()
    kept["line"] = quantities.loc[kept.index] * prices.loc[kept.index]
    return kept[["date", "line"]]


def lines_to_daily(lines: pd.DataFrame) -> pd.DataFrame:
    """Sum line amounts onto a complete daily calendar. Missing days are 0."""
    require_columns(lines, ["date", "line"], source="merchandise lines")
    if lines.empty:
        raise ValueError("No merchandise lines to aggregate.")
    totals = lines.groupby("date")["line"].sum()
    totals.index = pd.DatetimeIndex(totals.index, name="date")
    totals = totals.asfreq("D", fill_value=0.0)
    daily = totals.rename("revenue").reset_index()
    daily["revenue"] = daily["revenue"].astype(float).round(2)
    return daily


def daily_net_sales(transactions: pd.DataFrame) -> pd.DataFrame:
    """Aggregate invoice lines to a complete daily net-sales series."""
    return lines_to_daily(merchandise_lines(transactions))


def write_daily_revenue(daily: pd.DataFrame, path: Path = DATA_PATH) -> Path:
    """Write date,revenue with stable formatting."""
    require_columns(daily, ["date", "revenue"], source="daily revenue")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(daily["date"]).dt.strftime("%Y-%m-%d"),
            "revenue": daily["revenue"].astype(float),
        }
    )
    out.to_csv(path, index=False, lineterminator="\n", float_format="%.2f")
    return path


def load_daily_revenue(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the committed daily series. Reject gaps and duplicate dates."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. From the repo root, run "
            "python scripts/build_daily_revenue.py"
        )
    frame = pd.read_csv(path)
    require_columns(frame, ["date", "revenue"], source=str(path))
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
    frame["revenue"] = pd.to_numeric(frame["revenue"], errors="coerce")
    if frame["date"].isna().any() or frame["revenue"].isna().any():
        raise ValueError(f"{path} has unparseable date or revenue values.")
    if frame["date"].duplicated().any():
        raise ValueError(f"{path} has duplicate dates.")
    frame = frame.sort_values("date").reset_index(drop=True)
    gaps = frame["date"].diff().dt.days.iloc[1:]
    if (gaps != 1).any():
        raise ValueError(f"{path} is not a complete daily calendar.")
    return frame[["date", "revenue"]]


def add_features(daily: pd.DataFrame) -> pd.DataFrame:
    """Build lagged features. Rows without a full 28-day history are dropped.

    rolling means are shifted by one day, so day t does not enter its own
    features. day_of_week is the weekday of the day being forecast.
    """
    require_columns(daily, ["date", "revenue"], source="daily revenue")
    frame = daily[["date", "revenue"]].copy()
    frame["date"] = pd.to_datetime(frame["date"]).dt.normalize()
    frame["revenue"] = pd.to_numeric(frame["revenue"], errors="coerce")
    if frame.empty or frame["date"].isna().any():
        raise ValueError("Every row needs a date.")
    frame = frame.sort_values("date").reset_index(drop=True)
    if frame["date"].duplicated().any():
        raise ValueError("daily revenue has duplicate dates.")
    # The last row may be a forecast day whose sales are not known yet.
    # Every earlier row needs a real revenue, or the lags would be wrong.
    if frame["revenue"].iloc[:-1].isna().any():
        raise ValueError("Every day except a final forecast row needs a revenue.")

    revenue = frame["revenue"]
    frame["lag_1"] = revenue.shift(1)
    frame["lag_7"] = revenue.shift(7)
    frame["lag_14"] = revenue.shift(14)
    # shift(1) drops today before the window is applied.
    frame["rolling_mean_7"] = revenue.shift(1).rolling(7, min_periods=7).mean()
    frame["rolling_mean_28"] = revenue.shift(1).rolling(28, min_periods=28).mean()
    frame["day_of_week"] = frame["date"].dt.dayofweek.astype(int)

    featured = frame.dropna(subset=FEATURE_COLUMNS).reset_index(drop=True)
    return featured[["date", TARGET_COLUMN, *FEATURE_COLUMNS]]


def features_from_history(revenues, forecast_date) -> pd.DataFrame:
    """Feature row for forecast_date given the daily sales that precede it.

    `revenues` is oldest-first and must cover the 28 calendar days immediately
    before `forecast_date`. Extra leading values are ignored.
    """
    values = [float(value) for value in revenues]
    if len(values) < HISTORY_DAYS:
        raise ValueError(
            f"Need at least {HISTORY_DAYS} daily sales amounts before "
            f"{pd.Timestamp(forecast_date).date()}."
        )
    values = values[-HISTORY_DAYS:]
    forecast_ts = pd.Timestamp(forecast_date).normalize()
    history_dates = pd.date_range(
        end=forecast_ts - pd.Timedelta(days=1),
        periods=HISTORY_DAYS,
        freq="D",
    )
    frame = pd.DataFrame(
        {
            "date": list(history_dates) + [forecast_ts],
            "revenue": values + [np.nan],
        }
    )
    featured = add_features(frame)
    row = featured.loc[featured["date"] == forecast_ts]
    if row.empty:
        raise ValueError("Could not build a feature row from that history.")
    return row.reset_index(drop=True)


def chronological_split(
    featured: pd.DataFrame,
    valid_fraction: float = VALID_FRACTION,
    test_fraction: float = TEST_FRACTION,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split by time into train, validation, and test. No shuffling."""
    if not featured["date"].is_monotonic_increasing or not featured["date"].is_unique:
        raise ValueError("Feature rows must be sorted by unique dates.")
    n_rows = len(featured)
    test_n = int(round(n_rows * test_fraction))
    valid_n = int(round(n_rows * valid_fraction))
    train_n = n_rows - test_n - valid_n
    if min(train_n, valid_n, test_n) < 1:
        raise ValueError(
            f"Not enough rows ({n_rows}) for a {valid_fraction:.0%} validation "
            f"and {test_fraction:.0%} test split."
        )
    train = featured.iloc[:train_n].reset_index(drop=True)
    valid = featured.iloc[train_n : train_n + valid_n].reset_index(drop=True)
    test = featured.iloc[train_n + valid_n :].reset_index(drop=True)
    return train, valid, test


class SeasonalNaive:
    """Predict each day with sales from seven days earlier (lag_7)."""

    def fit(self, X, y=None):
        require_columns(X, ["lag_7"], source="seasonal naive")
        return self

    def predict(self, X):
        require_columns(X, ["lag_7"], source="seasonal naive")
        return X["lag_7"].to_numpy(dtype=float)


def make_ridge() -> Pipeline:
    """Ridge on scaled lags. Weekday is one-hot. Scaler fits inside the pipeline."""
    preprocess = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            (
                "weekday",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    return Pipeline(
        [
            ("preprocess", preprocess),
            ("model", Ridge(alpha=RIDGE_ALPHA)),
        ]
    )


def make_random_forest() -> RandomForestRegressor:
    """Small forest. Depth and leaf size are fixed, not searched on the test set."""
    return RandomForestRegressor(
        n_estimators=FOREST_TREES,
        max_depth=FOREST_MAX_DEPTH,
        min_samples_leaf=FOREST_MIN_LEAF,
        max_features=1.0,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )


MODEL_BUILDERS = {
    "seasonal_naive": SeasonalNaive,
    "ridge": make_ridge,
    "random_forest": make_random_forest,
}


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    """Held-out error in pounds, plus R². Rounded so reruns match the README."""
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 2),
        "rmse": round(float(root_mean_squared_error(y_true, y_pred)), 2),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def _fit(name: str, train_df: pd.DataFrame):
    model = MODEL_BUILDERS[name]()
    model.fit(train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN])
    return model


def _score(model, frame: pd.DataFrame) -> dict[str, float]:
    predictions = model.predict(frame[FEATURE_COLUMNS])
    return regression_metrics(frame[TARGET_COLUMN], predictions)


def _period(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)),
        "start": frame["date"].min().strftime("%Y-%m-%d"),
        "end": frame["date"].max().strftime("%Y-%m-%d"),
    }


def run_evaluation(featured: pd.DataFrame) -> dict:
    """Select a model on validation MAE, then score every model on the later test window.

    Validation scores come from models fit on the training window only.
    Test scores come from models refit on training plus validation. The
    saved model is the validation winner, refit the same way. Test rows
    are not used to choose the model or to fit it.
    """
    train, valid, test = chronological_split(featured)
    validation_scores = {
        name: _score(_fit(name, train), valid) for name in MODEL_BUILDERS
    }
    selected = min(
        validation_scores,
        key=lambda name: (validation_scores[name]["mae"], MODEL_PREFERENCE[name]),
    )
    pre_test = pd.concat([train, valid], ignore_index=True)
    fitted = {name: _fit(name, pre_test) for name in MODEL_BUILDERS}
    test_scores = {name: _score(model, test) for name, model in fitted.items()}
    return {
        "selected_model": selected,
        "validation": validation_scores,
        "test": test_scores,
        "periods": {
            "train": _period(train),
            "validation": _period(valid),
            "test": _period(test),
        },
        "frames": {"train": train, "validation": valid, "test": test},
        "fitted_on_pre_test": fitted,
        "trained_through": pre_test["date"].max().strftime("%Y-%m-%d"),
    }


def holdout_predictions(result: dict) -> pd.DataFrame:
    """Actual test-window sales and each model's forecast."""
    test = result["frames"]["test"]
    table = pd.DataFrame(
        {
            "date": test["date"].to_numpy(),
            "actual": test[TARGET_COLUMN].to_numpy(),
        }
    )
    for name, model in result["fitted_on_pre_test"].items():
        table[name] = model.predict(test[FEATURE_COLUMNS])
    return table


def metrics_payload(result: dict, n_calendar_days: int) -> dict:
    """JSON-ready evaluation record. Omits data frames and fitted estimators."""
    return {
        "target": TARGET_COLUMN,
        "features": list(FEATURE_COLUMNS),
        "n_calendar_days": int(n_calendar_days),
        "n_modeled_rows": int(sum(result["periods"][key]["rows"] for key in result["periods"])),
        "selection_rule": (
            "Lowest validation MAE. Ties prefer the simpler model "
            "(seasonal naive, then ridge, then random forest). "
            "Test rows are not used for selection or fitting."
        ),
        "selected_model": result["selected_model"],
        "trained_through": result["trained_through"],
        "periods": result["periods"],
        "validation": result["validation"],
        "test": result["test"],
        "hyperparameters": {
            "ridge_alpha": RIDGE_ALPHA,
            "random_forest": {
                "n_estimators": FOREST_TREES,
                "max_depth": FOREST_MAX_DEPTH,
                "min_samples_leaf": FOREST_MIN_LEAF,
                "max_features": 1.0,
                "random_state": RANDOM_STATE,
            },
        },
    }


def format_metrics_table(scores: dict) -> str:
    """Markdown table of MAE, RMSE, and R²."""
    lines = [
        "| Model | MAE (GBP) | RMSE (GBP) | R² |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, values in scores.items():
        lines.append(
            f"| {DISPLAY_NAMES[name]} | {values['mae']:,.2f} | "
            f"{values['rmse']:,.2f} | {values['r2']:.4f} |"
        )
    return "\n".join(lines)


def train_and_save(
    data_path: Path = DATA_PATH,
    model_path: Path = MODEL_PATH,
    metrics_path: Path = METRICS_PATH,
) -> dict:
    """Fit on the daily series, write metrics JSON, and save the selected model."""
    daily = load_daily_revenue(data_path)
    featured = add_features(daily)
    result = run_evaluation(featured)
    payload = metrics_payload(result, n_calendar_days=len(daily))

    metrics_path = Path(metrics_path)
    model_path = Path(model_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(payload, indent=2) + "\n")
    joblib.dump(
        {
            "model_name": result["selected_model"],
            "model": result["fitted_on_pre_test"][result["selected_model"]],
            "feature_columns": list(FEATURE_COLUMNS),
            "trained_through": result["trained_through"],
        },
        model_path,
    )
    payload["model_path"] = str(model_path)
    payload["metrics_path"] = str(metrics_path)
    return payload


def load_model(path: Path = MODEL_PATH) -> dict:
    """Load the joblib payload written by train_and_save."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. From the repo root, run python train.py"
        )
    payload = joblib.load(path)
    if not isinstance(payload, dict) or "model" not in payload:
        raise ValueError(f"{path} is not a revenue model payload.")
    return payload


def predict_revenue(model, revenues, forecast_date) -> float:
    """Point forecast for one date from prior daily sales."""
    row = features_from_history(revenues, forecast_date)
    prediction = model.predict(row[FEATURE_COLUMNS])
    return float(prediction[0])
