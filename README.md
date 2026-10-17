# Revenue Prediction Model — ML Portfolio

Machine learning projects for revenue, retention, and operations — plus the **Double Eagle Financial** planning dashboard.

**Owner:** Ladarius Jackson ([@ladariusjackson1](https://github.com/ladariusjackson1))

## Projects

| # | Project | Type | Path |
|---|---------|------|------|
| 01 | Daily sales forecast (UCI Online Retail) | Time series regression | [`projects/01-daily-sales-forecast`](projects/01-daily-sales-forecast) |
| 02 | Customer churn | Binary classification | [`projects/02-customer-churn`](projects/02-customer-churn) |
| 03 | Lead scoring (RE / PM / GC) | Binary classification | [`projects/03-lead-scoring`](projects/03-lead-scoring) |
| 04 | Customer segmentation (RFM) | Clustering | [`projects/04-customer-segmentation`](projects/04-customer-segmentation) |
| 05 | Expense memo classifier | Text classification | [`projects/05-expense-classifier`](projects/05-expense-classifier) |
| 06 | MRR forecast | Time series regression | [`projects/06-mrr-forecast`](projects/06-mrr-forecast) |
| 07 | Appointment no-show | Binary classification | [`projects/07-appointment-noshow`](projects/07-appointment-noshow) |

## App

| App | Description | Path |
|-----|-------------|------|
| Double Eagle revenue model | Next.js MRR / pricing / forecast dashboard for bookkeeping + AI packages | [`apps/double-eagle-revenue-model`](apps/double-eagle-revenue-model) |

## Quick start (ML)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Train + test every project
for d in projects/0*; do
  echo "=== $d ==="
  (cd "$d" && python -m src.generate_data 2>/dev/null || true)
  (cd "$d" && (python -m src.train 2>/dev/null || python train.py))
  (cd "$d" && pytest -q)
done
```

Project 01 uses the committed UCI-derived daily series (`python train.py`). Projects 02–07 generate synthetic data with fixed seeds.

## Double Eagle dashboard

```bash
cd apps/double-eagle-revenue-model
npm install
npm run dev
```

Open http://127.0.0.1:43211

## CI

GitHub Actions runs pytest across all `projects/*/tests`.
