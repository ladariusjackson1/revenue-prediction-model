# Test coverage

Statement coverage for all seven ML projects. `scripts/ci_ml.sh` runs data generation, training, and pytest under `coverage`, combines the seven runs, and rewrites this file and `docs/badges/coverage.svg`. GitHub Actions uploads an HTML copy (`htmlcov/`) as the `coverage-report` artifact and fails if the committed report drifts.

Measured total: **92%**.

| Name                                                    |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------------------------------- | -------: | -------: | ------: | --------: |
| projects/01-daily-sales-forecast/app.py                 |       66 |       14 |     79% |12, 37-38, 87-91, 96-100, 103, 116-118 |
| projects/01-daily-sales-forecast/src/forecast.py        |      214 |       23 |     89% |100, 107, 120, 131, 147-157, 164, 173, 175, 179, 194, 197, 201, 224, 244, 255, 261, 476, 481 |
| projects/02-customer-churn/src/generate\_data.py        |       23 |        0 |    100% |           |
| projects/02-customer-churn/src/train.py                 |       48 |        3 |     94% |     39-42 |
| projects/03-lead-scoring/src/generate\_data.py          |       25 |        0 |    100% |           |
| projects/03-lead-scoring/src/train.py                   |       36 |        3 |     92% |     23-25 |
| projects/04-customer-segmentation/src/generate\_data.py |       19 |        0 |    100% |           |
| projects/04-customer-segmentation/src/train.py          |       31 |        3 |     90% |     20-22 |
| projects/05-expense-classifier/src/generate\_data.py    |       25 |        0 |    100% |           |
| projects/05-expense-classifier/src/train.py             |       34 |        3 |     91% |     20-22 |
| projects/06-mrr-forecast/src/generate\_data.py          |       20 |        0 |    100% |           |
| projects/06-mrr-forecast/src/train.py                   |       54 |        3 |     94% |     31-33 |
| projects/07-appointment-noshow/src/generate\_data.py    |       21 |        0 |    100% |           |
| projects/07-appointment-noshow/src/train.py             |       35 |        3 |     91% |     21-23 |
| **TOTAL**                                               |  **651** |   **55** | **92%** |           |
