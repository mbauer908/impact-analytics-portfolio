"""Inverse-variance meta-analysis helpers (DerSimonian–Laird random effects)."""

from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd
from scipy import stats


def der_simonian_laird(
    effects: np.ndarray,
    ses: np.ndarray,
) -> dict[str, float]:
    """Random-effects pool with DL τ², I², and approximate 95% prediction interval."""
    y = np.asarray(effects, dtype=float)
    se = np.asarray(ses, dtype=float)
    if len(y) < 2:
        raise ValueError("Need ≥2 estimates")
    if np.any(se <= 0) or np.any(~np.isfinite(y)) or np.any(~np.isfinite(se)):
        raise ValueError("Effects and SEs must be finite and SE > 0")

    v = se**2
    w = 1.0 / v
    y_fe = float(np.sum(w * y) / np.sum(w))
    q = float(np.sum(w * (y - y_fe) ** 2))
    k = len(y)
    c = float(np.sum(w) - np.sum(w**2) / np.sum(w))
    tau2 = max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0

    w_re = 1.0 / (v + tau2)
    y_re = float(np.sum(w_re * y) / np.sum(w_re))
    se_re = float(np.sqrt(1.0 / np.sum(w_re)))
    z = y_re / se_re
    p = float(2 * (1 - stats.norm.cdf(abs(z))))

    i2 = max(0.0, (q - (k - 1)) / q) if q > 0 else 0.0
    # Higgins et al. approximate prediction interval for a new study
    t_crit = float(stats.t.ppf(0.975, df=max(k - 2, 1)))
    pred_se = float(np.sqrt(se_re**2 + tau2))
    pred_lo = y_re - t_crit * pred_se
    pred_hi = y_re + t_crit * pred_se

    return {
        "k": float(k),
        "mu_fe": y_fe,
        "mu_re": y_re,
        "se_re": se_re,
        "ci_lo": y_re - 1.96 * se_re,
        "ci_hi": y_re + 1.96 * se_re,
        "z": float(z),
        "p": p,
        "q": q,
        "tau2": tau2,
        "tau": float(np.sqrt(tau2)),
        "i2": i2,
        "pred_lo": pred_lo,
        "pred_hi": pred_hi,
    }


def _included_mask(df: pd.DataFrame) -> pd.Series:
    if "include" not in df.columns:
        return pd.Series(True, index=df.index)
    raw = df["include"]
    return pd.to_numeric(raw, errors="coerce").fillna(0).astype(int).eq(1)


def pool_extraction(df: pd.DataFrame, effect_col: str = "effect", se_col: str = "se") -> dict[str, float]:
    usable = df.dropna(subset=[effect_col, se_col]).copy()
    usable = usable.loc[_included_mask(usable)]
    return der_simonian_laird(usable[effect_col].to_numpy(), usable[se_col].to_numpy())


def study_weights(df: pd.DataFrame, tau2: float, effect_col: str = "effect", se_col: str = "se") -> pd.DataFrame:
    out = df.dropna(subset=[effect_col, se_col]).copy()
    out = out.loc[_included_mask(out)]
    out["var"] = out[se_col] ** 2
    out["w_fe"] = 1.0 / out["var"]
    out["w_re"] = 1.0 / (out["var"] + tau2)
    out["w_re_pct"] = 100.0 * out["w_re"] / out["w_re"].sum()
    return out.reset_index(drop=True)


def summarize_pool(pool: Mapping[str, float]) -> str:
    return (
        f"RE μ={100 * pool['mu_re']:.1f}% "
        f"(95% CI {100 * pool['ci_lo']:.1f}–{100 * pool['ci_hi']:.1f}%; "
        f"I²={100 * pool['i2']:.0f}%; "
        f"pred. {100 * pool['pred_lo']:.1f}–{100 * pool['pred_hi']:.1f}%)"
    )
