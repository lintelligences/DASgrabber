# Public DAS Datasets Reference Guide (US West Coast & Major Archives)

This document catalogs the URL structures, directory layouts, file formats, and companion reader repositories for publicly downloadable **Distributed Acoustic Sensing (DAS)** datasets.

---

## 1. University of Washington (UW FiberLab / OOI Regional Cabled Array)

The **Ocean Observatories Initiative (OOI) Regional Cabled Array (RCA)** submarine telecommunication cables offshore **Pacific City, Oregon** (North Cable ~65 km, South Cable ~95 km) host several open-access community DAS experiments managed by the University of Washington Department of Earth and Space Sciences (**UW FiberLab**).

Unlike cloud object stores that require API keys, the primary UW OOI RCA holdings are served directly via **open Apache HTML directory indexes** on `http://piweb.ooirsn.uw.edu/`.

### 1.1 OOI RCA 2021 RAPID Community Experiment (`uw-ooi-rca-2021`)
* **Dates:** November 1–5, 2021 (PI: Dr. William Wilcock, DOI: `10.58046/5J60-FJ89`)
* **Root HTML Index:** `http://piweb.ooirsn.uw.edu/das/`
* **Directory Tree:**
  * `http://piweb.ooirsn.uw.edu/das/data/Optasense/NorthCable/` — Raw/unprocessed HDF5 (`.h5`) files for the northern cable.
  * `http://piweb.ooirsn.uw.edu/das/data/Optasense/SouthCable/` — Divided into `TransmitFiber/` and `ReceiveFiber/` subdirectories.
  * `http://piweb.ooirsn.uw.edu/das/processed/` — Downsampled/processed products.
  * `http://piweb.ooirsn.uw.edu/das/processed/metadata/` — Essential documentation (`readme.pdf`, `changes.pdf`), system configuration (`Optasense/`, `Silixa/`), and 3D cable coordinates/bathymetric depth (`OOI_RCA_DAS_channel_location/`).

### 1.2 OOI RCA May 2024 Multiplexed DAS Experiment (`uw-ooi-rca-2024`)
* **Dates:** May 6–10, 2024
* **Experiment Summary:** 4-day continuous recording demonstrating optical multiplexing (simultaneous L-band DAS and live telecommunications traffic on the same active OOI fiber).
* **Root HTML Index:** `http://piweb.ooirsn.uw.edu/das24/`
* **Directory Tree:**
  * `http://piweb.ooirsn.uw.edu/das24/data/20240506/`
  * `http://piweb.ooirsn.uw.edu/das24/data/20240507/`
  * `http://piweb.ooirsn.uw.edu/das24/data/20240508/`
  * `http://piweb.ooirsn.uw.edu/das24/data/20240509/`
  * `http://piweb.ooirsn.uw.edu/das24/data/20240510/`
* **Companion Code & Geometry Repo:** `https://github.com/uwfiberlab/OOI_DAS_2024`

### 1.3 OOI RCA 2025–2026 Multi-Span & OptoDAS Campaign (`uw-ooi-rca-2025-*`)
* **Dates:** November 2025 – January 2026
* **Root HTML Index:** `http://piweb.ooirsn.uw.edu/das25/`
* **Directory Tree:**
  * **Alcatel OptoDAS (`uw-ooi-rca-2025-optodas`, ~1.2 TB):**
    * `http://piweb.ooirsn.uw.edu/das25/data/OptoDAS/` — HDF5 (`.h5`) files recorded on the OOI southern submarine cable.
  * **Nokia Bell Labs Multi-Span DAS (`uw-ooi-rca-2025-multidas`, ~3.9 TB):**
    * `http://piweb.ooirsn.uw.edu/das25/data/MultiDAS/` — Binary data arrays + metadata testing multi-span DAS across optical repeaters on the North and South cables.
* **Companion Code & Readers Repo:** `https://github.com/uwfiberlab/OOI_DAS_2025`

### 1.4 UW Photonic Sensing Facility (PSF) Regional West Coast Deployments
* **Portal:** `https://pita.ess.washington.edu/psf/projects-and-data/`
* **GitHub Organization:** `https://github.com/uwfiberlab`
* **Notable Regional Campaigns:**
  * **SeaDAS:** Urban dark-fiber array in Seattle, Washington.
  * **WhidbeyDAS:** Terrestrial/island dark-fiber deployment on Whidbey Island, Washington.
  * **Cook Inlet DAS:** Subsea/coastal deployment in Cook Inlet, Alaska.

---

## 2. Monterey Bay (MBARI MARS Cable) via NCEDC (`ncedc-mbari-mars`)

* **Location:** Moss Landing / Monterey Bay, California (52-km subsea Monterey Accelerated Research System [MARS] science cable).
* **Temporal Span:** Continuous 1-year archive from October 27, 2023 to October 31, 2024 (including the SeaFOAM campaign).
* **Format:** HDF5 (`.h5`) with embedded metadata, organized both by `year/day-of-year` and by continuous acquisition windows.
* **Programmatic Access (Anonymous AWS S3):**
  ```bash
  aws s3 ls --no-sign-request s3://ncedc-pds/
  ```
* **Documentation:** `https://ncedc.org/db/cloud.html`

---

## 3. Western US Geothermal & Terrestrial Arrays

### 3.1 PoroTomo at Brady Hot Springs, Nevada (`oedi-porotomo-brady`)
* **Array Geometry:** 8.7 km horizontal surface-trench fiber (`DASH`) and 0.4 km vertical borehole fiber (`DASV`) interrogated with a Silixa iDAS unit (March 2016).
* **Formats:** SEG-Y (`.sgy`), HDF5 (`.h5`), MATLAB (`.mat`).
* **Programmatic Access (Anonymous AWS S3):**
  ```bash
  aws s3 ls --no-sign-request s3://nrel-pds-porotomo/DAS/
  ```
* **HTTPS Browser Viewer:** `https://data.openei.org/s3_viewer?bucket=nrel-pds-porotomo`

### 3.2 DOE Geothermal Data Repository (GDR) — Utah FORGE & Dark Fiber
* **Portal:** `https://gdr.openei.org/`
* **Holdings:** Direct HTTP downloads of SEG-Y and HDF5 DAS packages from Utah FORGE borehole stimulation stages, Garner Valley, and Imperial Valley dark-fiber campaigns.

---

## 4. PubDAS Global & Multi-Institutional Catalog (`pubdas-globus-catalog`)

* **Reference:** Spica et al. (2023), *"PubDAS: A PUBlic Distributed Acoustic Sensing Datasets Repository for Geosciences"*, *Seismological Research Letters*, `10.1785/0220220279`.
* **Scale:** ~90+ TB across urban, marine, volcanic, and fault-zone fiber deployments (including the February 2023 Global DAS Month campaign).
* **Access Mechanism:** Coordinated via **Globus** endpoints (`https://www.globus.org/`).
