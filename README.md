# Top 500 Companies Revenue Model

Dashboard and Google Sheet for U.S. top 500 company revenues (Fortune 500 2025 / FY2024).

## Live links

- **Web dashboard (local):** run below, then open `http://127.0.0.1:43211`
- **[Google Sheet](https://docs.google.com/spreadsheets/d/1y1etk77QLopdToYomWSkjGGYxyCjy9WyvJtb26_r3NM/edit#gid=1516245268)**

## Run locally

```bash
npm install
npm run dev -- -p 43211 -H 127.0.0.1
```

Open [http://127.0.0.1:43211](http://127.0.0.1:43211).

## What’s included

### Web dashboard
- Total revenue / company / employee KPIs
- Concentration bars (Top 10 / 50 / 100 / rest)
- Top 20 company and top industry charts
- HQ state snapshot
- Searchable Top 100 table

### Google Sheet tabs
| Tab | Purpose |
| --- | --- |
| Dashboard | KPIs + charts |
| Top 500 | Full company table |
| By Industry / By State | Rollups |
| Scenarios | Base / Bull / Bear growth (yellow inputs) |
| About | Sources |

## Data

Salt Technologies AI Fortune 500 Companies Directory 2025 (CC BY 4.0).  
https://www.salttechno.ai/datasets/fortune-500-companies-2025/
