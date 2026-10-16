# Impact analytics portfolio

Personal analytical work in global health, philanthropy, and climate / social impact. Each project is a **decision-grade MVP**: a Marimo notebook, a short written brief, and a small set of figures an evaluator or grantmaker could actually use.

This repo is built for roles like GiveWell research, evidence synthesis, and climate / energy-transition analysis — not as a dump of unfinished EDA.

## Projects

| # | Project | Question | Primary deliverable |
|---|---|---|---|
| 01 | [GiveWell CEA uncertainty](projects/01-givewell-cea-uncertainty/) | Which assumptions drive cost-effectiveness for a top charity? | Monte Carlo + tornado + 2-page evaluator note |
| 02 | [Funding vs burden gap](projects/02-funding-burden-gap/) | Where is disease burden high and aid low? | Neglectedness map + ranked gap table |
| 03 | [Intervention meta-analysis](projects/03-intervention-meta-analysis/) | What is the pooled effect, and what does it cost? | Forest plot + cost per outcome |
| 04 | [DALY vs WELLBY ranking](projects/04-daly-wellby-comparison/) | Do charity rankings flip under a different welfare unit? | Comparison brief |
| 05 | [MA coastal flood exposure](projects/05-ma-coastal-flood/) | Who and what is exposed to SLR-driven flooding by 2050? | Exposure + vulnerability overlay |
| 06 | [EV charging deserts](projects/06-ev-charging-deserts/) | Where is charging access thin relative to people and income? | Underserved-area map |

See [RESEARCH_PLAN.md](RESEARCH_PLAN.md) for the 10–14 day sprint, scope boxes, and data sources.

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
