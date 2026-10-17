# 04 — Customer Segmentation (RFM + KMeans)

Cluster customers on Recency / Frequency / Monetary. Reports silhouette score and ARI vs latent segments in synthetic data.

```bash
cd projects/04-customer-segmentation
python -m src.generate_data && python -m src.train && pytest -q
```
