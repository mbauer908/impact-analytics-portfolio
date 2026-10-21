# 01 — Stress-test GiveWell cost-effectiveness (expanded)

Three linked research questions, written up in `brief.md`:

| Part | Question | Unit / metric |
|---|---|---|
| **1** | For AMF bed nets in **Guinea**, which assumptions drive uncertainty in cost per under-5 death averted, and how often does a simplified chain stay under a rough dollar bar? | $/U5 death averted (lower is better) |
| **2** | Across GiveWell’s Top Charity **program × geography** portfolio, how stable is **rank order** when each cell’s CE is drawn from GiveWell’s uncertainty ranges? Who is #1 how often? | × GiveWell benchmark (higher is better) |
| **3** | Under the same uncertainty, which initiative-geographies clear a **Top Charities Fund–style CE screen** (6× bar, with 8× robustness)? How often are borderline geos “in” vs “out”? | P(CE ≥ bar); rank by that probability |

**Scope notes.** Part 1 reverse-engineers a simplified causal chain from the AMF CEA. Parts 2–3 use published final CE + Sensitivity-sheet 25th/75th ranges (imputed widths where missing)—not a full re-build of every charity’s model. Part 3 is a **CE-screen proxy** only; TCF allocation also uses judgment and room for more funding.

## Run

```bash
source .venv/bin/activate
marimo edit projects/01-givewell-cea-uncertainty/notebook.py   # Part 1
python projects/01-givewell-cea-uncertainty/run_portfolio_ranks.py  # Parts 2–3
```

Workbooks are in `data/raw/givewell/`: AMF, HKI, Malaria Consortium, New Incentives, and the moral-weights tool. They are GiveWell’s public spreadsheets.

## Deliverables

- [x] `parameters.yaml` — Guinea AMF cells with sources
- [x] Part 1 Monte Carlo + Spearman tornado + one-way sensitivity (`figures/cea_distribution.png`, `figures/tornado.png`, `figures/one_way_tornado.png`; `one_way_sensitivity.csv`)
- [x] Part 2 ranks (`portfolio_ce_ranges.csv`, `portfolio_charity_level.csv`, `portfolio_pairwise_top8.csv`)
- [x] Part 3 TCF CE-screen proxy (`portfolio_fund_eligibility.csv`; P(clear 6× / 8×))
- [x] Portfolio figures (`figures/portfolio_*.png`)
- [x] `brief.md` — methodology, results, “what would change my mind,” and limitations per part

## Headline results

- **Part 1 — Guinea AMF:** median ~$2,565 per U5 death averted (GiveWell point ~$2,225); top drivers = baseline mortality, usage, cost per net; ~99% of draws below $5k.
- **Part 2 — Rank order (87 geos):** HKI Niger remains #1 in ~84% of draws; point-rank vs median-MC-rank Spearman ρ ≈ 1.0; mid-pack top-5 membership is less sticky (~0.57 Jaccard).
- **Part 3 — TCF CE screen (6×):** ~50 geos clear on point; ~48 clear per draw on average; ~18 contested; AMF Guinea clears with P≈1; Malaria Consortium most consistently fills the eligible set.
