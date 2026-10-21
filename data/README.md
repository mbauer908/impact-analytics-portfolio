# Data

The inputs for the finished analyses are in git so a clone can rerun them. Future large downloads (rasters, parcel files, full API dumps) still belong in `raw/` and stay ignored until a project needs them committed. Derived tables go in `processed/`. Small hand-built fixtures live in `fixtures/`.

Document every source in the project README that uses it: URL, retrieval date, and any terms of use. The publishers keep their own terms. These copies are here so the scripts run.

## Source map

| Project | Primary sources |
|---|---|
| GiveWell CEA | Workbooks in `data/raw/givewell/`: AMF, HKI, Malaria Consortium, New Incentives, and the moral-weights tool. Public GiveWell spreadsheets. |
| Funding vs burden | Files in `data/raw/funding/`: OECD CRS purpose 12262 (2019–2022), WHO malaria deaths, ISO names, country boundaries, Global Fund allocation tables for 2020–2022 and 2023–2025, WHO World malaria report 2024 Annex 4C, and the IHME malaria DALY extract. |
| Meta-analysis | [3ie Development Evidence Portal](https://developmentevidence.3ieimpact.org/) |
| DALY vs WELLBY | GiveWell moral weights / CEA; [Happier Lives Institute](https://www.happierlivesinstitute.org/) WELLBY work |
| MA coastal flood | NOAA SLR, MassGIS parcels, CDC/ATSDR SVI or MA EJ screening |
| EV deserts | [NREL AFDC](https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/), Census ACS |
