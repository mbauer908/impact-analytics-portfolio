# 02 — Funding vs burden (malaria)

**Question.** Which countries have a high malaria death toll relative to malaria aid, once OECD purpose 12262 and the Global Fund country allocation are counted together?

**Choice.** Malaria (not NTDs or nutrition), to sit next to the GiveWell bed-net work in project 1.

## Status

Crosswalk, ranked table, map, scatter, and brief use the combined aid total. The OECD-only rank is kept in the CSV as a comparison.

| Deliverable | Status |
|---|---|
| `cause_crosswalk.yaml` | done |
| Ranked CSV (`funding_burden_ranked.csv`) | done |
| Map, bar, and scatter, deaths and DALYs | done |
| `brief.md` | done |

## Headline

- 47 countries with ≥100 WHO malaria deaths in 2021.
- Aid in the rank = OECD 12262 (2019–2022 average) + Global Fund malaria allocation for 2020–2022, divided by three.
- That division by three is an assumption. Yemen and Gabon have no 2020–2022 country allocation; their Global Fund figure is the mean of WHO Annex 4C country reports. Equatorial Guinea is left at $0, not imputed.
- Countries with the largest death tolls are already at or above the median of Nigeria, the DRC, and Niger: about **$1,500 per WHO death** and **$18 per DALY**.
- Further aid on that rate: **Yemen $1.4–1.8 million** a year (Global Fund figure imputed from the WHO country report), and **Nigeria about $56 million** a year on deaths to match Niger. Chad and the other countries with no OECD malaria-control line are at **$0** once the Global Fund allocation is counted.

Government malaria-program spending from Annex 4C is in the CSV and is not part of the aid total.

## Run

```bash
source .venv/bin/activate
python projects/02-funding-burden-gap/run_funding_gap.py
```

The IHME malaria DALY extract is `data/raw/funding/gbd_malaria_dalys_2021.csv`. Other raw CRS, Global Fund, and WHO downloads under `data/raw/funding/` stay gitignored.
