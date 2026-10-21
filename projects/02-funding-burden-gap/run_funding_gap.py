"""Malaria funding vs burden: CRS 12262 plus Global Fund, against WHO deaths and GBD DALYs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]
PROJ = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "funding"
FIG = PROJ / "figures"
CRS_URL = (
    "https://sdmx.oecd.org/dcd-public/rest/data/"
    "OECD.DCD.FSD,DSD_CRS@DF_CRS,1.7/DAC..12262.100._T._T.D.Q._T.."
)
WHO_URL = "https://ghoapi.azureedge.net/api/MALARIA_EST_DEATHS"
ISO_URL = (
    "https://raw.githubusercontent.com/lukes/"
    "ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
)
GEO_URL = (
    "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
)
GF_URLS = {
    "gf_allocations_2020_2022.xlsx": (
        "https://archive.theglobalfund.org/media/9227/"
        "archive_2020-2022-allocations_table_en.xlsx"
    ),
    "gf_allocations_2023_2025.xlsx": (
        "https://archive.theglobalfund.org/media/t0iphpmh/"
        "archive_2023-2025-allocations_table_en.xlsx"
    ),
}
WHO_FUNDING_URL = (
    "https://cdn.who.int/media/docs/default-source/malaria/world-malaria-reports/"
    "wmr2024_annex_4c.xlsx?sfvrsn=c551dd04_3"
)
# World malaria report names that differ from the ISO English short name.
WHO_NAME_TO_ISO = {
    "Democratic Republic of the Congo": "Congo, Democratic Republic of the",
    "United Republic of Tanzania": "Tanzania, United Republic of",
    "Bolivia (Plurinational State of)": "Bolivia, Plurinational State of",
    "Iran (Islamic Republic of)": "Iran, Islamic Republic of",
    "Venezuela (Bolivarian Republic of)": "Venezuela, Bolivarian Republic of",
}
HEADERS = {"User-Agent": "impact-analytics-portfolio"}
# GBD Compare location labels that differ from the ISO 3166 English names.
GBD_NAME_TO_ISO = {
    "Bolivia (Plurinational State of)": "Bolivia, Plurinational State of",
    "Democratic People's Republic of Korea": "Korea, Democratic People's Republic of",
    "Democratic Republic of the Congo": "Congo, Democratic Republic of the",
    "Iran (Islamic Republic of)": "Iran, Islamic Republic of",
    "Micronesia (Federated States of)": "Micronesia, Federated States of",
    "Netherlands": "Netherlands, Kingdom of the",
    "Palestine": "Palestine, State of",
    "Republic of Korea": "Korea, Republic of",
    "Republic of Moldova": "Moldova, Republic of",
    "Taiwan": "Taiwan, Province of China",
    "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
    "United Republic of Tanzania": "Tanzania, United Republic of",
    "United States Virgin Islands": "Virgin Islands (U.S.)",
    "Venezuela (Bolivarian Republic of)": "Venezuela, Bolivarian Republic of",
}


def load_rules() -> dict:
    return yaml.safe_load((PROJ / "cause_crosswalk.yaml").read_text())


def fetch_crs() -> pd.DataFrame:
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / "crs_malaria_12262.csv"
    if not path.exists():
        r = requests.get(
            CRS_URL,
            params={"startPeriod": "2019", "endPeriod": "2022", "format": "csvfilewithlabels"},
            headers=HEADERS,
            timeout=180,
        )
        r.raise_for_status()
        path.write_bytes(r.content)
    crs = pd.read_csv(path)
    crs = crs[crs["TIME_PERIOD"].between(2019, 2022)].copy()
    crs = crs[crs["RECIPIENT"].astype(str).str.fullmatch(r"[A-Z]{3}")]
    # UNIT_MULT 6 = millions of USD.
    if not (crs["UNIT_MULT"] == 6).all():
        raise ValueError("Unexpected CRS unit multiplier; check before scaling.")
    aid = (
        crs.groupby("RECIPIENT", as_index=False)
        .agg(aid_usd_m_avg=("OBS_VALUE", "mean"), crs_name=("Recipient", "first"))
    )
    aid["aid_usd"] = aid["aid_usd_m_avg"] * 1_000_000
    return aid.rename(columns={"RECIPIENT": "iso3"})


def _download(url: str, path: Path) -> None:
    if path.exists():
        return
    r = requests.get(url, headers=HEADERS, timeout=180)
    r.raise_for_status()
    path.write_bytes(r.content)


def _gf_malaria_totals(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, header=None)
    header_row = raw.index[raw.iloc[:, 0].astype(str).str.strip().eq("ISO3")]
    if len(header_row) != 1:
        raise ValueError(f"Expected one ISO3 header in {path.name}")
    df = pd.read_excel(path, header=int(header_row[0]))
    df.columns = [str(c).strip() for c in df.columns]
    iso = next(c for c in df.columns if "ISO" in c.upper())
    disease = next(c for c in df.columns if "Disease" in c)
    usd_cols = [c for c in df.columns if ("USD" in c.upper() or "US$" in c) and "Total" not in c]
    if len(usd_cols) != 1:
        raise ValueError(f"Expected one USD allocation column in {path.name}, got {usd_cols}")
    malaria = df[df[disease].astype(str).str.strip().eq("Malaria")].copy()
    malaria = malaria[malaria[iso].astype(str).str.fullmatch(r"[A-Z]{3}")]
    malaria["gf_total_usd"] = pd.to_numeric(malaria[usd_cols[0]], errors="coerce")
    if malaria["gf_total_usd"].isna().any():
        raise ValueError(f"Missing USD malaria allocation in {path.name}")
    if malaria[iso].duplicated().any():
        raise ValueError(f"Duplicate malaria country rows in {path.name}")
    return malaria[[iso, "gf_total_usd"]].rename(columns={iso: "iso3"})


def fetch_global_fund() -> pd.DataFrame:
    RAW.mkdir(parents=True, exist_ok=True)
    frames = []
    for name, url in GF_URLS.items():
        path = RAW / name
        _download(url, path)
        part = _gf_malaria_totals(path)
        period = "2020_2022" if "2020" in name else "2023_2025"
        part = part.rename(columns={"gf_total_usd": f"gf_allocation_{period}_usd"})
        frames.append(part)
    out = frames[0].merge(frames[1], on="iso3", how="outer")
    # The Fund publishes a three-year envelope. Dividing by three is the
    # annual figure used in the rank. It is not a reported disbursement.
    out["gf_annual_from_allocation_usd"] = out["gf_allocation_2020_2022_usd"] / 3
    return out


def _who_number(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.replace(",", "", regex=False)
    cleaned = cleaned.replace({"–": np.nan, "-": np.nan, "…": np.nan, "nan": np.nan})
    return pd.to_numeric(cleaned, errors="coerce")


def fetch_who_funding() -> pd.DataFrame:
    """Country-reported Global Fund and government malaria-program contributions.

    World malaria report 2024, Annex 4C. Missing years stay missing.
    The mean uses only the years the country reported.
    """
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / "wmr2024_annex_4c.xlsx"
    _download(WHO_FUNDING_URL, path)
    raw = pd.read_excel(path, header=3)
    raw.columns = [
        "who_name",
        "year",
        "gf_donor",
        "pmi",
        "world_bank",
        "uk",
        "other_donor",
        "gov_nmp",
        "blank1",
        "gf_country",
        "blank2",
        "pmi_country",
        "wb_country",
        "other_bilat",
        "who",
        "unicef",
        "other_country",
    ]
    raw["who_name"] = (
        raw["who_name"].ffill().astype(str).str.replace(r"\d+$", "", regex=True).str.strip()
    )
    raw = raw[raw["year"].isin([2021, 2022, 2023])].copy()
    raw["gov_nmp"] = _who_number(raw["gov_nmp"])
    raw["gf_country"] = _who_number(raw["gf_country"])
    raw["gf_donor"] = _who_number(raw["gf_donor"])
    names = fetch_names()
    raw["country"] = raw["who_name"].replace(WHO_NAME_TO_ISO)
    raw = raw.merge(names, on="country", how="left")
    grouped = raw.groupby("iso3", dropna=True)
    out = grouped.agg(
        who_gf_country_reported_usd=("gf_country", "mean"),
        who_gf_country_years=("gf_country", "count"),
        who_gf_donor_reported_usd=("gf_donor", "mean"),
        gov_nmp_usd=("gov_nmp", "mean"),
        gov_nmp_years=("gov_nmp", "count"),
    ).reset_index()
    return out


def add_channels(ranked: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """Replace the aid total with CRS 12262 plus a Global Fund country figure.

    Government spending is kept as its own column. It is not aid.
    """
    eps = float(rules["ranking"]["epsilon_usd"])
    out = ranked.merge(fetch_global_fund(), on="iso3", how="left")
    out = out.merge(fetch_who_funding(), on="iso3", how="left")
    out = out.rename(columns={"aid_usd": "crs_aid_usd", "log_gap": "log_gap_crs", "rank_log_gap": "rank_log_gap_crs"})
    has_allocation = out["gf_annual_from_allocation_usd"].notna()
    out["gf_annual_usd"] = out["gf_annual_from_allocation_usd"]
    out["gf_amount_source"] = np.where(has_allocation, "global_fund_country_allocation", "none")
    out["gf_timing"] = np.where(has_allocation, "allocation_divided_by_3", "none")
    # No country allocation: use the WHO country report. Do not split a regional grant.
    impute = ~has_allocation & out["who_gf_country_reported_usd"].notna()
    out.loc[impute, "gf_annual_usd"] = out.loc[impute, "who_gf_country_reported_usd"]
    out.loc[impute, "gf_amount_source"] = "imputed_who_annex_4c_country_reported_global_fund"
    out.loc[impute, "gf_timing"] = "mean_of_reported_years_2021_2023"
    out["gf_annual_usd"] = out["gf_annual_usd"].fillna(0.0)
    out["aid_usd"] = out["crs_aid_usd"] + out["gf_annual_usd"]
    out["deaths_per_million_usd"] = out["deaths"] / ((out["aid_usd"] + eps) / 1_000_000)
    out["log_gap"] = np.log(out["deaths"]) - np.log(out["aid_usd"] + eps)
    out["rank_log_gap"] = out["log_gap"].rank(ascending=False, method="min").astype(int)
    out["rank_deaths_per_usd"] = (
        out["deaths_per_million_usd"].rank(ascending=False, method="min").astype(int)
    )
    return out.sort_values("log_gap", ascending=False).reset_index(drop=True)


def aid_recommendations(ranked: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """Extra annual aid to match the median intensity of Nigeria, the DRC, and Niger."""
    peers = ranked[ranked["iso3"].isin(rules["ranking"]["peer_isos"])].copy()
    if len(peers) != 3:
        raise ValueError("Expected Nigeria, the DRC, and Niger in the ranked set.")
    per_death = float((peers["aid_usd"] / peers["deaths"]).median())
    per_daly = float((peers["aid_usd"] / peers["dalys"]).median())
    out = ranked.copy()
    out["peer_usd_per_death"] = per_death
    out["peer_usd_per_daly"] = per_daly
    out["addl_aid_from_deaths_usd"] = np.maximum(0, per_death * out["deaths"] - out["aid_usd"])
    out["addl_aid_from_dalys_usd"] = np.maximum(0, per_daly * out["dalys"] - out["aid_usd"])
    return out


def fetch_deaths(year: int) -> pd.DataFrame:
    path = RAW / "who_malaria_deaths.json"
    if not path.exists():
        r = requests.get(WHO_URL, headers=HEADERS, timeout=180)
        r.raise_for_status()
        path.write_bytes(r.content)
    payload = json.loads(path.read_text())
    rows = [
        {"iso3": row["SpatialDim"], "deaths": row["NumericValue"]}
        for row in payload["value"]
        if row["SpatialDimType"] == "COUNTRY" and row["TimeDim"] == year
    ]
    return pd.DataFrame(rows)


def fetch_names() -> pd.DataFrame:
    path = RAW / "iso3166.csv"
    if not path.exists():
        r = requests.get(ISO_URL, headers=HEADERS, timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
    names = pd.read_csv(path)
    return names.rename(columns={"alpha-3": "iso3", "name": "country"})[["iso3", "country"]]


def fetch_dalys() -> pd.DataFrame:
    path = RAW / "gbd_malaria_dalys_2021.csv"
    if not path.exists():
        raise FileNotFoundError(
            "Missing IHME extract at data/raw/funding/gbd_malaria_dalys_2021.csv"
        )
    raw = pd.read_csv(path)
    gbd = raw[
        raw["Measure"].eq("DALYs")
        & raw["Year"].eq(2021)
        & raw["Age"].eq("All ages")
        & raw["Sex"].eq("Both")
        & raw["Cause of death or injury"].eq("Malaria")
    ].copy()
    if gbd["Location"].duplicated().any():
        raise ValueError("Duplicate locations in the GBD malaria DALY extract.")
    gbd["country"] = gbd["Location"].replace(GBD_NAME_TO_ISO)
    names = fetch_names()
    gbd = gbd.merge(names, on="country", how="left")
    missing = gbd.loc[gbd["iso3"].isna(), "Location"].tolist()
    if missing:
        raise ValueError(f"Unmatched GBD location names: {missing}")
    return gbd[["iso3", "Value"]].rename(columns={"Value": "dalys"})


def add_daly_ranks(ranked: pd.DataFrame, dalys: pd.DataFrame, rules: dict) -> pd.DataFrame:
    eps = float(rules["ranking"]["epsilon_usd"])
    out = ranked.merge(dalys, on="iso3", how="left")
    missing = out.loc[out["dalys"].isna(), "country"].tolist()
    if missing:
        raise ValueError(f"No GBD DALYs for ranked countries: {missing}")
    if (out["dalys"] <= 0).any():
        raise ValueError("A ranked country has zero GBD DALYs; the log gap is undefined.")
    out["dalys_per_million_usd"] = out["dalys"] / ((out["aid_usd"] + eps) / 1_000_000)
    out["daly_log_gap"] = np.log(out["dalys"]) - np.log(out["aid_usd"] + eps)
    out["rank_daly_log_gap"] = (
        out["daly_log_gap"].rank(ascending=False, method="min").astype(int)
    )
    return out


def score(deaths: pd.DataFrame, aid: pd.DataFrame, rules: dict) -> pd.DataFrame:
    eps = float(rules["ranking"]["epsilon_usd"])
    min_deaths = float(rules["ranking"]["min_deaths"])
    out = deaths.merge(aid, on="iso3", how="left")
    names = fetch_names()
    out = out.merge(names, on="iso3", how="left")
    out["country"] = out["country"].fillna(out["crs_name"]).fillna(out["iso3"])
    out["aid_usd"] = out["aid_usd"].fillna(0.0)
    out["aid_usd_m_avg"] = out["aid_usd_m_avg"].fillna(0.0)
    out = out[out["deaths"] >= min_deaths].copy()
    out["deaths_per_million_usd"] = out["deaths"] / ((out["aid_usd"] + eps) / 1_000_000)
    out["log_gap"] = np.log(out["deaths"]) - np.log(out["aid_usd"] + eps)
    out["rank_log_gap"] = out["log_gap"].rank(ascending=False, method="min").astype(int)
    out["rank_deaths_per_usd"] = (
        out["deaths_per_million_usd"].rank(ascending=False, method="min").astype(int)
    )
    return out.sort_values("log_gap", ascending=False).reset_index(drop=True)


def save_figures(df: pd.DataFrame) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    top = df.head(12).iloc[::-1]
    labels = top["country"].replace({"Congo, Democratic Republic of the": "DRC"})
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.barh(labels, top["deaths_per_million_usd"], color="#3b6d9a")
    ax.set_xscale("log")
    ax.set_xlabel("Deaths per $1 million of malaria aid ($0 scored as $100k)")
    ax.set_title("Where malaria aid is thin relative to deaths")
    fig.tight_layout()
    fig.savefig(FIG / "gap_top12.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    x = np.log10(df["aid_usd"] + 1e5)
    y = np.log10(df["deaths"])
    ax.scatter(x, y, s=28, color="#3b6d9a", alpha=0.85)
    for _, row in df.nlargest(6, "log_gap").iterrows():
        ax.annotate(row["country"], (np.log10(row["aid_usd"] + 1e5), np.log10(row["deaths"])), fontsize=8)
    ax.set_xlabel("log10(annual malaria aid, OECD + Global Fund, USD + $100k)")
    ax.set_ylabel("log10(WHO malaria deaths, 2021)")
    ax.set_title("High deaths and low malaria aid sit top-left")
    fig.tight_layout()
    fig.savefig(FIG / "gap_scatter.png", dpi=160)
    plt.close(fig)

    try:
        import geopandas as gpd

        geo_path = RAW / "countries.geojson"
        if not geo_path.exists():
            r = requests.get(GEO_URL, headers=HEADERS, timeout=120)
            r.raise_for_status()
            geo_path.write_bytes(r.content)
        world = gpd.read_file(geo_path)
        iso_col = "ISO3166-1-Alpha-3" if "ISO3166-1-Alpha-3" in world.columns else "ISO_A3"
        merged = world.merge(df[["iso3", "log_gap"]], left_on=iso_col, right_on="iso3", how="left")
        fig, ax = plt.subplots(figsize=(10, 5.2))
        merged.plot(ax=ax, color="#e6e6e6", linewidth=0.2, edgecolor="white")
        merged.dropna(subset=["log_gap"]).plot(
            ax=ax, column="log_gap", cmap="YlOrRd", linewidth=0.2, edgecolor="white", legend=True,
            legend_kwds={"label": "log(deaths) − log(OECD + Global Fund + $100k)", "shrink": 0.6},
        )
        ax.set_axis_off()
        ax.set_title("Malaria funding–burden gap, with Global Fund included")
        fig.tight_layout()
        fig.savefig(FIG / "gap_map.png", dpi=160)
        plt.close(fig)
    except Exception as exc:  # map is a deliverable; surface the failure in the summary
        (FIG / "map_error.txt").write_text(str(exc))


def save_daly_figures(df: pd.DataFrame) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    top = df.sort_values("daly_log_gap", ascending=False).head(12).iloc[::-1]
    labels = top["country"].replace({"Congo, Democratic Republic of the": "DRC"})
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.barh(labels, top["dalys_per_million_usd"], color="#8c4a3a")
    ax.set_xscale("log")
    ax.set_xlabel("DALYs per $1 million of malaria aid ($0 scored as $100k)")
    ax.set_title("Same aid total, burden measured in DALYs")
    fig.tight_layout()
    fig.savefig(FIG / "gap_top12_dalys.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    x = np.log10(df["aid_usd"] + 1e5)
    y = np.log10(df["dalys"])
    ax.scatter(x, y, s=28, color="#8c4a3a", alpha=0.85)
    for _, row in df.nlargest(6, "daly_log_gap").iterrows():
        ax.annotate(
            row["country"],
            (np.log10(row["aid_usd"] + 1e5), np.log10(row["dalys"])),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=8,
        )
    ax.set_xlabel("log10(annual malaria aid, OECD + Global Fund, USD + $100k)")
    ax.set_ylabel("log10(GBD malaria DALYs, 2021)")
    ax.set_title("High DALYs and low malaria aid sit top-left")
    fig.tight_layout()
    fig.savefig(FIG / "gap_scatter_dalys.png", dpi=160)
    plt.close(fig)

    try:
        import geopandas as gpd

        geo_path = RAW / "countries.geojson"
        if not geo_path.exists():
            r = requests.get(GEO_URL, headers=HEADERS, timeout=120)
            r.raise_for_status()
            geo_path.write_bytes(r.content)
        world = gpd.read_file(geo_path)
        iso_col = "ISO3166-1-Alpha-3" if "ISO3166-1-Alpha-3" in world.columns else "ISO_A3"
        merged = world.merge(df[["iso3", "daly_log_gap"]], left_on=iso_col, right_on="iso3", how="left")
        fig, ax = plt.subplots(figsize=(10, 5.2))
        merged.plot(ax=ax, color="#e6e6e6", linewidth=0.2, edgecolor="white")
        merged.dropna(subset=["daly_log_gap"]).plot(
            ax=ax,
            column="daly_log_gap",
            cmap="YlOrRd",
            linewidth=0.2,
            edgecolor="white",
            legend=True,
            legend_kwds={"label": "log(DALYs) − log(OECD + Global Fund + $100k)", "shrink": 0.6},
        )
        ax.set_axis_off()
        ax.set_title("Malaria DALY gap, with Global Fund included")
        fig.tight_layout()
        fig.savefig(FIG / "gap_map_dalys.png", dpi=160)
        plt.close(fig)
    except Exception as exc:
        (FIG / "daly_map_error.txt").write_text(str(exc))


def main() -> None:
    rules = load_rules()
    eps = float(rules["ranking"]["epsilon_usd"])
    aid = fetch_crs()
    deaths = fetch_deaths(2021)
    # First pass uses CRS purpose 12262 only, so those ranks can be kept.
    crs_ranked = add_daly_ranks(score(deaths, aid, rules), fetch_dalys(), rules)
    crs_ranked = crs_ranked.rename(
        columns={
            "daly_log_gap": "daly_log_gap_crs",
            "rank_daly_log_gap": "rank_daly_log_gap_crs",
            "dalys_per_million_usd": "dalys_per_million_usd_crs",
        }
    )
    ranked = add_channels(crs_ranked, rules)
    ranked["dalys_per_million_usd"] = ranked["dalys"] / ((ranked["aid_usd"] + eps) / 1_000_000)
    ranked["daly_log_gap"] = np.log(ranked["dalys"]) - np.log(ranked["aid_usd"] + eps)
    ranked["rank_daly_log_gap"] = (
        ranked["daly_log_gap"].rank(ascending=False, method="min").astype(int)
    )
    ranked = aid_recommendations(ranked, rules)
    cols = [
        "rank_log_gap",
        "rank_daly_log_gap",
        "rank_log_gap_crs",
        "rank_daly_log_gap_crs",
        "iso3",
        "country",
        "deaths",
        "dalys",
        "crs_aid_usd",
        "gf_allocation_2020_2022_usd",
        "gf_allocation_2023_2025_usd",
        "gf_annual_usd",
        "gf_amount_source",
        "gf_timing",
        "who_gf_country_reported_usd",
        "who_gf_country_years",
        "who_gf_donor_reported_usd",
        "gov_nmp_usd",
        "gov_nmp_years",
        "aid_usd",
        "deaths_per_million_usd",
        "dalys_per_million_usd",
        "log_gap",
        "daly_log_gap",
        "log_gap_crs",
        "rank_deaths_per_usd",
        "peer_usd_per_death",
        "peer_usd_per_daly",
        "addl_aid_from_deaths_usd",
        "addl_aid_from_dalys_usd",
    ]
    ranked[cols].to_csv(PROJ / "funding_burden_ranked.csv", index=False)
    save_figures(ranked)
    save_daly_figures(ranked)
    rho = ranked["rank_log_gap"].corr(ranked["rank_deaths_per_usd"], method="spearman")
    rho_daly = ranked["rank_log_gap"].corr(ranked["rank_daly_log_gap"], method="spearman")
    rho_crs = ranked["rank_log_gap"].corr(ranked["rank_log_gap_crs"], method="spearman")
    death_top = set(ranked.nsmallest(10, "rank_log_gap")["iso3"])
    daly_top = set(ranked.nsmallest(10, "rank_daly_log_gap")["iso3"])
    crs_top = set(ranked.nsmallest(10, "rank_log_gap_crs")["iso3"])
    daly_order = ranked.sort_values("rank_daly_log_gap")
    focus = ["TCD", "TGO", "YEM", "COG", "CAF", "SOM", "IND", "PAK", "SDN", "NGA", "COD", "NER"]
    focus_rows = ranked[ranked["iso3"].isin(focus)].sort_values("rank_log_gap")
    summary = {
        "n_countries": int(len(ranked)),
        "min_deaths": rules["ranking"]["min_deaths"],
        "epsilon_usd": rules["ranking"]["epsilon_usd"],
        "zero_crs_countries": int((ranked["crs_aid_usd"] == 0).sum()),
        "zero_combined_aid_countries": int((ranked["aid_usd"] == 0).sum()),
        "gf_imputed_countries": ranked.loc[
            ranked["gf_amount_source"].eq("imputed_who_annex_4c_country_reported_global_fund"),
            "country",
        ].tolist(),
        "peer_usd_per_death": float(ranked["peer_usd_per_death"].iloc[0]),
        "peer_usd_per_daly": float(ranked["peer_usd_per_daly"].iloc[0]),
        "spearman_log_gap_vs_deaths_per_usd": float(rho),
        "spearman_death_rank_vs_daly_rank": float(rho_daly),
        "spearman_combined_rank_vs_crs_only_rank": float(rho_crs),
        "top10_overlap_deaths_vs_dalys": int(len(death_top & daly_top)),
        "top10_overlap_combined_vs_crs_only": int(len(death_top & crs_top)),
        "top5": ranked.head(5)[
            ["country", "deaths", "crs_aid_usd", "gf_annual_usd", "aid_usd", "gf_amount_source", "rank_log_gap_crs"]
        ].to_dict(orient="records"),
        "daly_top5": daly_order.head(5)[
            ["country", "rank_log_gap", "rank_daly_log_gap", "rank_daly_log_gap_crs", "dalys", "aid_usd"]
        ].to_dict(orient="records"),
        "focus": focus_rows[
            [
                "country",
                "rank_log_gap",
                "rank_daly_log_gap",
                "rank_log_gap_crs",
                "crs_aid_usd",
                "gf_annual_usd",
                "gf_amount_source",
                "gov_nmp_usd",
                "gov_nmp_years",
                "addl_aid_from_deaths_usd",
                "addl_aid_from_dalys_usd",
            ]
        ].to_dict(orient="records"),
    }
    (FIG / "gap_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
