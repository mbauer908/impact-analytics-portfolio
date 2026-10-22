# Impact analytics portfolio

Personal analytical work in global health, philanthropy, and climate / social impact. Each project is a **decision-grade MVP**: a Marimo notebook, a short written brief, and a small set of figures an evaluator or grantmaker could actually use.

This repo is built for roles like GiveWell research, evidence synthesis, and climate / energy-transition analysis — not as a dump of unfinished EDA.

## Projects

Projects 01–04 are written up. Projects 05–06 are scoped and not yet run. Public inputs for 01 and 02 are in `data/raw/`.

| # | Project | What it does | Result |
|---|---|---|---|
| 01 | [GiveWell CEA uncertainty](projects/01-givewell-cea-uncertainty/) | Monte Carlo of AMF bed nets in Guinea, then rank stability and a 6× screen across 87 top-charity geographies | Median about $2,600 per under-5 death. HKI Niger is first in about 84% of draws. About 18 geographies are contested at the 6× bar. |
| 02 | [Funding vs burden](projects/02-funding-burden-gap/) | WHO malaria deaths, and GBD DALYs, against OECD malaria-control disbursements plus Global Fund allocations | Large death tolls already match Nigeria, the DRC, and Niger (about $1,500 per death). Yemen is about $1.4–1.8 million a year short; Nigeria is about $56 million a year short of Niger. |
| 03 | [Cash transfers and consumption](projects/03-intervention-meta-analysis/) | Random-effects pool of 8 cash-transfer studies on household consumption, plus a cost per 10 percentage-point gain | Mean about +19%. Programs disagree enough that a new program’s range includes no gain. About $570 per 10 percentage-point gain. |
| 04 | [DALY vs WELLBY ranking](projects/04-daly-wellby-comparison/) | Published WELLBY estimates for cash, psychotherapy, and bed nets, set next to the life-saving programs that have none | StrongMinds produces about five times the wellbeing per dollar of GiveDirectly cash transfers (40 vs 7.55 WELLBYs per $1,000). Bed nets span about 7 to 90, so they can match cash transfers or beat psychotherapy. Vitamin A and seasonal chemoprevention have no WELLBY estimate. |
| 05 | [MA coastal flood exposure](projects/05-ma-coastal-flood/) | 2050 sea-level flood zone over parcels and social vulnerability, one Massachusetts county | Not run. |
| 06 | [EV charging deserts](projects/06-ev-charging-deserts/) | Public chargers against population and income in the Boston metro | Not run. Output is tracts that are both poorly served and lower-income. |

See [RESEARCH_PLAN.md](RESEARCH_PLAN.md) for the original scope boxes and the order the week was run.

## Setup

Python 3.10+ (3.11+ preferred). System Python on macOS is often 3.9.

```bash
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Launch a notebook:

```bash
marimo edit projects/01-givewell-cea-uncertainty/notebook.py
```

## How a project is “done”

1. Notebook runs end-to-end from documented inputs.
2. `brief.md` is 2–4 pages: question, method, result, decision, limitations.
3. Figures in `figures/` are cited in the brief.
4. Data provenance is in the project README (URL, date, license).

## License

Code is MIT. Underlying datasets remain under their original licenses; do not republish restricted extracts.
