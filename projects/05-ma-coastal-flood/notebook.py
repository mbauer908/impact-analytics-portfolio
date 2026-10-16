import marimo

__generated_with = "0.9.0"

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # MA coastal flood exposure

        Day 10 ingest (clip first, then overlay):

        1. Download NOAA SLR inundation for the chosen scenario → `data/raw/slr/`.
        2. Download MassGIS parcels for **one town**; refuse statewide files on a laptop.
        3. Join SVI at block group.
        4. `overlay` / `sjoin` inundation ∩ parcels; tabulate by SVI quartile.

        CRS: work in a Massachusetts meter projection (e.g. EPSG:26986) for areas.
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()
