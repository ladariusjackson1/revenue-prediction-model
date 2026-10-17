# 03 — Lead Scoring

Score Oxford-area RE / PM / GC leads for Double Eagle outbound. Gradient boosting on niche, source, firm size, inbound volume, books backlog, and engagement.

```bash
cd projects/03-lead-scoring
python -m src.generate_data && python -m src.train && pytest -q
```
