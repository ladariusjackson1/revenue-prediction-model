"""Streamlit app that forecasts one day with the model saved by train.py."""

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.forecast import (
    DATA_PATH,
    DISPLAY_NAMES,
    FEATURE_COLUMNS,
    HISTORY_DAYS,
    METRICS_PATH,
    MODEL_PATH,
    add_features,
    features_from_history,
    load_daily_revenue,
    load_model,
    predict_revenue,
)


st.set_page_config(page_title="Daily sales forecast", layout="wide")
st.title("Daily sales forecast")
st.write(
    "Forecasts one day of net merchandise sales (GBP) for the UCI Online Retail "
    "series. The number is the saved model's prediction, using only earlier days."
)

if not MODEL_PATH.exists() or not METRICS_PATH.exists():
    st.warning("No saved model yet. From the repository root, run `python train.py`.")
    st.stop()

payload = load_model(MODEL_PATH)
metrics = json.loads(METRICS_PATH.read_text())
model_name = payload["model_name"]
trained_through = pd.Timestamp(payload["trained_through"])

st.subheader("Held-out test scores")
st.caption(
    "Models were refit on every day through "
    f"{trained_through.date()} and scored on later days. "
    f"The saved model is {DISPLAY_NAMES[model_name]}, "
    "chosen by validation MAE before this window was scored."
)
test_rows = []
for name, scores in metrics["test"].items():
    test_rows.append(
        {
            "Model": DISPLAY_NAMES[name],
            "MAE (GBP)": f"{scores['mae']:,.2f}",
            "RMSE (GBP)": f"{scores['rmse']:,.2f}",
            "R²": f"{scores['r2']:.4f}",
            "Saved model": "yes" if name == model_name else "",
        }
    )
st.dataframe(pd.DataFrame(test_rows), hide_index=True)

daily = load_daily_revenue(DATA_PATH)
st.subheader("Daily net sales")
chart = daily.set_index("date")["revenue"]
st.line_chart(chart)

st.subheader("Forecast one day")
featured_dates = add_features(daily)["date"]
next_day = daily["date"].max() + pd.Timedelta(days=1)
options = list(featured_dates) + [next_day]
labels = [day.strftime("%Y-%m-%d") for day in options]
default_index = labels.index(daily["date"].max().strftime("%Y-%m-%d"))
choice = st.selectbox("Date to forecast", labels, index=default_index)
forecast_day = pd.Timestamp(choice)

custom = st.text_area(
    f"Optional history: {HISTORY_DAYS} daily sales amounts for the calendar days "
    "before this date, oldest first. Leave this blank to use the public series.",
    placeholder="One number per line",
)

prior = daily.loc[daily["date"] < forecast_day].tail(HISTORY_DAYS)
if custom.strip():
    try:
        history = [float(piece) for piece in custom.split()]
    except ValueError:
        st.error("History must be numbers separated by spaces or new lines.")
        st.stop()
else:
    history = prior["revenue"].tolist()

if len(history) < HISTORY_DAYS:
    st.error(
        f"Need {HISTORY_DAYS} days before {forecast_day.date()}. "
        "This date is too early in the series, or the pasted history is short."
    )
    st.stop()

if forecast_day <= trained_through:
    st.info(
        "This date is on or before the last training day "
        f"({trained_through.date()}), so the forecast is in-sample."
    )
else:
    st.info(
        "This date is after the last training day "
        f"({trained_through.date()}). It was not used to fit the saved model."
    )

try:
    feature_row = features_from_history(history, forecast_day)
    forecast = predict_revenue(payload["model"], history, forecast_day)
except (ValueError, FileNotFoundError) as error:
    st.error(str(error))
    st.stop()

st.metric("Model forecast", f"£{forecast:,.2f}")
actual = daily.loc[daily["date"] == forecast_day, "revenue"]
if not actual.empty:
    st.metric("Actual net sales that day", f"£{float(actual.iloc[0]):,.2f}")
    st.caption("The actual amount is shown for comparison. It is not a model input.")

with st.expander("Features passed to the model"):
    st.dataframe(feature_row[FEATURE_COLUMNS], hide_index=True)
    st.caption(
        "lag_1, lag_7, and lag_14 are earlier days. The rolling means use only "
        "days before the forecast date. day_of_week uses Monday = 0."
    )
