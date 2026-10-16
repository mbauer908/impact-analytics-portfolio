# 01 — Stress-test a GiveWell cost-effectiveness model

Convert a top charity’s point-estimate CEA into distributions, run Monte Carlo, and identify which assumptions dominate uncertainty.

**Status.** Methods notebook runs on illustrative parameters. Replace `parameters.yaml` with values from the current GiveWell spreadsheet before treating results as a funding comment.

## Run

```bash
marimo edit projects/01-givewell-cea-uncertainty/notebook.py
```

## Deliverables

- [ ] `parameters.yaml` sourced to spreadsheet cells
- [ ] Calibration vs GiveWell published point estimate
- [ ] `figures/` distribution + tornado
- [ ] `brief.md` (decision-first evaluator note)
