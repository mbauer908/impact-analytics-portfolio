import marimo

__generated_with = "0.9.0"

app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    import marimo as mo

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_ranking import load_conversions, score

    mo.md(
        """
        # Wellbeing-years and the life-saving programs

        The brief uses published Happier Lives Institute totals.
        GiveDirectly and StrongMinds are survey-based. Bed nets are a
        charity-wide range that moves with the value of a saved life.
        Vitamin A and seasonal chemoprevention have no published WELLBY estimate.
        The slider below applies one factor to GiveWell’s cost per death.
        That cannot reorder the life-saving programs.
        """
    )
    return mo, load_conversions, score


@app.cell
def _(load_conversions, mo):
    spec = load_conversions()
    factor = mo.ui.slider(
        start=0, stop=8, step=0.1, value=spec["wellby"]["wellbys_per_year_of_life"],
        label="WELLBYs credited per year of life saved",
    )
    factor
    return factor, spec


@app.cell
def _(factor, mo, score, spec):
    best = score(spec, float(factor.value), "best")
    median = score(spec, float(factor.value), "median")
    show = [
        "charity",
        "geography",
        "cost_per_u5_death_usd",
        "life_years_per_1000",
        "wellbys_per_1000",
        "rank_life_years",
        "rank_wellby",
    ]
    mo.vstack(
        [
            mo.md("**Strongest geography**"),
            best[show],
            mo.md("**Median geography**"),
            median[show],
        ]
    )
    return


@app.cell
def _(mo):
    from pathlib import Path

    fig = Path(__file__).resolve().parent / "figures"
    mo.vstack(
        [
            mo.md("Figures at the baseline factor of 5, from `run_ranking.py`."),
            mo.image(src=str(fig / "two_rankings.png")),
            mo.image(src=str(fig / "wellby_sensitivity.png")),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
