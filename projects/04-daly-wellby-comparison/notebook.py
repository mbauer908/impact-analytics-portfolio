import marimo

__generated_with = "0.9.0"

app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import pandas as pd
    import yaml

    mo.md(
        """
        # DALY vs WELLBY ranking

        Fill `conversions.yaml` with GiveWell point estimates (or project 01 medians).
        Rank on (1 / cost_per_DALY) vs WELLBYs per dollar. Sweep
        `wellbys_per_year_of_healthy_life` — if ranks flip, that is the finding.
        """
    )
    return Path, mo, pd, yaml


@app.cell
def _(Path, yaml):
    conv = yaml.safe_load(
        (Path(__file__).resolve().parent / "conversions.yaml").read_text()
    )
    conv
    return (conv,)


if __name__ == "__main__":
    app.run()
