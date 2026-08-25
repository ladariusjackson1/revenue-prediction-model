"""Fit the revenue prediction model and save it to models/."""

import joblib
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from revenue_model import (
    FEATURE_COLUMNS,
    MODEL_PATH,
    RIDGE_ALPHA,
    MissingColumnsError,
    load_training_frame,
    training_target,
)


def train() -> Ridge:
    print("Initiating Machine Learning Training Pipeline...")

    # Loads, de-duplicates, validates columns, and drops rows with missing
    # features. Raises MissingColumnsError with a readable message rather than
    # a bare KeyError when the CSV lacks a feature column.
    df = load_training_frame()
    print(f"   - Training rows after de-duplication and NA drop: {len(df)}")

    X = df[FEATURE_COLUMNS]
    y = training_target(df["gross_revenue"], df["is_recurring"])

    model = Ridge(alpha=RIDGE_ALPHA)
    model.fit(X, y)

    print("Model Training Complete.")
    for name, coefficient in zip(FEATURE_COLUMNS, model.coef_):
        print(f"   - {name} coefficient: {coefficient:.4f}")

    # Fit quality on the training rows themselves. The target is a closed-form
    # formula, so these errors should be near zero; a large value means the
    # feature columns and the target formula have drifted apart.
    predictions = model.predict(X)
    print(f"   - In-sample MAE:  ${mean_absolute_error(y, predictions):,.2f}")
    print(f"   - In-sample RMSE: ${root_mean_squared_error(y, predictions):,.2f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved trained model to '{MODEL_PATH}'")
    return model


if __name__ == "__main__":
    try:
        train()
    except (FileNotFoundError, MissingColumnsError) as error:
        raise SystemExit(f"Training aborted: {error}")
