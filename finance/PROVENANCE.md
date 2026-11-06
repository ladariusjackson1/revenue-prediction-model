# Provenance and snapshot rules

The ledger is built from one public file.

| Item | Value |
| --- | --- |
| Dataset | Online Retail, UCI Machine Learning Repository, id 352 |
| Citation | Daqing Chen, Sai Laing Sain, and Kun Guo (2012). *Data mining for the online retail industry: A case study of RFM model-based customer segmentation using data mining.* Journal of Database Marketing and Customer Strategy Management, 19(3). |
| Page | https://archive.ics.uci.edu/dataset/352/online+retail |
| Download | https://archive.ics.uci.edu/static/public/352/online+retail.zip |
| License | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Aggregates in this repo stay under that license. Attribution stays with the citation above. |
| Currency | GBP. Country is the ship-to country. This file does not contain FX rates. |
| Workbook sha256 | `43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d` |
| Workbook bytes | 23,715,344 |
| Retrieved | 2026-11-06 |

## What is committed

- `finance/outputs/uci_snapshot.json` and the aggregate CSVs next to it. No invoice line and no customer id.
- `finance/fixtures/online_retail_messy.csv`, a 19-row planted fixture. It is not a sample of the UCI file. See `fixtures/FIXTURE_NOTES.md`.
- The daily forecast series in `projects/01-daily-sales-forecast/data/daily_revenue.csv`, which the mart must match to the penny.

## What is not committed

- The xlsx workbook and the zip.
- `finance/build/`, the local SQLite files. Those still contain customer ids and are gitignored.

## Rebuild rule

1. Download the zip from the URL above. Do not take the workbook from a mirror whose hash you have not checked.
2. Unzip `Online Retail.xlsx`.
3. Confirm the sha256. If it differs from the table, stop. Do not refresh the published snapshot until the difference is understood.
4. From the repository root, with pandas and openpyxl installed: `python -m finance.run --uci "/path/to/Online Retail.xlsx"`.
5. That command replaces the snapshot, the aggregate CSVs, and `docs/revenue-quality/index.html`. The offline test then checks that the new daily mart still matches the forecast series. If it does not, the merchandise rule and the forecast have drifted and the snapshot should not be published.

The default command, `python -m finance.run`, does not download. It tests the fixture and rewrites the explorer from the committed snapshot.
