"""Known-value checks for the revenue model.

Runs under pytest, or standalone: .venv/bin/python tests/test_revenue_model.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from revenue_model import (  # noqa: E402
    APP_GROWTH_RATE,
    TRAINING_GROWTH_RATE,
    TRAINING_RECURRING_BONUS,
    MissingColumnsError,
    app_forecast,
    load_training_frame,
    require_columns,
    training_target,
)


def test_training_target_recurring():
    # 1000 * 1.08 + 200 = 1280
    assert training_target(1000.0, 1) == 1280.0


def test_training_target_non_recurring():
    # 1000 * 1.08 + 0 = 1080
    assert training_target(1000.0, 0) == 1080.0


def test_training_target_accepts_bool():
    """A bool flag must give the same answer as the equivalent integer."""
    assert training_target(1000.0, True) == training_target(1000.0, 1)
    assert training_target(1000.0, False) == training_target(1000.0, 0)


def test_training_target_vectorised():
    gross = pd.Series([1000.0, 2000.0])
    recurring = pd.Series([True, False])
    expected = pd.Series([1280.0, 2160.0])
    pd.testing.assert_series_equal(
        training_target(gross, recurring), expected, check_names=False
    )


def test_app_forecast():
    # 1000 * 1.05 = 1050
    assert app_forecast(1000.0) == 1050.0


def test_growth_rates_are_unreconciled():
    """Guards the known discrepancy so a silent change gets caught."""
    assert TRAINING_GROWTH_RATE == 1.08
    assert TRAINING_RECURRING_BONUS == 200.0
    assert APP_GROWTH_RATE == 1.05


def test_require_columns_raises_named_error():
    df = pd.DataFrame({"gross_revenue": [1.0]})
    try:
        require_columns(df, ["gross_revenue", "prev_revenue_lag1"], source="test")
    except MissingColumnsError as error:
        assert "prev_revenue_lag1" in str(error)
    else:
        raise AssertionError("expected MissingColumnsError")


def test_load_training_frame_drops_duplicates_and_nans(tmp_path=None):
    """T101 appears twice and T103 has no gross_revenue; both must go."""
    target_dir = Path(tmp_path) if tmp_path else Path(__file__).resolve().parent
    csv_path = target_dir / "_tmp_training_data.csv"
    csv_path.write_text(
        "transaction_id,gross_revenue,is_recurring,prev_revenue_lag1\n"
        "T101,4500,True,4000\n"
        "T101,4500,True,4000\n"
        "T103,,True,3000\n"
        "T104,3100,False,2900\n"
    )
    try:
        df = load_training_frame(csv_path)
        assert len(df) == 2, f"expected 2 usable rows, got {len(df)}"
        assert sorted(df["transaction_id"]) == ["T101", "T104"]
    finally:
        csv_path.unlink(missing_ok=True)


def test_end_to_end_ridge_recovers_the_formula():
    """A Ridge fit on clean data should reproduce training_target closely.

    Ridge's L2 penalty shrinks coefficients, so recovery is approximate rather
    than exact; 1% is comfortably inside that bias and still catches a genuinely
    wrong formula.
    """
    from sklearn.linear_model import Ridge

    rng = np.random.default_rng(0)
    gross = rng.uniform(1000, 15000, size=200)
    recurring = rng.integers(0, 2, size=200)
    lag = rng.uniform(1000, 15000, size=200)

    X = pd.DataFrame(
        {"gross_revenue": gross, "is_recurring": recurring, "prev_revenue_lag1": lag}
    )
    y = training_target(X["gross_revenue"], X["is_recurring"])

    model = Ridge(alpha=1.0).fit(X, y)
    prediction = model.predict(pd.DataFrame([{
        "gross_revenue": 1000.0, "is_recurring": 1, "prev_revenue_lag1": 900.0
    }]))[0]
    assert abs(prediction - 1280.0) / 1280.0 < 0.01, prediction


if __name__ == "__main__":
    failures = 0
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            try:
                function()
                print(f"PASS  {name}")
            except Exception as error:  # noqa: BLE001 - test runner
                failures += 1
                print(f"FAIL  {name}: {error}")
    print(f"\n{failures} failure(s)")
    sys.exit(1 if failures else 0)
