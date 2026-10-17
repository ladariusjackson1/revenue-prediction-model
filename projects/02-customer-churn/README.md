# 02 — Customer Churn Prediction

Predict which retainer clients will churn using tenure, MRR, support load, payment behavior, usage, and NPS.

## Run

```bash
cd projects/02-customer-churn
python -m src.generate_data
python -m src.train
pytest -q
```

Synthetic data (reproducible seed). Compares logistic regression, random forest, and gradient boosting; selects by ROC-AUC.
