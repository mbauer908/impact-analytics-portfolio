# 06 — EV charging deserts

Map public chargers against population and income; flag tracts that are both underserved and lower-income.

**Status.** Scaffold. Default geography: **Boston–Cambridge–Newton metro** (reuse MA context from 05).

## Data

- NREL AFDC API (`NREL_API_KEY` in `.env`)
- ACS tract population and median household income

## Deliverables

- [ ] Access metric (plugs per 10k within 1 km, plus distance to nearest DCFC)
- [ ] Tract table of “desert ∩ low income”
- [ ] `brief.md`
