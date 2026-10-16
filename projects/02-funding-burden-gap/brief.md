# Scan: funding vs burden gaps

**Status:** outline — fill on Days 5–6.

## Decision

_Where a grantmaker should look first, in one paragraph._

## Question

Which countries have high malaria (or NTD / nutrition) burden and little recorded development finance for that cause?

## Method

Join GBD DALYs to CRS disbursements via `cause_crosswalk.yaml`. Rank by DALYs per dollar and by a residual from regressing log aid on log DALYs + log GDP.

## Results

_Table of top 10 gap countries; one robustness check (deaths instead of DALYs)._

## What would change my mind

A better mapping of CRS codes, or IATI philanthropy that fills the “gap.”

## Limitations

Aid is not the same as domestic spend or DAH from IHME’s development-assistance-for-health series. Crosswalk error is first-order.
