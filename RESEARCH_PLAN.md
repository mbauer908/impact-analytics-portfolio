# Research plan — 10–14 day sprint

**Goal.** Six portfolio-ready analyses, each with a notebook and a short decision memo, completed in 1–2 weeks of focused work (~6–8 hours/day, ~70–90 hours total).

**Operating rule.** Optimize for *evaluator-quality writing and transparent uncertainty*, not for covering every country, charity, or scenario. One object of analysis per project. If a data source blocks you for more than half a day, fall back to the documented alternative and write the limitation in the brief.

**Portfolio thesis.** You can take a real allocation question, quantify it with open data, show what would change the conclusion, and write it so a grantmaker can act.

---

## Cadence

Treat this as two sprints. Week 1 is global-health / philanthropy (GiveWell + Fieldshaper). Week 2 is frameworks + U.S. climate/energy (insurance and policy).

| Day | Focus | Done when |
|---|---|---|
| **0 (2–3h)** | Env, GitHub, data accounts (NREL, OECD, IHME downloads) | `marimo edit` works; keys in `.env` |
| **1** | 01 GiveWell — parameterize AMF or VAS from the public spreadsheet | Parameter table with sources; model reproduces GiveWell point estimate ±10% |
| **2** | 01 GiveWell — Monte Carlo, tornado, brief | 20k draws; top 5 drivers; `brief.md` v1 |
| **3** | 03 Meta-analysis — extract 3ie studies (cash transfers *or* deworming) | Extraction sheet ≥8 studies with effect, SE, N, cost if available |
| **4** | 03 Meta-analysis — random-effects pool, heterogeneity, cost per outcome | Forest plot + `brief.md` v1 |
| **5** | 02 Funding–burden — join CRS/IATI + GBD for one year, cause × country | Gap ranking for a cause family (e.g. NTDs or malaria) |
| **6** | 02 Funding–burden — maps, robustness (alt burden metric), brief | `brief.md` v1 |
| **7** | Buffer / polish 01–03; start 04 moral-weight table | Week-1 projects have figures + briefs |
| **8** | 04 DALY vs WELLBY — convert 4–5 charities under both units | Ranking table |
| **9** | 04 Divergence brief; start 05 data ingest (SLR + SVI) | `brief.md` v1 |
| **10** | 05 MA flood — overlay SLR inundation with parcels/SVI for 1–2 coastal towns or a county | Exposure counts by vulnerability quartile |
| **11** | 05 brief; start 06 AFDC + ACS | `brief.md` v1 |
| **12** | 06 EV deserts — stations vs density/income; buffers + simple access metric | Underserved tract list |
| **13** | 06 brief; repo README polish; cross-links between projects | All six briefs readable |
| **14** | Optional stretch: one “application packet” PDF (3 strongest briefs) | Packet ready to attach |

If you only have **one week**, ship 01, 03, and 02 (in that order). Those three are the strongest GiveWell / grantmaking set. Park 04–06 as scoped follow-ons with READMEs already in the repo.

---

## Project scopes (in / out)

### 01 — Stress-test a GiveWell CEA

**Question.** For Against Malaria Foundation (LLINs) *or* Helen Keller Intl vitamin A, which parameters dominate uncertainty in cost per outcome, and how often does the charity fall below a funding bar?

**In**
- Recode the published GiveWell point-estimate chain into explicit distributions (lognormal costs, beta shares, triangular expert ranges).
- Monte Carlo (n ≥ 20,000).
- Rank-correlation tornado + one-way sensitivity on the top 5.
- Compare to GiveWell’s published point estimate as a calibration check.
- 2-page note: “Would a skeptical prior change the funding decision?”

**Out**
- Full replication of every GiveWell adjustment (leverage, funging, crowding-in) unless it is a top driver.
- Bayesian elicitation interviews.
- Multiple charities (save that comparison for 04).

**Primary source.** GiveWell CEA spreadsheets: https://www.givewell.org/how-we-work/our-criteria/cost-effectiveness/cost-effectiveness-models

**Fallback.** If spreadsheet parsing eats the day, use the documented parameter table in `projects/01-givewell-cea-uncertainty/parameters.yaml` (illustrative, labeled as such) and treat calibration as a limitation.

**Deliverables.** `notebook.py`, `parameters.yaml`, `figures/tornado.png`, `figures/cea_distribution.png`, `brief.md`

---

### 02 — Funding vs burden (“neglectedness”)

**Question.** Which cause × country cells have high 2019/2021 GBD burden (DALYs) and low 2019–2022 development finance?

