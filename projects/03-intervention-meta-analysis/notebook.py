import marimo

__generated_with = "0.9.0"

app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import numpy as np
    import pandas as pd
    import statsmodels.mixed_linear_model as mlm

    mo.md(
        """
        # Meta-analysis pipeline

        1. Fill `extraction.csv` from 3ie (one intervention, one outcome family).
        2. Inverse-variance random-effects pool (start with DerSimonian–Laird by hand;
           statsmodels mixed models as a check).
        3. Forest plot; I²; 95% prediction interval.
        4. Cost per outcome using `impact_analytics.monte_carlo`.
        """
    )
    return Path, mlm, mo, np, pd


@app.cell
def _(Path, pd):
    extract = pd.read_csv(Path(__file__).resolve().parent / "extraction.csv")
    extract
    return (extract,)


@app.cell
def _(extract, mo, np):
    usable = extract.dropna(subset=["effect", "se"])
    if len(usable) < 3:
        mo.md("Need ≥3 rows with effect and SE. Extraction is the Day 3 job.")
        pooled = None
    else:
        w = 1 / (usable["se"] ** 2)
        pooled = float(np.average(usable["effect"], weights=w))
        mo.md(f"Fixed-effect placeholder (not the final model): **{pooled:.3f}**")
    return pooled, usable


if __name__ == "__main__":
    app.run()
