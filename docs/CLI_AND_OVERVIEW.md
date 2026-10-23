# Global Public DAS Datasets Catalog & CLI Reference

A lightweight, git-safe repository for indexing, monitoring, and selectively downloading **validated global public Distributed Acoustic Sensing (DAS)** datasets across submarine cables, urban dark fiber, geothermal boreholes, volcanoes, subduction zones, and alpine/polar glaciers.

---

## Core Repository Rules

1. **Zero Waveform Data in Git:** Raw or processed DAS waveform files (`.h5`, `.hdf5`, `.tdms`, `.sgy`, `.segy`, `.mseed`, `.bin`, `.mat`, `.zarr`, `.zip`) **must never be committed to this repository**. All data extensions and download directories (`downloads/`, `data/`, `raw/`, `cache/`) are blocked by [`.gitignore`](file:///Users/lisa/PROJECTS/DAS/.gitignore) and enforced by [`scripts/download_dataset.py`](file:///Users/lisa/PROJECTS/DAS/scripts/download_dataset.py).
2. **100% Validated Downloads Only:** Every dataset listed in [`catalog/datasets.json`](file:///Users/lisa/PROJECTS/DAS/catalog/datasets.json) has been locally indexed into `manifests/<dataset_id>.json` and verified via [`scripts/validate_downloads.py`](file:///Users/lisa/PROJECTS/DAS/scripts/validate_downloads.py) (confirming unauthenticated HTTP `200`/`206` streaming and valid HDF5/MAT/ZIP/PDF/CSV file headers).

---

## CLI Workflow

```bash
# 1. List all validated datasets
python3 scripts/das_catalog.py list

# 2. Re-run local end-to-end download validation across all 12 datasets
python3 scripts/validate_downloads.py

# 3. Crawl/refresh a dataset's manifest without downloading data
python3 scripts/crawl_http_index.py --dataset uw-ooi-rca-2025-optodas

# 4. Preview (--dry-run) and selectively download matched files
python3 scripts/download_dataset.py --manifest manifests/uw-ooi-rca-2024.json --match "1557.*\\.hdf5$"
python3 scripts/download_dataset.py --manifest manifests/uw-ooi-rca-2024.json --match "1557.*\\.hdf5$" --limit 2 --execute
```
