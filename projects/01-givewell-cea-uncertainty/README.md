# 01 — Stress-test a GiveWell cost-effectiveness model

**Part A.** Convert AMF / Guinea point estimates into distributions, run Monte Carlo, identify drivers of uncertainty in cost per under-5 death averted.

**Part B.** Propagate GiveWell’s published CE uncertainty across the **full top-charity program × geography portfolio** and ask whether rank order is stable.

## Run

```bash
source .venv/bin/activate
marimo edit projects/01-givewell-cea-uncertainty/notebook.py
python projects/01-givewell-cea-uncertainty/run_portfolio_ranks.py
```

Requires local workbooks under `data/raw/givewell/` (gitignored): AMF / HKI / Malaria Consortium / New Incentives CEAs plus the moral-weights tool export.

## Deliverables

- [x] `parameters.yaml` — Guinea AMF cells
- [x] Monte Carlo + tornado (`figures/cea_distribution.png`, `figures/tornado.png`)
- [x] Portfolio CE ranges + ranks (`portfolio_ce_ranges.csv`, `portfolio_charity_level.csv`)
- [x] TCF CE-screen proxy (`portfolio_fund_eligibility.csv`; P(clear 6× / 8×))
- [x] Portfolio figures (`figures/portfolio_*.png`)
- [x] `brief.md` — single-initiative + portfolio rank + fund-bar section

## Headline results

- **Guinea AMF:** median ~$2,565 per U5 death averted (GiveWell point ~$2,225); top drivers = baseline mortality, usage, cost per net.
- **Portfolio (87 geos):** HKI Niger remains #1 in ~84% of draws; point-rank vs median-MC-rank Spearman ρ ≈ 1.0; mid-pack top-5 membership is less sticky (~0.57 Jaccard).
- **TCF CE screen (6× bar):** ~50 geos clear on point; ~48 clear per draw on average; ~18 contested; AMF Guinea clears with P≈1.
