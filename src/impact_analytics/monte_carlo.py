"""Lightweight Monte Carlo and sensitivity helpers for CEA models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Dist:
    """A named sampling distribution."""

    name: str
    kind: str
    params: Mapping[str, float]

    def sample(self, rng: np.random.Generator, n: int) -> np.ndarray:
        p = self.params
        if self.kind == "lognormal":
            return rng.lognormal(mean=p["mu"], sigma=p["sigma"], size=n)
        if self.kind == "normal":
            return rng.normal(loc=p["mu"], scale=p["sigma"], size=n)
        if self.kind == "beta":
            return rng.beta(p["a"], p["b"], size=n)
        if self.kind == "uniform":
            return rng.uniform(p["low"], p["high"], size=n)
        if self.kind == "triangular":
            return rng.triangular(p["left"], p["mode"], p["right"], size=n)
        if self.kind == "point":
            return np.full(n, p["value"])
        raise ValueError(f"Unknown distribution kind: {self.kind}")


def lognormal_from_mean_cv(mean: float, cv: float) -> tuple[float, float]:
    """Convert a positive mean and coefficient of variation to lognormal mu, sigma."""
    variance = (mean * cv) ** 2
    sigma2 = np.log(1 + variance / mean**2)
    mu = np.log(mean) - 0.5 * sigma2
    return float(mu), float(np.sqrt(sigma2))


def beta_from_mean_phi(mean: float, phi: float) -> tuple[float, float]:
    """Beta parameterization by mean in (0,1) and precision phi > 0."""
    a = mean * phi
    b = (1 - mean) * phi
    return float(a), float(b)


def run_mc(
    dists: Mapping[str, Dist],
    outcome_fn: Callable[[dict[str, np.ndarray]], dict[str, np.ndarray]],
    n: int = 20_000,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    draws = {name: dist.sample(rng, n) for name, dist in dists.items()}
    outcomes = outcome_fn(draws)
    return pd.DataFrame({**draws, **outcomes})


def spearman_tornado(df: pd.DataFrame, outcome: str, inputs: list[str]) -> pd.DataFrame:
    """Rank-correlation tornado: which inputs co-move with the outcome."""
    rows = []
    y = df[outcome]
    for col in inputs:
        rho = df[col].corr(y, method="spearman")
        rows.append({"input": col, "spearman": rho, "abs": abs(rho)})
    out = pd.DataFrame(rows).sort_values("abs", ascending=False)
    return out.reset_index(drop=True)


def one_way_sensitivity(
    baseline: Mapping[str, float],
    lows: Mapping[str, float],
    highs: Mapping[str, float],
    outcome_fn: Callable[[dict[str, float]], float],
    inputs: list[str] | None = None,
) -> pd.DataFrame:
    """Classic one-way tornado: move one input to low/high; hold others at baseline.

    ``outcome_fn`` takes a flat dict of scalar inputs and returns a scalar outcome.
    """
    names = list(inputs) if inputs is not None else list(lows)
    base_out = float(outcome_fn(dict(baseline)))
    rows = []
    for name in names:
        low_d = dict(baseline)
        high_d = dict(baseline)
        low_d[name] = float(lows[name])
        high_d[name] = float(highs[name])
        out_low = float(outcome_fn(low_d))
        out_high = float(outcome_fn(high_d))
        rows.append(
            {
                "input": name,
                "baseline": base_out,
                "low_value": float(lows[name]),
                "high_value": float(highs[name]),
                "outcome_at_low": out_low,
                "outcome_at_high": out_high,
                "swing": abs(out_high - out_low),
            }
        )
    out = pd.DataFrame(rows).sort_values("swing", ascending=False)
    return out.reset_index(drop=True)
