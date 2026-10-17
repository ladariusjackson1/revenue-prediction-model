# Daily sales forecast

A small forecasting project for one public retail dataset. It predicts the next day's net merchandise sales from earlier days only, compares a seasonal naive baseline with two scikit-learn models, and reports error on a later time window.

The saved model is a random forest. On the held-out window (1 October 2011 through 8 December 2011) its MAE is **£11,629.44**. That is about £654 lower than forecasting each day with the same weekday one week earlier. Ridge regression loses to that naive forecast on the same window. Details are in the tables below.

## Dataset

Daily net sales are aggregated from the [Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) dataset in the UCI Machine Learning Repository.

- **Citation:** Daqing Chen, Sai Laing Sain, and Kun Guo (2012). *Data mining for the online retail industry: A case study of RFM model-based customer segmentation using data mining.* Journal of Database Marketing and Customer Strategy Management, 19(3).
- **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). The daily file in this repo is a derivative and is redistributed under the same license. Attribution belongs with the citation above.
- **What the series is:** 373 calendar days, 1 December 2010 through 8 December 2011, for a UK online gift retailer. `revenue` is net merchandise sales in GBP: `Quantity * UnitPrice` on lines whose stock code starts with a digit and whose unit price is positive. Returns and cancellations stay in as negative quantities. Postage, fees, discounts, manual adjustments, and gift vouchers do not start with a digit, so they are left out. A few letter-prefixed goods (about £400 total) are left out with them.
- **Partial last day:** the workbook ends at 12:50 on 9 December 2011, so that date is dropped. Days with no kept invoices, including every Saturday in this extract, are stored as 0.
- **What is not in the file:** no customer names, customer ids, or invoice lines. The committed table is `date` and `revenue` only.

`data/daily_revenue.csv` is the file the model trains on (total net sales £9,762,760.55, 69 zero-sales days). Rebuild it from the UCI workbook with:

```bash
python scripts/build_daily_revenue.py
```

The workbook is downloaded to `data/raw/` and is gitignored.

## Question and features

Predict net sales on day *t* without using day *t*'s sales.

| Feature | Definition |
| --- | --- |
| `lag_1` | Sales on day *t − 1* |
| `lag_7` | Sales on day *t − 7* (same weekday last week) |
| `lag_14` | Sales on day *t − 14* |
| `rolling_mean_7` | Mean of the 7 days before *t* |
| `rolling_mean_28` | Mean of the 28 days before *t* |
| `day_of_week` | Weekday of day *t* (Monday = 0), known before the day starts |

The first 28 days are only history, so the models see 345 days (29 December 2010 through 8 December 2011). Same-day sales are the target, not a feature. Rolling means are shifted by one day before the window is applied.

## Split

Rows stay in calendar order. There is no random shuffle and no cross-validation.

| Window | Days | Dates | Role |
| --- | ---: | --- | --- |
| Train | 207 | 2010-12-29 to 2011-07-23 | Fit the models that are scored on validation |
| Validation | 69 | 2011-07-24 to 2011-09-30 | Choose the model (lowest MAE) |
| Test | 69 | 2011-10-01 to 2011-12-08 | Held-out scores below |

The test scores are from models refit on train plus validation (through 30 September 2011). The test window is not used to fit or to choose the model. A tie on validation MAE would keep the simpler model: seasonal naive, then ridge, then random forest.

## Models

- **Seasonal naive:** predict day *t* with `lag_7`.
- **Ridge:** `Ridge(alpha=1.0)` on scaled numeric features. The scaler is fit on the fitting rows only. Weekday is one-hot encoded.
- **Random forest:** 300 trees, `max_depth=6`, `min_samples_leaf=5`, `max_features=1.0`, `random_state=0`. Weekday stays a number so the trees can split on it.

These forest settings are fixed. They were not searched on the test window.

## Results

Validation MAE chooses the saved model. Ridge has a slightly lower validation RMSE than the forest; the selection rule is MAE, so the forest is saved.

| Model | MAE (GBP) | RMSE (GBP) | R² |
| --- | ---: | ---: | ---: |
| Seasonal naive | 11,593.10 | 17,978.33 | 0.1667 |
| Ridge | 11,007.89 | 16,006.22 | 0.3395 |
| Random forest | 10,486.13 | 16,033.32 | 0.3373 |

Held-out test scores:

| Model | MAE (GBP) | RMSE (GBP) | R² |
| --- | ---: | ---: | ---: |
| Seasonal naive | 12,283.78 | 17,066.00 | 0.5076 |
| Ridge | 14,670.54 | 19,326.25 | 0.3686 |
| Random forest | 11,629.44 | 16,509.50 | 0.5392 |

Random forest is the saved model. Its test MAE is £11,629.44, against £12,283.78 for the seasonal naive forecast and £14,670.54 for ridge. Ridge beat the naive forecast on validation and lost to it on this later window, which is the run-up to Christmas. R² is higher on the test window than on validation, including for the naive forecast, because sales vary more in that season. MAE is the number in pounds.

`python train.py` reprints these tables and writes `models/metrics.json` plus `models/revenue_model.joblib`. The joblib file is gitignored. The metrics file is committed and checked against a fresh training run in the tests.

## How to run

Python 3.12. From the repository root:

```bash
python -m pip install -r requirements.txt
python train.py
python -m pytest
python -m streamlit run app.py
```

`train.py` has to run before the app. The app loads the saved model and forecasts one day from the previous 28 daily totals. It can use the public series or numbers you paste. If the date is in the dataset, the actual total is shown beside the forecast and is not passed into the model. Dates after 30 September 2011 were not used to fit the saved model; earlier dates are in-sample, and the app says so.

`notebooks/revenue_forecast.ipynb` walks through the same code path. It is stored with executed outputs. Re-run it from the repository root if you change the model code.

## Tests

`pytest` checks the cleaning rules, that features do not depend on same-day or future sales, that the split is chronological, that the naive forecast is last week's sales, that the ridge scaler is fit only on the pre-test window, that `models/metrics.json` matches a fresh run, and that the Streamlit app renders a forecast from the saved model.

GitHub Actions (`.github/workflows/tests.yml`) installs `requirements.txt` and runs `pytest` on Python 3.12.

## Layout

```
app.py                 Streamlit forecast using the saved model
train.py               Fit, score, and save the validation winner
src/forecast.py        Cleaning, features, split, models, metrics
scripts/build_daily_revenue.py
data/daily_revenue.csv Committed daily series (CC BY 4.0 derivative)
data/SOURCE.txt
notebooks/revenue_forecast.ipynb
tests/test_revenue_model.py
models/metrics.json    Held-out scores from train.py
requirements.txt
.github/workflows/tests.yml
```

## Limits

This is one UK gift retailer for about a year. Saturdays are structural zeros, so a weekly naive forecast is already strong. The test window is a single holiday season, not a sample of many years. The forest's gain over last-week sales is real on this split and modest: a few hundred pounds per day against errors of about £12,000. Nothing here estimates what would happen if prices or advertising changed.
