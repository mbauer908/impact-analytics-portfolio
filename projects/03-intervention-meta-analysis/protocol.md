# Protocol — cash transfers → household consumption (locked before pooling)

Written **before** looking at the forest plot / pooled estimate. Do not edit inclusion decisions after seeing the pool unless logged as a post-hoc robustness note in `brief.md`.

## Decision question

Is the pooled effect of cash transfers on **total household consumption** large enough, given cost and heterogeneity, that a grantmaker should treat consumption gains as a reliable near-term outcome of cash in LMIC settings studied—and what is a transparent **cost per 10% consumption gain** for a GiveDirectly-like transfer?

## PICOS

| Element | Choice |
|---|---|
| **Population** | Households in low- and middle-income countries |
| **Intervention** | Non-contributory **cash transfers** (UCT or CCT). Cash-plus / graduation / public works **out** of primary pool |
| **Comparator** | No transfer / delayed entry / pure control (as in the source evaluation) |
| **Outcome** | **Total household consumption / expenditure** (food+nonfood). Prefer per-capita or per-adult-equivalent |
| **Study design** | RCT preferred; high-quality quasi-experimental (DID / matching) allowed when the estimate is already standardized in a 3ie-linked review |

## Effect metric (one family)

**Proportionate change** in mean total consumption relative to the comparison mean (or baseline mean when that is how the evaluation reports % effects).

- If the paper reports **log points**, convert with \(\exp(\beta)-1\) and delta-method SE \(\approx \exp(\beta)\cdot\mathrm{SE}(\beta)\).
- If the paper reports a **level** impact and a comparison/baseline mean, use \(\hat\beta / \bar y\) and \(\mathrm{SE}(\hat\beta)/\bar y\).
- If a systematic review already reports proportionate change + CI (Kabeer & Waddington 2015), use those; SE from CI as \((\mathrm{U}-\mathrm{L})/(2\cdot 1.96)\).

**Out of primary metric:** poverty headcount pp, food share, SMD-only rows without a consumption % path.

## Inclusion

1. Estimate is for **total** (or nondurable total) household consumption/expenditure.
2. Effect and a usable SE (published SE, t-stat, or 95% CI) are available—or, for at most two rows, a **conservative** SE implied by reported significance stars (document `se_method`).
3. One preferred estimate **per program** (prefer endline / primary ITT; prefer total over food-only).
4. Transfer is cash (UCT or CCT), not vouchers-only or in-kind food.

## Exclusion (pre-specified)

- Food-only or education-only expenditure as the sole outcome.
- Enterprise grants / big-push graduation packages as the primary arm (cash-plus livelihoods).
- Pure labor-supply or poverty-headcount outcomes without a consumption estimate.
- Duplicate estimates of the same program wave (keep one).
- Effects measured only after program exit unless labeled as a robustness row (`include=0`).

## Heterogeneity rule (when *not* to trust a single pool)

Treat the pooled mean as **decision-grade** only if:

- the random-effects 95% CI excludes zero, **and**
- I² is interpreted with the **prediction interval**: if the 95% prediction interval **crosses zero**, say so plainly (effects may be null in a new similar setting) even if the mean CI does not.

If I² > 75% **and** the prediction interval crosses zero, lead the brief with heterogeneity / transfer-size context rather than a single headline %.

## Cost conversion (Day 4)

Anchor on a **GiveDirectly-like** all-in cost per household (~$1,000 transfer + ~10% delivery, order-of-magnitude from Haushofer & Shapiro 2016 program costs).  
Cost per 10 ppt consumption gain ≈ (cost per household) / (pooled proportionate effect / 0.10), with Monte Carlo on both the pooled effect and cost.

## Search / extraction frame

**Primary frame:** 3ie Development Evidence / systematic-review repository (cash transfers).  
**Fallback used here:** extract standardized consumption effects from (a) Kabeer & Waddington (2015) 3ie-linked CCT meta-analysis tables and (b) primary evaluation reports for major UCTs (GiveDirectly, Zambia CGP, Kenya HSNP, Malawi SCTP, Nicaragua Atención a Crisis). Document sources in `extraction.csv`.
