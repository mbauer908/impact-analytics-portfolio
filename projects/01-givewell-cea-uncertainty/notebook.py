import marimo

__generated_with = "0.9.0"

app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import yaml

    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "src"))

    from impact_analytics.monte_carlo import (
        Dist,
        beta_from_mean_phi,
        lognormal_from_mean_cv,
        run_mc,
        spearman_tornado,
    )

    mo.md(
        """
        # Stress-testing a GiveWell-style LLIN CEA

        Convert point estimates into distributions, simulate cost per death averted,
        and rank which assumptions dominate uncertainty.

        **Calibration rule:** once `parameters.yaml` is filled from GiveWell's spreadsheet,
        the median of this model should land near their published point estimate.
        Until then, treat numbers as a methods demonstration.
        """
    )
    return (
        Dist,
        Path,
        beta_from_mean_phi,
        lognormal_from_mean_cv,
        mo,
        np,
        pd,
        plt,
        root,
        run_mc,
        spearman_tornado,
        yaml,
    )


@app.cell
def _(Path, yaml):
    param_path = Path(__file__).resolve().parent / "parameters.yaml"
    spec = yaml.safe_load(param_path.read_text())
    spec["meta"]
    return param_path, spec


@app.cell
def _(Dist, beta_from_mean_phi, lognormal_from_mean_cv, spec):
    def dist_from_spec(name: str, p: dict) -> Dist:
        kind = p["kind"]
        if kind == "lognormal_mean_cv":
            mu, sigma = lognormal_from_mean_cv(p["mean"], p["cv"])
            return Dist(name, "lognormal", {"mu": mu, "sigma": sigma})
        if kind == "beta_mean_phi":
            a, b = beta_from_mean_phi(p["mean"], p["phi"])
            return Dist(name, "beta", {"a": a, "b": b})
        if kind == "triangular":
            return Dist(
                name,
                "triangular",
                {"left": p["left"], "mode": p["mode"], "right": p["right"]},
            )
        if kind == "point":
            return Dist(name, "point", {"value": p["value"]})
        raise ValueError(kind)

    dists = {name: dist_from_spec(name, p) for name, p in spec["parameters"].items()}
    list(dists)
    return dist_from_spec, dists


@app.cell
def _(dists, np, run_mc):
    def outcomes(d: dict) -> dict:
        nets = 1.0  # per $ we will scale by cost
        # Deaths averted per net:
        # 1 net covers (1 / nets_per_person) people for years_of_net_efficacy,
        # used at usage_rate, with protective_efficacy against baseline mortality.
        person_years = (
            (1.0 / d["nets_per_person_covered"])
            * d["years_of_net_efficacy"]
            * d["usage_rate"]
        )
        deaths_per_py = d["malaria_deaths_per_1000_py"] / 1000.0
        deaths_averted_per_net = (
            person_years
            * deaths_per_py
            * d["protective_efficacy"]
            * d["adjustment_factor"]
        )
        philanthropic_cost_per_net = d["cost_per_net"] * d["philanthropic_cost_share"]
        cost_per_death = philanthropic_cost_per_net / np.clip(
            deaths_averted_per_net, 1e-12, None
        )
        return {
            "deaths_averted_per_net": deaths_averted_per_net,
            "cost_per_death_averted": cost_per_death,
            "log10_cost_per_death": np.log10(cost_per_death),
        }

    df = run_mc(dists, outcomes, n=20_000, seed=42)
    df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).T
    return df, outcomes


@app.cell
def _(df, mo, pd):
    s = df["cost_per_death_averted"]
    summary = pd.Series(
        {
            "median": s.median(),
            "p5": s.quantile(0.05),
            "p95": s.quantile(0.95),
            "p95/p5": s.quantile(0.95) / s.quantile(0.05),
            "share_below_5000": (s < 5_000).mean(),
            "share_below_10000": (s < 10_000).mean(),
        }
    )
    mo.md(
        f"""
        Working bars ($5k and $10k per death averted) are **illustrative**, not GiveWell's bar.
        Median cost per death averted: **${summary['median']:,.0f}**
        (5–95%: ${summary['p5']:,.0f} – ${summary['p95']:,.0f}).
        """
    )
    summary
    return s, summary


@app.cell
def _(df, plt):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df["cost_per_death_averted"].clip(upper=df["cost_per_death_averted"].quantile(0.99)), bins=60, color="#3b6d9a")
    ax.axvline(df["cost_per_death_averted"].median(), color="black", linestyle="--", label="median")
    ax.set_xlabel("Cost per death averted (USD)")
    ax.set_ylabel("Draws")
    ax.legend()
    ax.set_title("Monte Carlo: cost per death averted")
    fig.tight_layout()
    fig
    return ax, fig


@app.cell
def _(df, plt, spearman_tornado):
    inputs = [
        "cost_per_net",
        "nets_per_person_covered",
        "years_of_net_efficacy",
        "usage_rate",
        "protective_efficacy",
        "malaria_deaths_per_1000_py",
        "adjustment_factor",
        "philanthropic_cost_share",
    ]
    tornado = spearman_tornado(df, "log10_cost_per_death", inputs)

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ordered = tornado.sort_values("spearman")
    ax2.barh(ordered["input"], ordered["spearman"], color="#c47b3a")
    ax2.axvline(0, color="black", linewidth=0.8)
    ax2.set_xlabel("Spearman ρ with log10(cost per death averted)")
    ax2.set_title("Which assumptions drive uncertainty?")
    fig2.tight_layout()
    fig2
    return ax2, fig2, inputs, ordered, tornado


@app.cell
def _(mo, tornado):
    top = tornado.iloc[0]["input"]
    mo.md(
        f"""
        ## Next (Day 2)

        1. Replace every row in `parameters.yaml` with GiveWell spreadsheet cells.
        2. Paste their published point estimate into `meta.givewell_point_estimate_placeholder`.
        3. Save the histogram and tornado into `figures/`.
        4. Write the decision paragraph in `brief.md`.

        Current top driver (illustrative): **{top}**.
        """
    )
    return (top,)


if __name__ == "__main__":
    app.run()
