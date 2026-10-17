# 06 — MRR Forecast

Monthly recurring revenue forecast with lag features. Compares seasonal naive (lag-12), ridge, and random forest on a held-out tail window.

```bash
cd projects/06-mrr-forecast
python -m src.generate_data && python -m src.train && pytest -q
```
