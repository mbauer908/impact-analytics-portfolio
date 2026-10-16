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
        # Funding vs burden gap

        Pipeline (Day 5–6):

        1. Download GBD DALYs for one cause family, most recent comparable year.
        2. Download OECD CRS disbursements; filter by `cause_crosswalk.yaml`.
        3. Inner join on ISO3; compute DALYs per dollar and log-residual neglectedness.
        4. Map and write the top-20 table into `brief.md`.

        Put extracts in `data/raw/` (gitignored) and a small processed table in
        `data/processed/funding_burden_preview.csv` if it is small enough to commit.
        """
    )
    return Path, mo, pd, yaml


@app.cell
def _(Path, yaml):
    crosswalk = yaml.safe_load(
        (Path(__file__).resolve().parent / "cause_crosswalk.yaml").read_text()
    )
    crosswalk
    return (crosswalk,)


@app.cell
def _(mo, pd):
    preview = pd.DataFrame(
        {
            "iso3": ["EXAMPLE"],
            "dalys": [None],
            "aid_usd": [None],
            "dalys_per_million_usd": [None],
        }
    )
    mo.md("Replace this stub frame with the joined GBD–CRS table.")
    preview
    return (preview,)


if __name__ == "__main__":
    app.run()
