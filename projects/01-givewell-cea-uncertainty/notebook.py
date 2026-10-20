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
        # Stress-testing GiveWell's AMF CEA (Guinea)

        Convert GiveWell point estimates into distributions, simulate cost per
        under-5 death averted, and rank which assumptions dominate uncertainty.

        **Calibration:** `parameters.yaml` is sourced to GiveWell's public AMF
        workbook (Guinea). At input *modes*, the chain should reproduce Simple CEA
        cost per U5 death averted (about **$2,225**). Monte Carlo medians can drift
        because several inputs are asymmetric triangulars.
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
        Working bars ($5k / $10k) are **illustrative**, not GiveWell's funding threshold.
        Median cost per U5 death averted: **${summary['median']:,.0f}**
        (5–95%: ${summary['p5']:,.0f} – ${summary['p95']:,.0f}).
        Share below $5k: **{summary['share_below_5000']:.0%}**.
        """
    )
    summary
    return s, summary


@app.cell
def _(Path, df, plt, spec):
    fig_dir = Path(__file__).resolve().parent / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    s_plot = df["cost_per_death_averted"]
    gw = spec["meta"]["givewell_point_estimate_placeholder"]

    xmax = float(s_plot.quantile(0.99))
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.hist(
        s_plot[s_plot <= xmax],
        bins=60,
        color="#3b6d9a",
        edgecolor="white",
        linewidth=0.3,
    )
    ax.axvline(s_plot.median(), color="black", linestyle="--", label=f"median ${s_plot.median():,.0f}")
    if gw is not None:
        ax.axvline(gw, color="#c47b3a", linestyle="-", label=f"GiveWell point ${gw:,.0f}")
    ax.set_xlim(float(s_plot.min()) * 0.95, xmax)
    ax.set_xlabel("Cost per under-5 death averted (USD)")
    ax.set_ylabel("Monte Carlo draws")
    ax.set_title("AMF (Guinea): cost per U5 death averted — 20,000 draws")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(fig_dir / "cea_distribution.png", dpi=160)
    fig
    return ax, fig, fig_dir, gw, s_plot, xmax


@app.cell
def _(df, fig_dir, plt, spearman_tornado):
    inputs = [
        "cost_per_net",
        "nets_per_person_covered",
        "years_of_net_efficacy",
        "usage_rate",
        "protective_efficacy",
        "malaria_deaths_per_1000_py",
        "philanthropic_cost_share",
    ]
    # Omit adjustment_factor: held at a point mass (no Spearman).
    tornado = spearman_tornado(df, "log10_cost_per_death", inputs)

    fig2, ax2 = plt.subplots(figsize=(7.5, 4.2))
    ordered = tornado.sort_values("spearman")
    colors = ["#3b6d9a" if v < 0 else "#c47b3a" for v in ordered["spearman"]]
    ax2.barh(ordered["input"], ordered["spearman"], color=colors)
    ax2.axvline(0, color="black", linewidth=0.8)
    ax2.set_xlabel("Spearman ρ with log10(cost per U5 death averted)")
    ax2.set_title("Which assumptions drive uncertainty? (Guinea AMF)")
    fig2.tight_layout()
    fig2.savefig(fig_dir / "tornado.png", dpi=160)
    fig2
    return ax2, colors, fig2, inputs, ordered, tornado


@app.cell
def _(mo, summary, tornado):
    top5 = tornado.head(5)
    lines = "\n".join(
        f"        {i}. `{r.input}` (ρ={r.spearman:+.2f})"
        for i, r in enumerate(top5.itertuples(), 1)
    )
    mo.md(
        f"""
        ## Day 2 status

        Figures written to `figures/cea_distribution.png` and `figures/tornado.png`.
        Decision write-up is in `brief.md`.

        Median **${summary['median']:,.0f}** (5–95%: ${summary['p5']:,.0f}–${summary['p95']:,.0f}).
        Share below $5k: **{summary['share_below_5000']:.0%}**.

        Top drivers:
{lines}
        """
    )
    return lines, top5


if __name__ == "__main__":
    app.run()
