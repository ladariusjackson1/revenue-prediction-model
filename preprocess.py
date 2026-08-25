"""Preprocessing walkthrough for the quarterly revenue sample dataset.

This is a standalone teaching pipeline. Its sample data has different columns
than mock_revenue_data.csv (which drives train.py), so it stays self-contained.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

TARGET_COLUMN = "quarterly_revenue"
CATEGORICAL_COLUMNS = ["region"]
NUMERIC_COLUMNS = ["advertising_spend", "active_customers"]
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Sample dataset for Double Eagle Financial LLC.
SAMPLE_DATA = {
    "advertising_spend": [1200, 1500, np.nan, 2100, 1800, 2500, 1500, 2900],
    "active_customers": [45, 50, 48, 65, np.nan, 80, 50, 95],
    "region": ["North", "South", "North", "West", "South", "West", "North", "South"],
    "quarterly_revenue": [15000, 18500, 16000, 24000, 21000, 29000, 18500, 34000],
}


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode categoricals and split off the target."""
    encoded = pd.get_dummies(df, columns=CATEGORICAL_COLUMNS, drop_first=True)
    return encoded.drop(columns=[TARGET_COLUMN])


def preprocess(df: pd.DataFrame):
    """Split first, then fit imputation and scaling on the training rows only.

    Ordering matters: the previous version imputed and scaled the full dataset
    before splitting, which leaked test-set statistics into the training data.
    """
    X = build_features(df)
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    # NOTE: the README describes median imputation but this has always used the
    # mean. Left as mean to preserve behaviour -- confirm which is intended.
    fill_values = X_train[NUMERIC_COLUMNS].mean()
    X_train = X_train.fillna(fill_values)
    X_test = X_test.fillna(fill_values)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)  # transform only, never refit

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


if __name__ == "__main__":
    print("Data engineering pipeline initialized.")
    frame = pd.DataFrame(SAMPLE_DATA)
    print("\n--- Raw Ingested Data ---")
    print(frame)

    X_train, X_test, y_train, y_test, _ = preprocess(frame)

    print("\n--- Preprocessing Metrics ---")
    print(f"Training input rows (X_train shape): {X_train.shape}")
    print(f"Testing evaluation rows (X_test shape): {X_test.shape}")
    print("Pipeline complete.")
