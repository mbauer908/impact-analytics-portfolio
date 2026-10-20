# 03 — Meta-analysis: cash transfers → consumption

**Question.** What is the pooled effect of LMIC cash transfers on **total household consumption**, how heterogeneous is it, and what is a transparent cost per 10% consumption gain?

**Choice.** Cash (UCT/CCT) rather than deworming—clearer link to GiveWell’s cash benchmark and a clean cost conversion.

## Status

Day 3–4 core complete: protocol locked, ≥8 estimates extracted, RE pool + forest + cost MC + brief.

| Deliverable | Status |
|---|---|
| `protocol.md` (exclusion rules before the forest) | done |
| `extraction.csv` (8 included programs) | done |
| Forest plot + I² + prediction interval | done |
| Cost per 10 ppt consumption gain (MC) | done |
| `brief.md` | done |

## Headline

- RE mean ≈ **+19%** consumption (95% CI +8% to +31%; k=8)
- **I² ≈ 94%**; prediction interval **crosses zero** (−21% to +59%)
- GiveDirectly-like cost per **10 ppt** consumption gain ≈ **$570**/hh (5–95% ~$355–$1,170)

## Run

```bash
source .venv/bin/activate
marimo edit projects/03-intervention-meta-analysis/notebook.py
```

Figures write to `figures/forest.png`, `figures/cost_per_10ppt.png`.

## Sources

3ie-linked Kabeer & Waddington (2015) CCT consumption table; Haushofer & Shapiro (2016); AIR Zambia CGP; Macours et al. (2012); HSNP pilot evaluation; Malawi SCTP 3ie endline report. See `extraction.csv` for cell-level citations.
