"""Checks for the daily sales forecast.

The model must not see same-day sales, the holdout must be later in time than
the fit window, and the seasonal naive forecast must be last week's sales.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.forecast import (
    FEATURE_COLUMNS,
    HISTORY_DAYS,
    METRICS_PATH,
    MODEL_PATH,
    MODEL_PREFERENCE,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    MissingColumnsError,
    add_features,
    chronological_split,
    daily_net_sales,
    features_from_history,
    holdout_predictions,
    load_daily_revenue,
    load_model,
    make_ridge,
    predict_revenue,
    require_columns,
    run_evaluation,
    train_and_save,
)


def _invoices(*rows):
    return pd.DataFrame(rows)


def test_require_columns_names_the_missing_field():
    frame = pd.DataFrame({"revenue": [1.0]})
    with pytest.raises(MissingColumnsError, match="date"):
        require_columns(frame, ["date", "revenue"], source="test")


def test_daily_net_sales_nets_returns_drops_fees_and_partial_last_day():
    invoices = _invoices(
        {"StockCode": "11111", "Quantity": 2, "InvoiceDate": "2020-01-01 10:00", "UnitPrice": 5.0},
        {"StockCode": "11111", "Quantity": -1, "InvoiceDate": "2020-01-01 12:00", "UnitPrice": 5.0},
        {"StockCode": "POST", "Quantity": 1, "InvoiceDate": "2020-01-01 12:00", "UnitPrice": 100.0},
        {"StockCode": "22222", "Quantity": 4, "InvoiceDate": "2020-01-01 15:00", "UnitPrice": 0.0},
        {"StockCode": "85123A", "Quantity": 1, "InvoiceDate": "2020-01-02 18:30", "UnitPrice": 2.5},
        {"StockCode": "33333", "Quantity": 10, "InvoiceDate": "2020-01-03 12:00", "UnitPrice": 9.0},
    )
    daily = daily_net_sales(invoices)
    assert list(daily["date"].dt.strftime("%Y-%m-%d")) == ["2020-01-01", "2020-01-02"]
    assert daily["revenue"].tolist() == [5.0, 2.5]


def test_daily_net_sales_fills_missing_calendar_days_with_zero():
    invoices = _invoices(
        {"StockCode": "11111", "Quantity": 1, "InvoiceDate": "2020-01-01 18:00", "UnitPrice": 10.0},
        {"StockCode": "11111", "Quantity": 2, "InvoiceDate": "2020-01-03 18:00", "UnitPrice": 4.0},
    )
    daily = daily_net_sales(invoices)
    assert daily["revenue"].tolist() == [10.0, 0.0, 8.0]


def test_public_series_is_a_complete_daily_calendar():
    daily = load_daily_revenue()
    assert len(daily) >= 300
    assert daily["date"].min() == pd.Timestamp("2010-12-01")
    assert daily["date"].max() == pd.Timestamp("2011-12-08")
    assert daily["date"].is_unique
    assert (daily["date"].diff().dt.days.iloc[1:] == 1).all()
    # This retailer recorded no Saturday invoices in the extract.
    saturdays = daily.loc[daily["date"].dt.dayofweek == 5, "revenue"]
    assert (saturdays == 0).all()
    assert saturdays.shape[0] > 40


def test_features_use_only_earlier_days():
    daily = load_daily_revenue()
    featured = add_features(daily)
    assert TARGET_COLUMN not in FEATURE_COLUMNS
    assert featured["date"].is_monotonic_increasing
    # lag_1 is the previous modeled day's sales, and those days are consecutive.
    pd.testing.assert_series_equal(
        featured["lag_1"].iloc[1:].reset_index(drop=True),
        featured["revenue"].iloc[:-1].reset_index(drop=True),
        check_names=False,
    )
    by_date = daily.set_index("date")["revenue"]
    expected_lag7 = featured["date"].map(lambda day: by_date.loc[day - pd.Timedelta(days=7)])
    pd.testing.assert_series_equal(
        featured["lag_7"].reset_index(drop=True),
        expected_lag7.reset_index(drop=True),
        check_names=False,
    )
    expected_roll = featured["date"].map(
        lambda day: by_date.loc[day - pd.Timedelta(days=7) : day - pd.Timedelta(days=1)].mean()
    )
    pd.testing.assert_series_equal(
        featured["rolling_mean_7"].reset_index(drop=True),
        expected_roll.reset_index(drop=True),
        check_names=False,
        atol=1e-8,
        rtol=0,
    )


def test_changing_a_day_does_not_change_earlier_features():
    daily = load_daily_revenue()
    original = add_features(daily).set_index("date")
    bumped = daily.copy()
    change_at = bumped.index[len(bumped) // 2]
    change_date = bumped.loc[change_at, "date"]
    bumped.loc[change_at, "revenue"] = bumped.loc[change_at, "revenue"] + 5000
    updated = add_features(bumped).set_index("date")
    earlier = original.index < change_date
    pd.testing.assert_frame_equal(
        original.loc[earlier, FEATURE_COLUMNS],
        updated.loc[earlier, FEATURE_COLUMNS],
    )


def test_same_day_sales_are_not_in_the_feature_row():
    daily = load_daily_revenue()
    featured = add_features(daily)
    planted = daily.copy()
    planted.loc[planted.index[-1], "revenue"] = -12345.67
    replanted = add_features(planted)
    pd.testing.assert_frame_equal(
        featured[FEATURE_COLUMNS],
        replanted[FEATURE_COLUMNS],
    )
    assert featured["revenue"].iloc[-1] != replanted["revenue"].iloc[-1]


def test_history_builder_matches_the_training_matrix():
    daily = load_daily_revenue()
    featured = add_features(daily)
    row = featured.iloc[40]
    prior = daily.loc[daily["date"] < row["date"]].tail(HISTORY_DAYS)
    built = features_from_history(prior["revenue"], row["date"])
    pd.testing.assert_series_equal(
        built.iloc[0][FEATURE_COLUMNS].reset_index(drop=True),
        row[FEATURE_COLUMNS].reset_index(drop=True),
        check_names=False,
        atol=1e-8,
        rtol=0,
    )


def test_split_is_chronological_and_covers_every_modeled_day():
    featured = add_features(load_daily_revenue())
    train, valid, test = chronological_split(featured)
    assert len(train) + len(valid) + len(test) == len(featured)
    assert train["date"].max() < valid["date"].min()
    assert valid["date"].max() < test["date"].min()
    assert set(train["date"]).isdisjoint(set(test["date"]))


def test_seasonal_naive_is_last_week_and_selection_uses_validation_only():
    featured = add_features(load_daily_revenue())
    result = run_evaluation(featured)
    predictions = holdout_predictions(result)
    np.testing.assert_allclose(
        predictions["seasonal_naive"],
        result["frames"]["test"]["lag_7"],
    )
    winner = min(
        result["validation"],
        key=lambda name: (result["validation"][name]["mae"], MODEL_PREFERENCE[name]),
    )
    assert result["selected_model"] == winner
    assert result["trained_through"] == result["periods"]["validation"]["end"]
    assert result["trained_through"] < result["periods"]["test"]["start"]
    for split_name in ("validation", "test"):
        for scores in result[split_name].values():
            assert scores["mae"] > 0
            assert scores["rmse"] >= scores["mae"]


def test_ridge_scaler_is_fit_on_the_pre_test_window_only():
    featured = add_features(load_daily_revenue())
    result = run_evaluation(featured)
    ridge = result["fitted_on_pre_test"]["ridge"]
    scaler = ridge.named_steps["preprocess"].named_transformers_["numeric"]
    pre_test = pd.concat(
        [result["frames"]["train"], result["frames"]["validation"]],
        ignore_index=True,
    )
    np.testing.assert_allclose(scaler.mean_, pre_test[NUMERIC_FEATURES].mean().to_numpy())
    full_mean = featured[NUMERIC_FEATURES].mean().to_numpy()
    assert not np.allclose(scaler.mean_, full_mean)


def test_committed_metrics_match_a_fresh_run():
    featured = add_features(load_daily_revenue())
    fresh = run_evaluation(featured)
    saved = json.loads(METRICS_PATH.read_text())
    assert fresh["selected_model"] == saved["selected_model"]
    assert fresh["trained_through"] == saved["trained_through"]
    assert fresh["periods"] == saved["periods"]
    for split_name in ("validation", "test"):
        assert fresh[split_name] == saved[split_name]


def test_train_and_save_round_trip(tmp_path):
    model_path = tmp_path / "revenue_model.joblib"
    metrics_path = tmp_path / "metrics.json"
    payload = train_and_save(model_path=model_path, metrics_path=metrics_path)
    assert model_path.exists()
    saved = load_model(model_path)
    assert saved["model_name"] == payload["selected_model"]
    daily = load_daily_revenue()
    featured = add_features(daily)
    holdout_day = featured.loc[featured["date"] > pd.Timestamp(saved["trained_through"])].iloc[0]
    history = daily.loc[daily["date"] < holdout_day["date"]].tail(HISTORY_DAYS)["revenue"]
    prediction = predict_revenue(saved["model"], history, holdout_day["date"])
    assert np.isfinite(prediction)
    # The saved model was fit before this holdout day, so the call above is
    # not using that day's sales. Confirm the feature row agrees.
    assert features_from_history(history, holdout_day["date"])["lag_1"].iloc[0] == pytest.approx(
        history.iloc[-1]
    )


def test_readme_lists_the_held_out_scores():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
    saved = json.loads(METRICS_PATH.read_text())
    assert "random_forest" == saved["selected_model"]
    for scores in list(saved["test"].values()) + list(saved["validation"].values()):
        assert f"{scores['mae']:,.2f}" in readme
        assert f"{scores['rmse']:,.2f}" in readme
        assert f"{scores['r2']:.4f}" in readme


def test_make_ridge_exposes_a_scaler_inside_the_pipeline():
    pipeline = make_ridge()
    assert "preprocess" in pipeline.named_steps


def test_app_renders_a_forecast_from_the_saved_model():
    """The Streamlit script must forecast with the trained model, not a formula."""
    if not MODEL_PATH.exists() or not METRICS_PATH.exists():
        train_and_save()
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
    app.run(timeout=60)
    assert not app.exception
    metrics = app.metric
    assert metrics
    labels = [metric.label for metric in metrics]
    assert "Model forecast" in labels
    assert any(label.startswith("Actual") for label in labels)
