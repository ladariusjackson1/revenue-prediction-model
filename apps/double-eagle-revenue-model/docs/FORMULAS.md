# Financial formulas & recognition policy

## Revenue types (never mix)

| Stream | Counts toward MRR? | Notes |
|---|---|---|
| Setup / implementation | **No** | One-time; contracted / invoiced / collected tracked separately |
| Monthly recurring (website + agent management) | **Yes** | Normalized if billed annually |
| Usage overage | **No** (usage revenue) | Variable; shown separately from MRR |
| Add-on MRR | **Yes** | Included in customer monthly recurring |
| One-time redesign / projects | **No** | Nonrecurring services |

## Core formulas

### MRR
Sum of `customerMonthlyRecurring` for `status === "active"`.

```
monthly = billingFrequency === "annual" ? contracted/12 : contracted
MRR += monthly + normalized(addonMrr)
```

Setup fees are **never** included.

### ARR
`ARR = MRR × 12` — **annualized run-rate**, not trailing twelve-month revenue.

### Gross profit / margin (monthly delivery view)
```
Recognized_delivery = Active_MRR + Usage_overage
Direct_costs = voice_mins×$/min + hosting + phone + support_labor + processing + allocated_CRM
Gross_profit = Recognized_delivery − Direct_costs
Gross_margin = Gross_profit / Recognized_delivery
```
Shared OpEx (ads, owner draw, shared tools) is **not** in direct costs.

### Operating profit
`Operating_profit = Gross_profit − monthly_OpEx`

### CAC
`CAC = attributable_acquisition_spend / new_activated_customers`  
Null if denominator is 0.

### ARPA
`ARPA = MRR / active_paying_accounts`  
Null if no actives.

### Logo churn
`Churn = customers_cancelled_in_period / customers_active_at_period_start`  
Null if start cohort empty.

### Revenue churn
`Lost_MRR / Starting_MRR` (cancellations + downgrades; expansions excluded).

### NRR
`(Start + Expansion − Contraction − Churned) / Start`  
Label early-stage when history is thin.

### LTV (simple gross-profit method)
`LTV = ARPA × Gross_margin × (1 / monthly_logo_churn)`  
Requires positive churn. **Early-stage estimate** when churn is assumed.

### CAC payback (months)
`CAC / (ARPA × Gross_margin)`

### Break-even revenue
`Fixed_OpEx / (1 − variable_cost_rate)` where variable_cost_rate = direct_costs / delivery_revenue.

### Cash runway
`Operating_cash / monthly_net_burn` if burning; otherwise “Not burning”.

### Forecast closed logos
```
new_customers = leads × lead_to_appt × show_rate × close_rate
```
Only closed logos enter customer base. Pipeline stages are not double-counted.

## Pricing recommendations (planning)

| Tier | Setup | MRR | Includes |
|---|---|---|---|
| Starter | $1,500 | $497 | Website + lead capture |
| Growth | $3,500 | $1,497 | + voice agent + booking (200 min) |
| Premium | $5,500 | $2,497 | + premium integrations (500 min) |

Market **bands** (not standards): SMB voice retainers commonly cited ~$400–$3,000/mo; managed packages often $1,500–$2,500/mo + $3k–$5k setup (agency blogs / operator reports 2025–2026). Our prices are set from delivery cost + target ~70% gross margin and those bands.

Voice infra planning rate: **$0.13/min** (mid published Vapi/Retell all-in stack, 2026).
