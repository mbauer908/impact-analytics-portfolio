import marimo

__generated_with = "0.9.0"

app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import pandas as pd
    import yaml

    proj = Path(__file__).resolve().parent
    mo.md(
        """
        # Funding vs burden: malaria

        Rules live in `cause_crosswalk.yaml`. The ranked table and figures
        are produced by `run_funding_gap.py`. Aid is OECD purpose 12262 plus
        an annualized Global Fund malaria allocation. Burden is WHO deaths,
        with a second rank on IHME GBD 2023 malaria DALYs for 2021.
        """
    )
    return Path, mo, pd, proj, yaml


@app.cell
def _(proj, yaml):
    crosswalk = yaml.safe_load((proj / "cause_crosswalk.yaml").read_text())
    crosswalk
    return (crosswalk,)


@app.cell
def _(pd, proj):
    ranked = pd.read_csv(proj / "funding_burden_ranked.csv")
    ranked.head(15)
    return (ranked,)


if __name__ == "__main__":
    app.run()
