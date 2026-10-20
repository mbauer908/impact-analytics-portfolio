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

    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "src"))

    from impact_analytics.meta_analysis import pool_extraction, study_weights, summarize_pool
    from impact_analytics.monte_carlo import Dist, run_mc

    mo.md(
        """
        # Meta-analysis: cash transfers → household consumption

        Protocol locked in `protocol.md`. Extraction in `extraction.csv`.
        Random-effects DerSimonian–Laird pool → forest plot → cost per 10% consumption gain.
        """
    )
    return Dist, Path, mo, np, pd, plt, pool_extraction, root, run_mc, study_weights, summarize_pool


@app.cell
def _(Path, pd):
    proj = Path(__file__).resolve().parent
    extract = pd.read_csv(proj / "extraction.csv")
    included = extract[extract["include"] == 1].copy()
    included
    return extract, included, proj


@app.cell
def _(included, mo, pool_extraction, study_weights, summarize_pool):
    pool = pool_extraction(included)
    weighted = study_weights(included, pool["tau2"])
    mo.md(
        f"""
        ## Random-effects pool (DerSimonian–Laird)

        {summarize_pool(pool)}

        - k = {int(pool['k'])} programs
        - τ = {pool['tau']:.3f}
        - Prediction interval crosses zero: **{pool['pred_lo'] < 0 < pool['pred_hi']}**
        """
    )
    pool
    return pool, weighted


@app.cell
def _(np, plt, pool, proj, weighted):
    fig_dir = proj / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = weighted.sort_values("effect")
    y = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.errorbar(
        df["effect"],
        y,
        xerr=1.96 * df["se"],
        fmt="o",
        color="#3b6d9a",
        ecolor="#3b6d9a",
        elinewidth=1.2,
        capsize=3,
        markersize=6,
    )
    ax.axvline(0, color="black", linewidth=0.8)
    ax.axvline(pool["mu_re"], color="#c47b3a", linestyle="--", label=f"RE pool {100*pool['mu_re']:.1f}%")
    ax.axvspan(pool["ci_lo"], pool["ci_hi"], color="#c47b3a", alpha=0.15, label="95% CI (mean)")
    ax.axvspan(pool["pred_lo"], pool["pred_hi"], color="#888888", alpha=0.12, label="95% prediction")
    labels = [f"{r.program} ({r.country})" for r in df.itertuples()]
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Proportionate change in total household consumption")
    ax.set_title("Cash transfers → consumption (random-effects forest)")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(fig_dir / "forest.png", dpi=160)
    fig
    return ax, df, fig, fig_dir, labels


@app.cell
def _(Dist, mo, np, pool, run_mc):
    # Cost per 10 ppt consumption gain for a GiveDirectly-like transfer.
    cost_mean = 1100.0
    cost_cv = 0.15
    mu = np.log(cost_mean) - 0.5 * np.log(1 + cost_cv**2)
    sigma = np.sqrt(np.log(1 + cost_cv**2))

    dists = {
        "cost_per_hh": Dist("cost_per_hh", "lognormal", {"mu": float(mu), "sigma": float(sigma)}),
        "effect": Dist(
            "effect",
            "normal",
            {"mu": float(pool["mu_re"]), "sigma": float(pool["se_re"])},
        ),
    }

    def outcomes(d):
        # dollars per household for a 0.10 (10 ppt) consumption gain
        gain = np.clip(d["effect"], 1e-4, None)
        cost_per_10ppt = d["cost_per_hh"] * (0.10 / gain)
        return {"cost_per_10ppt_consumption": cost_per_10ppt}

    mc = run_mc(dists, outcomes, n=20_000, seed=7)
    s = mc["cost_per_10ppt_consumption"]
    cost_summary = {
        "median": float(s.median()),
        "p5": float(s.quantile(0.05)),
        "p95": float(s.quantile(0.95)),
    }
    mo.md(
        f"""
        ## Cost per 10% consumption gain (GiveDirectly-like)

        All-in cost ~$1,100/hh (lognormal CV 15%); effect ~ N(μ̂_RE, SE_RE).

        Median **${cost_summary['median']:,.0f}** per household for a 10 ppt consumption gain
        (5–95%: ${cost_summary['p5']:,.0f}–${cost_summary['p95']:,.0f}).
        """
    )
    cost_summary
    return cost_mean, cost_summary, cost_cv, dists, mc, mu, outcomes, s, sigma


@app.cell
def _(cost_summary, fig_dir, mo, pool, plt, s):
    import json

    fig2, ax2 = plt.subplots(figsize=(8, 3.8))
    xmax = float(s.quantile(0.99))
    ax2.hist(s[s <= xmax], bins=50, color="#3b6d9a", edgecolor="white", linewidth=0.3)
    ax2.axvline(s.median(), color="black", linestyle="--", label=f"median ${s.median():,.0f}")
    ax2.set_xlabel("USD per household for a 10 ppt consumption gain")
    ax2.set_ylabel("Monte Carlo draws")
    ax2.set_title("Cost per 10% consumption gain — uncertainty")
    ax2.legend(frameon=False)
    fig2.tight_layout()
    fig2.savefig(fig_dir / "cost_per_10ppt.png", dpi=160)

    summary = {
        "pool": pool,
        "cost_per_10ppt": cost_summary,
    }
    (fig_dir / "meta_summary.json").write_text(json.dumps(summary, indent=2, default=float))
    mo.md("Wrote `figures/forest.png`, `figures/cost_per_10ppt.png`, `figures/meta_summary.json`.")
    fig2
    return ax2, fig2, summary, xmax


if __name__ == "__main__":
    app.run()