**In**
- One snapshot year (or 3-year average) for disbursements.
- One cause family (malaria / NTDs / nutrition — pick one on Day 5 morning).
- OECD CRS purpose codes mapped to GBD causes (explicit crosswalk in YAML).
- Metric: `log(DALYs) − log(aid + ε)` and a simple rank of “DALYs per $`.
- Robustness: swap DALYs for deaths; exclude humanitarian codes.

**Out**
- Full IATI activity-level NLP.
- All GBD causes. All years as a panel model.

**Sources.** OECD CRS, IATI Datastore API, IHME GBD Results (CSV download — account may be required).

**Fallback.** Use IHME GBD and a published CRS extract / World Bank WDI health ODA if OECD SDMX is painful. IATI as a supplement for philanthropy/NGO flows, not the spine.

**Deliverables.** Crosswalk YAML, ranked CSV, 1 map, `brief.md` framed as a Fieldshaper-style scan.

---

### 03 — Meta-analysis of one intervention

**Question.** What is the pooled effect of **unconditional/conditional cash transfers on consumption or poverty** *or* **mass deworming on weight/schooling**, how heterogeneous is it, and what is a back-of-envelope cost per outcome?

**In**
- ≥8 independent estimates from 3ie (and, if needed, a published systematic review).
- Random-effects pool (DerSimonian–Laird or REML), I², prediction interval.
- One cost-per-outcome conversion using a published cost and the pooled effect (with MC from project 01 helpers).
- Exclusion rules written *before* looking at the forest plot.

**Out**
- Individual participant data.
- Full GRADE or Cochrane-style RoB 2 on every study (do a light RoB tag instead).
- Multiple outcomes unless the first is too thin.

**Source.** https://developmentevidence.3ieimpact.org/

**Fallback.** Use a published review’s effect table (e.g. Bastagli et al. on cash; Taylor-Robinson / Welch on deworming) and be explicit that 3ie was the intended frame.

**Deliverables.** `extraction.csv`, forest plot, `brief.md`

---

### 04 — DALY vs WELLBY ranking

**Question.** Rank the same 4–5 charities on (a) GiveWell-style DALYs / $ and (b) WELLBYs / $, and explain every rank change.

**In**
- Charities: AMF, Malaria Consortium (SMC), HKI VAS, GiveDirectly. Optional: StrongMinds or a HLI-evaluated program as the WELLBY-native contrast.
- Transparent conversion: life saved → years of life → WELLBYs via a stated WELLBYs-per-year-of-life (or HLI published conversions), plus income/consumption → WELLBYs for GiveDirectly.
- One-way sensitivity on the conversion factor — that *is* the result.

**Out**
- A new moral-weights survey.
- Claiming either unit is “correct.”

**Sources.** GiveWell CEAs; Happier Lives Institute reports; Clark et al. / Frijters WELLBY literature.

**Deliverables.** Ranking table, 3-page brief on *why* rankings move (units, time, suffering vs death).

---

### 05 — Coastal flood exposure in Massachusetts

**Question.** Under an intermediate 2050 sea-level scenario, how many parcels and socially vulnerable residents in **one coastal county or two towns** (e.g. Revere–Winthrop, New Bedford, or Barnstable) are in the inundation zone?

**In**
- NOAA / NOAA-derived SLR inundation polygon for one scenario + year.
- Parcels (MassGIS) or building footprints if parcels are too heavy.
- CDC/ATSDR SVI or MA environmental justice block groups.
- Simple overlay: counts, value at risk if assessed value is in the parcel file, SVI quartiles.

**Out**
- Statewide mosaic on Day 10.
- Hydrodynamic modeling, wave action, groundwater.
- Insurance pricing (you can *discuss* it in the brief using your background without building a ratemaking model).

**Sources.** NOAA SLR Viewer / data; MassGIS; CDC SVI; NOAA tides for local SLR context.

**Fallback.** Use census block groups instead of parcels; still overlay SVI.

**Deliverables.** Map, exposure table, `brief.md` (risk + equity, written for a state/climate-adaptation audience).

---

### 06 — EV charging deserts

**Question.** Which census tracts in **one metro** (Boston metro recommended, to reuse MA context) have low public L2/DCFC access relative to population and low income?

**In**
- NREL AFDC stations (API).
- ACS population, median income, vehicle access if available.
- Access metric: stations (or plugs) per 10k people within 1 km buffer *or* distance to nearest DCFC. Prefer buffers first; network distance only if OSM routing is easy.
- Flag tracts in the worst access quartile *and* bottom income quartile.

**Out**
- National coverage.
- Full routing / travel-time matrix unless geopandas buffers are too crude *and* you have leftover time on Day 12.

**Sources.** NREL AFDC API (`NREL_API_KEY`); Census ACS via API or download.

**Deliverables.** Map, tract table, `brief.md` for an energy-transition / equity audience.

---

## Shared methods (do once, reuse)

Use `src/impact_analytics/monte_carlo.py` for:
- GiveWell parameter uncertainty (01)
- Cost-per-outcome around the pooled effect (03)
- WELLBY conversion-factor uncertainty (04)

Keep a single visual language: one lead figure, one tornado or robustness panel, one table a program officer could paste into a memo.

Every brief uses this skeleton:

1. **Decision** (one paragraph, first)
2. Question and why it matters
3. Data and method (including what you did *not* do)
4. Results
5. What would change my mind
6. Limitations and next measurement

---

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| GiveWell xlsx is a nest of named ranges | High | Cap reverse-engineering at 4 hours; use `parameters.yaml` + cite cells |
| GBD / CRS cause crosswalk is ambiguous | High | Publish the crosswalk; sensitivity on 2 mappings |
| 3ie export is thin for your outcome | Medium | Supplement from a published review; reduce N, keep methods honest |
| MassGIS parcel file is huge | Medium | Clip to 1–2 towns immediately |
| AFDC rate limits / no key | Low | Static station CSV download from AFDC |
| Scope creep on Day 4 or 10 | High | Time-box; ship the brief with “would measure next” |

---

## Application mapping

| Audience | Lead with | Supporting |
|---|---|---|
| GiveWell research | 01 + 03 | 04 |
| Fieldshaper / grantmaking | 02 + 03 | 01 |
| Climate / insurance / state policy | 05 | 06 |
| Energy transition / equity | 06 | 05 |

Do not wait until Day 14 to write. Draft `brief.md` on the same day as the first result. The notebook is evidence; the brief is the portfolio piece.
