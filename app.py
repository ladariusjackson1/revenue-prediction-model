import sqlite3
from contextlib import closing

import joblib
import pandas as pd
import streamlit as st
from sklearn.linear_model import Ridge
from sqlalchemy import create_engine

from revenue_model import (
    APP_GROWTH_RATE,
    FEATURE_COLUMNS,
    LOG_DB_PATH,
    MIN_ROWS_TO_RETRAIN,
    MODEL_PATH,
    app_forecast,
    require_columns,
)

LOG_TABLE = "user_inputs"
UPLOAD_PREVIEW_COLUMNS = ["transaction_id", "gross_revenue", "Predicted_Future_Revenue"]
LOG_COLUMNS = ["transaction_id", *FEATURE_COLUMNS, "Predicted_Future_Revenue", "actual_revenue"]

# --- DATABASE LAYER ---
# create_engine returns a real connectable; the previous code passed a bare
# connection-string to pandas and only worked because SQLAlchemy was installed.
engine = create_engine(f"sqlite:///{LOG_DB_PATH}")


# --- RETRAINING FUNCTION ---
def retrain_from_verified_logs():
    """Refit on logged rows that have a verified actual_revenue.

    Returns (row_count, error_message). The previously fitted model was
    discarded without being saved; it is now persisted to MODEL_PATH.
    """
    if not LOG_DB_PATH.exists():
        return 0, None

    try:
        logged = pd.read_sql(LOG_TABLE, con=engine)
    except (ValueError, sqlite3.DatabaseError) as error:
        # Previously a bare `except Exception: pass`, which made a corrupt
        # database indistinguishable from an empty one.
        return 0, str(error)

    if "actual_revenue" not in logged.columns:
        return 0, None

    verified = logged.dropna(subset=["actual_revenue"])
    if len(verified) < MIN_ROWS_TO_RETRAIN:
        return 0, None

    try:
        require_columns(verified, FEATURE_COLUMNS, source="log database")
    except ValueError as error:
        return 0, str(error)

    model = Ridge()
    model.fit(verified[FEATURE_COLUMNS], verified["actual_revenue"])
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return len(verified), None


def log_rows(rows: pd.DataFrame) -> None:
    """Append rows to the log table using a stable column order."""
    rows.reindex(columns=LOG_COLUMNS).to_sql(
        LOG_TABLE, con=engine, if_exists="append", index=False
    )


st.set_page_config(page_title="Revenue Forecasting", layout="wide")
st.title("Revenue Forecasting Engine")
st.write("Log transactions, forecast revenue, and refit the model on verified outcomes.")

# --- SIDEBAR STATUS MONITOR ---
with st.sidebar:
    st.header("System Status")

    trained_rows, retrain_error = retrain_from_verified_logs()
    if retrain_error:
        st.error(f"Could not read the log database: {retrain_error}")
    elif trained_rows:
        st.info(f"Model refit and saved using {trained_rows} verified records.")
    else:
        st.warning(
            f"Awaiting data: need at least {MIN_ROWS_TO_RETRAIN} rows with a "
            "verified actual_revenue before refitting."
        )

    # Stated plainly because it is easy to miss: the numbers on screen come from
    # the configured growth rate, not from the saved model.
    st.caption(
        f"Displayed forecasts use the configured growth rate "
        f"({APP_GROWTH_RATE:.2f}x), not the saved model."
    )

# --- MAIN INTERFACE BLOCKS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Live Estimation Inputs")
    transaction_id = st.text_input("Transaction/Client ID", "T115")
    gross_revenue = st.slider("Gross Revenue ($)", 1000.0, 15000.0, 5000.0, step=100.0)
    is_recurring = st.selectbox(
        "Is Recurring?", [1, 0], format_func=lambda flag: "Yes" if flag == 1 else "No"
    )
    prev_revenue_lag1 = st.slider(
        "Previous Lag Revenue ($)", 1000.0, 15000.0, 4500.0, step=100.0
    )

    forecast = app_forecast(gross_revenue)
    st.metric(label="Forecasted Revenue", value=f"${forecast:,.2f}")

    if st.button("Commit Log to Database"):
        log_rows(
            pd.DataFrame(
                [
                    {
                        "transaction_id": transaction_id,
                        "gross_revenue": gross_revenue,
                        "is_recurring": is_recurring,
                        "prev_revenue_lag1": prev_revenue_lag1,
                        "Predicted_Future_Revenue": forecast,
                        "actual_revenue": None,
                    }
                ]
            )
        )
        st.success("Transaction logged.")
        st.rerun()

with col2:
    st.subheader("Bulk Spreadsheet Processing")
    uploaded_file = st.file_uploader(
        "Drop your raw transaction CSV or Excel file here:", type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        # Guard against re-ingesting the same upload. The old code called
        # st.rerun() inside this block, so every rerun re-appended the whole
        # file to the database in an endless loop.
        upload_key = (uploaded_file.name, uploaded_file.size)
        already_ingested = st.session_state.get("last_upload") == upload_key

        try:
            if uploaded_file.name.endswith(".csv"):
                user_df = pd.read_csv(uploaded_file)
            else:
                user_df = pd.read_excel(uploaded_file)  # needs openpyxl
        except (ValueError, ImportError, pd.errors.ParserError) as error:
            user_df = None
            st.error(f"Could not read that file: {error}")

        if user_df is not None:
            try:
                # Validate every column used below, not just gross_revenue.
                require_columns(
                    user_df, ["transaction_id", *FEATURE_COLUMNS], source=uploaded_file.name
                )
            except ValueError as error:
                st.error(str(error))
            else:
                user_df["Predicted_Future_Revenue"] = app_forecast(user_df["gross_revenue"])
                if "actual_revenue" not in user_df.columns:
                    user_df["actual_revenue"] = None

                st.write("### Forecast Preview")
                st.dataframe(user_df[UPLOAD_PREVIEW_COLUMNS].head())

                if already_ingested:
                    st.info("This file has already been logged.")
                else:
                    log_rows(user_df)
                    st.session_state["last_upload"] = upload_key
                    st.success(f"Logged {len(user_df)} rows.")

st.markdown("---")

# --- FEEDBACK LAYER ---
st.subheader("Submit Real-World Outcome")
st.write(
    "Logging verified revenue lets the sidebar refit the saved model on reload."
)

f_col1, f_col2 = st.columns(2)
with f_col1:
    target_id = st.text_input("Enter Transaction ID to Update:", "")
with f_col2:
    actual_revenue = st.number_input(
        "Enter Real-World Actual Revenue Earned ($):", min_value=0.0, step=100.0
    )

if st.button("Submit Actual Revenue"):
    if not target_id.strip():
        st.warning("Enter a transaction ID first.")
    else:
        # `with sqlite3.connect(...)` commits but does not close, so wrap in closing().
        with closing(sqlite3.connect(LOG_DB_PATH)) as connection, connection:
            cursor = connection.execute(
                f"UPDATE {LOG_TABLE} SET actual_revenue = ? WHERE transaction_id = ?",
                (actual_revenue, target_id.strip()),
            )
            updated_rows = cursor.rowcount
        # Previously reported success even when no row matched.
        if updated_rows:
            st.success(f"Updated {updated_rows} row(s) for {target_id}.")
            st.rerun()
        else:
            st.warning(f"No logged transaction found with ID '{target_id}'.")
