import marimo

__generated_with = "0.9.0"

app = marimo.App(width="medium")


@app.cell
def _():
    import os

    import marimo as mo
    from dotenv import load_dotenv

    load_dotenv()
    key_ok = bool(os.getenv("NREL_API_KEY"))
    mo.md(
        f"""
        # EV charging deserts

        1. Copy `.env.example` → `.env` and add an NREL AFDC key
           (present: **{key_ok}**).
        2. Pull public ELEC stations for MA; keep L2 and DC Fast.
        3. Tract centroids / polygons from TIGER + ACS income and population.
        4. Buffer 1 km in a projected CRS; compute plugs per 10k people.
        5. Flag low-access ∩ low-income tracts.

        Fallback if the API is annoying: AFDC station CSV download.
        """
    )
    return key_ok, load_dotenv, mo, os


if __name__ == "__main__":
    app.run()
