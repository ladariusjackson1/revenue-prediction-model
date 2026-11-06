# Fixture notes

`online_retail_messy.csv` is a 19-row stand-in for the UCI column layout. It is not the UCI extract and it is not a sample of that file. Rows that plant a case the public merchandise subset does not show are marked below. Tests use this file so `python -m finance.run` needs no download.

The hand total for kept merchandise, including the exact-duplicate extra, is 4,643 pence (£46.43).

| Row | What it is | Disposition |
| --- | --- | --- |
| 1 | Merchandise, £2.55 × 6 | kept_merchandise |
| 2 | Exact duplicate of row 1 | kept_duplicate_extra |
| 3 | Same invoice and stock as row 1, different quantity, so not a duplicate | kept_merchandise |
| 4 | Second product on the same invoice | kept_merchandise |
| 5 | Planted return: negative quantity, invoice does not start with C | kept_merchandise (return) |
| 6 | Cancellation invoice | kept_merchandise (cancellation) |
| 7 | Postage | excluded_non_product |
| 8 | Zero price | excluded_bad_price |
| 9 | Negative price | excluded_bad_price |
| 10 | Planted `£` symbol | excluded_unparseable |
| 11 | Planted comma decimal `1,25` | excluded_unparseable |
| 12 | Planted three-decimal price `0.001` | excluded_unparseable |
| 13 | Blank customer id, still a sale | kept_merchandise |
| 14 | Later month, other customer, Germany | kept_merchandise |
| 15 | Same customer as row 1, later month, France | kept_merchandise |
| 16 | Ordinary sale on 5 Dec 2010 | kept_merchandise |
| 17 | Latest timestamp is 16 Jan 2011 12:30, before 16:00, so that day is partial | excluded_partial_day |
| 18 | Blank invoice date | excluded_unparseable |
| 19 | Postage credit. Negative, but not merchandise | excluded_non_product |

Row 5 is planted. On the real UCI merchandise subset, negative quantities that survive the product and price rules are cancellation invoices, not a separate return type. The SQL still has to classify both.
