# 02 — Funding vs burden gap (quantitative neglectedness)

Join aid/philanthropy flows with GBD burden to find cause × country cells with high need and little funding.

**Status.** Scaffold. Pick one cause family on Day 5 (malaria, NTDs, or nutrition).

## Data

- OECD CRS disbursements (purpose codes)
- Optional IATI for foundations/NGOs
- IHME GBD DALYs and deaths
- Crosswalk: `cause_crosswalk.yaml`

## Run

```bash
marimo edit projects/02-funding-burden-gap/notebook.py
```

## Deliverables

- [ ] Crosswalk YAML you would defend in a grant meeting
- [ ] Ranked gap table (CSV)
- [ ] One map
- [ ] `brief.md` (Fieldshaper-style scan)
