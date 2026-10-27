# DAS Dataset Download Manager

Start the local download manager and live job monitor UI (writes only to git-ignored `downloads/`):

```bash
python3 scripts/server.py --port 8765
# Open http://127.0.0.1:8765
```

> CLI documentation & dataset notes: [`docs/CLI_AND_OVERVIEW.md`](docs/CLI_AND_OVERVIEW.md) · [`docs/WEST_COAST_AND_PUBLIC_DAS.md`](docs/WEST_COAST_AND_PUBLIC_DAS.md)

---

### Download Jobs (Static Snapshot)

<table>
  <thead>
    <tr>
      <th align="left">Job</th>
      <th align="left">Dataset</th>
      <th align="left">Current File</th>
      <th align="left">Files</th>
      <th align="left">Progress</th>
      <th align="left">Downloaded</th>
      <th align="left">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="7"><em>Idle — run <code>python3 scripts/server.py --port 8765</code> locally to start and monitor active transfers.</em></td>
    </tr>
  </tbody>
</table>

### Validated Global Datasets (20/20 Passed)

<table>
  <thead>
    <tr>
      <th align="left">Dataset ID</th>
      <th align="left">Place / Region</th>
      <th align="left">Protocol</th>
      <th align="left">Est. Size</th>
      <th align="right">Manifest Files</th>
      <th align="left">Validation</th>
      <th align="left">Links</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>uw-ooi-rca-2021</code></td>
      <td>Northeast Pacific — Offshore Pacific City, Oregon, USA</td>
      <td><code>http_directory</code></td>
      <td>Multi-TB (308+ HDF5 files in OptaSense North &amp; South ReceiveFiber)</td>
      <td align="right">5433</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="http://piweb.ooirsn.uw.edu/das/data/">Endpoint</a> · <a href="manifests/uw-ooi-rca-2021.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>uw-ooi-rca-2024</code></td>
      <td>Northeast Pacific — Offshore Central Oregon, USA</td>
      <td><code>http_directory</code></td>
      <td>Multi-TB</td>
      <td align="right">2787</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="http://piweb.ooirsn.uw.edu/das24/data/">Endpoint</a> · <a href="manifests/uw-ooi-rca-2024.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>uw-ooi-rca-2025-optodas</code></td>
      <td>Northeast Pacific — Offshore Oregon, USA (OOI Southern Cable)</td>
      <td><code>http_directory</code></td>
      <td>1.2 TB</td>
      <td align="right">570</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="http://piweb.ooirsn.uw.edu/das25/data/OptoDAS/">Endpoint</a> · <a href="manifests/uw-ooi-rca-2025-optodas.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>uw-ooi-rca-2025-multidas</code></td>
      <td>Northeast Pacific — Offshore Oregon, USA (OOI North &amp; South Cables)</td>
      <td><code>http_directory</code></td>
      <td>3.9 TB</td>
      <td align="right">480</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="http://piweb.ooirsn.uw.edu/das25/data/MultiDAS/">Endpoint</a> · <a href="manifests/uw-ooi-rca-2025-multidas.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-oregon-tsunami-infragravity</code></td>
      <td>Northeast Pacific — Offshore Oregon, USA (Submarine Telecom Cable)</td>
      <td><code>zenodo_api</code></td>
      <td>5.94 GB (72 hourly .h5 waveform files)</td>
      <td align="right">76</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="https://zenodo.org/api/records/10463888">Endpoint</a> · <a href="manifests/zenodo-oregon-tsunami-infragravity.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-monterey-mars-geosense</code></td>
      <td>Northeast Pacific — Monterey Canyon, Offshore California, USA</td>
      <td><code>zenodo_api</code></td>
      <td>10.95 GB</td>
      <td align="right">12</td>
      <td><code>PASS (MiniSEED Waveform)</code></td>
      <td><a href="https://zenodo.org/api/records/18673947">Endpoint</a> · <a href="manifests/zenodo-monterey-mars-geosense.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-muroto-japan</code></td>
      <td>Northwest Pacific — Offshore Cape Muroto, Shikoku, Japan (Nankai Trough)</td>
      <td><code>zenodo_api</code></td>
      <td>2.72 GB</td>
      <td align="right">5</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/7935235">Endpoint</a> · <a href="manifests/zenodo-muroto-japan.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-muroto-noto-earthquake</code></td>
      <td>Northwest Pacific — Offshore Cape Muroto, Nankai Trough, Southwest Japan</td>
      <td><code>zenodo_api</code></td>
      <td>37.1 GB (17 hourly ZIP archives of AP Sensing .hdf5 files)</td>
      <td align="right">19</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/16907853">Endpoint</a> · <a href="manifests/zenodo-muroto-noto-earthquake.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-svalbard-whale</code></td>
      <td>Arctic Ocean / North Atlantic — Isfjorden, Svalbard, Norway</td>
      <td><code>zenodo_api</code></td>
      <td>25.2 GB (8 multi-GB raw .mat files)</td>
      <td align="right">11</td>
      <td><code>PASS (MATLAB v5 MAT-file)</code></td>
      <td><a href="https://zenodo.org/api/records/5823343">Endpoint</a> · <a href="manifests/zenodo-svalbard-whale.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-trondheim-submarine-ships</code></td>
      <td>Norwegian Sea / North Atlantic — Trondheimsfjord, Norway</td>
      <td><code>zenodo_api</code></td>
      <td>60.6 GB</td>
      <td align="right">1</td>
      <td><code>PASS (7-Zip Archive (7z\xbc\xaf))</code></td>
      <td><a href="https://zenodo.org/api/records/18851481">Endpoint</a> · <a href="manifests/zenodo-trondheim-submarine-ships.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-marlinks-north-sea</code></td>
      <td>North Sea — Offshore Belgium / Southern North Sea</td>
      <td><code>zenodo_api</code></td>
      <td>13.46 GB (direct single .h5 waveform matrix)</td>
      <td align="right">5</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="https://zenodo.org/api/records/15611778">Endpoint</a> · <a href="manifests/zenodo-marlinks-north-sea.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-abyss-offshore-optodas</code></td>
      <td>Southeast Pacific — Offshore Central Chile (CCN.N Submarine Cable)</td>
      <td><code>zenodo_api</code></td>
      <td>45.5 GB (10 ZIP bundles containing 7,200 native OptoDAS .hdf5 files)</td>
      <td align="right">10</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/17143738">Endpoint</a> · <a href="manifests/zenodo-abyss-offshore-optodas.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-emso-catania-mediterranean</code></td>
      <td>Mediterranean Sea — Western Ionian Sea, Offshore Catania, Sicily, Italy</td>
      <td><code>zenodo_api</code></td>
      <td>1.65 GB</td>
      <td align="right">10</td>
      <td><code>PASS (NumPy Array (\x93NUMPY))</code></td>
      <td><a href="https://zenodo.org/api/records/17571118">Endpoint</a> · <a href="manifests/zenodo-emso-catania-mediterranean.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-sicily-microseisms-das</code></td>
      <td>Mediterranean Sea — Offshore Catania, Sicily, Italy</td>
      <td><code>zenodo_api</code></td>
      <td>19.5 GB (8.2 GB observed `DAS_data.hdf5` in `DAS_data.zip` + 11.3 GB simulations)</td>
      <td align="right">3</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/20668434">Endpoint</a> · <a href="manifests/zenodo-sicily-microseisms-das.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-santorini-kolumbo-submarine</code></td>
      <td>Mediterranean / Aegean Sea — Offshore Santorini &amp; Kolumbo Volcano, Greece</td>
      <td><code>zenodo_api</code></td>
      <td>1.55 GB (3 ZIP archives of Silixa .h5 submarine DAS files)</td>
      <td align="right">3</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/11241132">Endpoint</a> · <a href="manifests/zenodo-santorini-kolumbo-submarine.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-multisite-finwhale-das</code></td>
      <td>Global Multi-Basin — North Pacific (OOI), Arctic (Svalbard), Mediterranean (MEUST Toulon)</td>
      <td><code>zenodo_api</code></td>
      <td>1.81 GB</td>
      <td align="right">1</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/15008561">Endpoint</a> · <a href="manifests/zenodo-multisite-finwhale-das.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-utqiagvik-arctic-seaice</code></td>
      <td>Arctic Ocean — Offshore Utqiagvik (Barrow), Alaska, USA</td>
      <td><code>zenodo_api</code></td>
      <td>2.88 GB</td>
      <td align="right">6</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/23221461">Endpoint</a> · <a href="manifests/zenodo-utqiagvik-arctic-seaice.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>oedi-porotomo-brady</code></td>
      <td>North America — Brady Hot Springs, Nevada, USA</td>
      <td><code>aws_s3_anonymous</code></td>
      <td>25+ TB</td>
      <td align="right">100</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="https://nrel-pds-porotomo.s3.amazonaws.com/">Endpoint</a> · <a href="manifests/oedi-porotomo-brady.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-tangshan-china</code></td>
      <td>Asia — Tangshan, Hebei Province, China</td>
      <td><code>zenodo_api</code></td>
      <td>45 MB</td>
      <td align="right">5</td>
      <td><code>PASS (MATLAB v5 MAT-file)</code></td>
      <td><a href="https://zenodo.org/api/records/4554758">Endpoint</a> · <a href="manifests/zenodo-tangshan-china.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-rhonegletscher-alps</code></td>
      <td>Europe — Rhonegletscher, Valais, Swiss Alps, Switzerland</td>
      <td><code>zenodo_api</code></td>
      <td>13.5 GB</td>
      <td align="right">2</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/13890738">Endpoint</a> · <a href="manifests/zenodo-rhonegletscher-alps.json">Manifest</a></td>
    </tr>
  </tbody>
</table>

### Manifest File Inspector (Static Preview)

<details>
  <summary><strong><code>uw-ooi-rca-2021</code></strong> — OOI Regional Cabled Array (RCA) RAPID Community Submarine DAS Experiment (2021) (5433 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 5433)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/data/Optasense/NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143211Z.h5"><code>NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143211Z.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/data/Optasense/NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143311Z.h5"><code>NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143311Z.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/data/Optasense/NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143411Z.h5"><code>NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143411Z.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/data/Optasense/NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143511Z.h5"><code>NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143511Z.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/data/Optasense/NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143611Z.h5"><code>NorthCable/ReceiveFiber/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T07_31_00-0700/North-C1-LR-P1kHz-GL50m-Sp2m-FS200Hz-ReceiveFiber_2021-11-05T143611Z.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>uw-ooi-rca-2024</code></strong> — OOI Regional Cabled Array Multiplexed Submarine DAS Experiment (May 2024) (2787 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 2787)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das24/data/20240506/dphi/155734.hdf5"><code>dphi/155734.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das24/data/20240506/dphi/155744.hdf5"><code>dphi/155744.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das24/data/20240506/dphi/155754.hdf5"><code>dphi/155754.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das24/data/20240506/dphi/155804.hdf5"><code>dphi/155804.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das24/data/20240506/dphi/155814.hdf5"><code>dphi/155814.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>uw-ooi-rca-2025-optodas</code></strong> — OOI Regional Cabled Array Alcatel OptoDAS Submarine Experiment (Nov 2025 – Jan 2026) (570 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 570)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/OptoDAS/2025/11/13/south/8Hz/UW_DAS_south_8Hz_20251113_222344.hdf5"><code>south/8Hz/UW_DAS_south_8Hz_20251113_222344.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/OptoDAS/2025/11/13/south/8Hz/UW_DAS_south_8Hz_20251113_222518.hdf5"><code>south/8Hz/UW_DAS_south_8Hz_20251113_222518.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/OptoDAS/2025/11/13/south/8Hz/UW_DAS_south_8Hz_20251113_222528.hdf5"><code>south/8Hz/UW_DAS_south_8Hz_20251113_222528.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/OptoDAS/2025/11/13/south/8Hz/UW_DAS_south_8Hz_20251113_222538.hdf5"><code>south/8Hz/UW_DAS_south_8Hz_20251113_222538.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/OptoDAS/2025/11/13/south/8Hz/UW_DAS_south_8Hz_20251113_222548.hdf5"><code>south/8Hz/UW_DAS_south_8Hz_20251113_222548.hdf5</code></a></td>
        <td><code>.hdf5</code></td>
        <td align="right">-</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>uw-ooi-rca-2025-multidas</code></strong> — OOI Regional Cabled Array Nokia Multi-Span Submarine DAS Experiment (Nov 2025 – Jan 2026) (480 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 480)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/MultiDAS/2025/11/05/north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_021204_00000000000000000000.h5"><code>north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_021204_00000000000000000000.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/MultiDAS/2025/11/05/north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_021204_00000000000000000001.h5"><code>north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_021204_00000000000000000001.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/MultiDAS/2025/11/05/north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_021636_00000000000000000002.h5"><code>north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_021636_00000000000000000002.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/MultiDAS/2025/11/05/north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_022107_00000000000000000003.h5"><code>north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_022107_00000000000000000003.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das25/data/MultiDAS/2025/11/05/north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_022538_00000000000000000004.h5"><code>north/8Hz/downsampled_nokia_DAS_north_8Hz_20251105_022538_00000000000000000004.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">-</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-oregon-tsunami-infragravity</code></strong> — Offshore Oregon Underwater DAS Earthquake Infragravity &amp; Tsunami Wave Dataset (76 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 76)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/10463888/files/2021-08-10T10.02.39.08_60_min.h5/content"><code>2021-08-10T10.02.39.08_60_min.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">82.42M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/10463888/files/2021-08-10T11.02.40.08_60_min.h5/content"><code>2021-08-10T11.02.40.08_60_min.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">82.42M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/10463888/files/2021-08-11T00.02.53.08_60_min.h5/content"><code>2021-08-11T00.02.53.08_60_min.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">82.42M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/10463888/files/2021-08-11T01.02.54.08_60_min.h5/content"><code>2021-08-11T01.02.54.08_60_min.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">82.42M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/10463888/files/2021-08-11T02.02.55.08_60_min.h5/content"><code>2021-08-11T02.02.55.08_60_min.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">82.42M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-monterey-mars-geosense</code></strong> — Monterey Canyon &amp; MARS Cabled Observatory Seafloor DAS Dataset (Geo-Sense) (12 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 12)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/18673947/files/1004.2007.57162.028.202.mseed/content"><code>1004.2007.57162.028.202.mseed</code></a></td>
        <td><code>.mseed</code></td>
        <td align="right">360.00M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/18673947/files/1004.2007.57162.029.203.mseed/content"><code>1004.2007.57162.029.203.mseed</code></a></td>
        <td><code>.mseed</code></td>
        <td align="right">360.00M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/18673947/files/1004.2007.57162.030.204.mseed/content"><code>1004.2007.57162.030.204.mseed</code></a></td>
        <td><code>.mseed</code></td>
        <td align="right">360.00M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/18673947/files/1004.2007.57162.031.205.mseed/content"><code>1004.2007.57162.031.205.mseed</code></a></td>
        <td><code>.mseed</code></td>
        <td align="right">360.00M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/18673947/files/1004.2007.57162.032.206.mseed/content"><code>1004.2007.57162.032.206.mseed</code></a></td>
        <td><code>.mseed</code></td>
        <td align="right">360.00M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-muroto-japan</code></strong> — Cape Muroto Subsea Cable Shallow Tremor &amp; Slow Slip DAS Dataset (Japan) (5 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 5)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/7935235/files/tremor_hdf5.zip/content"><code>tremor_hdf5.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">2598.72M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/7935235/files/DataSetS1.txt/content"><code>DataSetS1.txt</code></a></td>
        <td><code>.txt</code></td>
        <td align="right">2114B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/7935235/files/channelinfo.txt/content"><code>channelinfo.txt</code></a></td>
        <td><code>.txt</code></td>
        <td align="right">1527B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/7935235/files/DataSetS3.txt/content"><code>DataSetS3.txt</code></a></td>
        <td><code>.txt</code></td>
        <td align="right">1361B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/7935235/files/DataSetS2.txt/content"><code>DataSetS2.txt</code></a></td>
        <td><code>.txt</code></td>
        <td align="right">2114B</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-muroto-noto-earthquake</code></strong> — Cape Muroto 120 km Subsea Cable Continuous DAS Dataset (2024 M7.6 Noto Earthquake, Japan) (19 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 19)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/16907853/files/20240101_07.zip/content"><code>20240101_07.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">2369.81M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/16907853/files/20240101_09.zip/content"><code>20240101_09.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">2230.68M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/16907853/files/20240101_08.zip/content"><code>20240101_08.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">2220.81M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/16907853/files/20240101_11.zip/content"><code>20240101_11.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">2189.22M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/16907853/files/20240101_10.zip/content"><code>20240101_10.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">2182.76M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-svalbard-whale</code></strong> — DAS4Whale: Svalbard Arctic Subsea Cable DAS Dataset (Norway) (11 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 11)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/5823343/files/20200627_192255_ch07001_to_ch08500_whale_raw_L310s.mat/content"><code>20200627_192255_ch07001_to_ch08500_whale_raw_L310s.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">2290.43M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/5823343/files/20200716_154302_ch21001_to_ch22000_whale_raw_L720s.mat/content"><code>20200716_154302_ch21001_to_ch22000_whale_raw_L720s.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">3547.48M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/5823343/files/20200716_154302_ch20001_to_ch21000_whale_raw_L720s.mat/content"><code>20200716_154302_ch20001_to_ch21000_whale_raw_L720s.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">3547.48M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/5823343/files/20200627_052441_ch08751_to_ch10000_whale_raw_L160s.mat/content"><code>20200627_052441_ch08751_to_ch10000_whale_raw_L160s.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">985.42M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/5823343/files/20200627_052441_ch10001_to_ch15000_whale_raw_L160s.mat/content"><code>20200627_052441_ch10001_to_ch15000_whale_raw_L160s.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">3938.63M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-trondheim-submarine-ships</code></strong> — Trondheimsfjord Ocean-Bottom Submarine Cable Ship Tracking DAS Dataset (Norway) (1 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–1 of 1)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/18851481/files/Trondheim_DAS_Data.7z/content"><code>Trondheim_DAS_Data.7z</code></a></td>
        <td><code>.7z</code></td>
        <td align="right">60564.67M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-marlinks-north-sea</code></strong> — Marlinks-NS North Sea Submarine Cable DAS Dataset for Vessel Detection (5 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 5)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/15611778/files/dataset_sensor_range_1440_1690_0.h5/content"><code>dataset_sensor_range_1440_1690_0.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">13462.08M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/15611778/files/README.pdf/content"><code>README.pdf</code></a></td>
        <td><code>.pdf</code></td>
        <td align="right">96617B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/15611778/files/README.md/content"><code>README.md</code></a></td>
        <td><code>.md</code></td>
        <td align="right">23103B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/15611778/files/misc.zip/content"><code>misc.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">6706B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/15611778/files/src.zip/content"><code>src.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">3991B</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-abyss-offshore-optodas</code></strong> — ABYSS Permanent Offshore Subsea Cable 20-Hour Continuous OptoDAS Dataset (Chile) (10 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 10)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/17143738/files/18_20.zip/content"><code>18_20.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">4569.81M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/17143738/files/10_12.zip/content"><code>10_12.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">4561.45M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/17143738/files/00_02.zip/content"><code>00_02.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">4557.02M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/17143738/files/14_16.zip/content"><code>14_16.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">4556.07M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/17143738/files/02_04.zip/content"><code>02_04.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">4555.69M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-emso-catania-mediterranean</code></strong> — EMSO Western Ionian Sea Facility Submarine DAS Array (Offshore Catania, Sicily) (10 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 10)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/17571118/files/decimated_20250605T021802.010365_1010_seconds_10_Hz.npy/content"><code>decimated_20250605T021802.010365_1010_seconds_10_Hz.npy</code></a></td>
        <td><code>.npy</code></td>
        <td align="right">466.19M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/17571118/files/decimated_20250602T231502.010365_970_seconds_10_Hz.npy/content"><code>decimated_20250602T231502.010365_970_seconds_10_Hz.npy</code></a></td>
        <td><code>.npy</code></td>
        <td align="right">447.73M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/17571118/files/decimated_20250522T225003.010523_930_seconds_10_Hz.npy/content"><code>decimated_20250522T225003.010523_930_seconds_10_Hz.npy</code></a></td>
        <td><code>.npy</code></td>
        <td align="right">429.27M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/17571118/files/decimated_20250611T224503.011263_1490_seconds_10_Hz.npy/content"><code>decimated_20250611T224503.011263_1490_seconds_10_Hz.npy</code></a></td>
        <td><code>.npy</code></td>
        <td align="right">168.41M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/17571118/files/decimated_20250610T030504.010529_1050_seconds_10_Hz.npy/content"><code>decimated_20250610T030504.010529_1050_seconds_10_Hz.npy</code></a></td>
        <td><code>.npy</code></td>
        <td align="right">118.68M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-sicily-microseisms-das</code></strong> — Offshore Sicily Submarine Cable Joint DAS Observations &amp; Microseism Waveform Dataset (3 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–3 of 3)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/20668434/files/DAS_data.zip/content"><code>DAS_data.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">8217.06M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/20668434/files/simulations.zip/content"><code>simulations.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">11277.64M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/20668434/files/README.txt/content"><code>README.txt</code></a></td>
        <td><code>.txt</code></td>
        <td align="right">2874B</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-santorini-kolumbo-submarine</code></strong> — Santorini &amp; Kolumbo Volcanic Chain Submarine Fiber-Optic DAS Dataset (Greece) (3 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–3 of 3)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/11241132/files/microseisms_data_20211126_1129.zip/content"><code>microseisms_data_20211126_1129.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">1065.77M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/11241132/files/earthquake_data_20211023_0240.zip/content"><code>earthquake_data_20211023_0240.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">291.68M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/11241132/files/earthquake_data_20211023_1649.zip/content"><code>earthquake_data_20211023_1649.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">194.18M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-multisite-finwhale-das</code></strong> — Multi-Ocean Submarine DAS Fin Whale Waveform Dataset (OOI Pacific, Svalbard Arctic, Mediterranean) (1 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–1 of 1)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/15008561/files/data.zip/content"><code>data.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">1808.04M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-utqiagvik-arctic-seaice</code></strong> — Arctic Ocean Landfast Sea Ice &amp; Marine Acoustic DAS Dataset (Utqiagvik, Alaska) (6 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 6)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/23221461/files/pisces_2025_Fs5Hz.zip/content"><code>pisces_2025_Fs5Hz.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">1752.24M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/23221461/files/pisces_2025_hammer_signals.zip/content"><code>pisces_2025_hammer_signals.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">1126.08M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/23221461/files/channel_geometry_full.npz/content"><code>channel_geometry_full.npz</code></a></td>
        <td><code>.npz</code></td>
        <td align="right">17768B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/23221461/files/README_pisces_2025_hammer_signals.txt/content"><code>README_pisces_2025_hammer_signals.txt</code></a></td>
        <td><code>.txt</code></td>
        <td align="right">5329B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/23221461/files/channel_geometry_L.npz/content"><code>channel_geometry_L.npz</code></a></td>
        <td><code>.npz</code></td>
        <td align="right">4410B</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>oedi-porotomo-brady</code></strong> — PoroTomo Natural Laboratory Horizontal &amp; Vertical DAS (Brady Hot Springs, NV) (100 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 100)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://nrel-pds-porotomo.s3.amazonaws.com/DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164618.h5"><code>DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164618.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">998.7M</td>
      </tr>
      <tr>
        <td><a href="https://nrel-pds-porotomo.s3.amazonaws.com/DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164648.h5"><code>DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164648.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">998.7M</td>
      </tr>
      <tr>
        <td><a href="https://nrel-pds-porotomo.s3.amazonaws.com/DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164718.h5"><code>DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164718.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">998.7M</td>
      </tr>
      <tr>
        <td><a href="https://nrel-pds-porotomo.s3.amazonaws.com/DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164748.h5"><code>DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164748.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">998.7M</td>
      </tr>
      <tr>
        <td><a href="https://nrel-pds-porotomo.s3.amazonaws.com/DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164818.h5"><code>DAS/H5/DASH/20160311/PoroTomo_iDAS16043_160311164818.h5</code></a></td>
        <td><code>.h5</code></td>
        <td align="right">998.7M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-tangshan-china</code></strong> — Tangshan Fault Zone Earthquake Monitoring DAS Dataset (Hebei, China) (5 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 5)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/4554758/files/20200716141100.mat/content"><code>20200716141100.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">14.31M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/4554758/files/20200719022500.mat/content"><code>20200719022500.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">14.31M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/4554758/files/20200716171200.mat/content"><code>20200716171200.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">14.31M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/4554758/files/20200720222100.mat/content"><code>20200720222100.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">7.16M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/4554758/files/CH1000_det_event.mat/content"><code>CH1000_det_event.mat</code></a></td>
        <td><code>.mat</code></td>
        <td align="right">164842B</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-rhonegletscher-alps</code></strong> — Rhonegletscher Cryoseismological Glacier DAS Dataset (Swiss Alps) (2 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–2 of 2)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/13890738/files/denoised_data.zip/content"><code>denoised_data.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">12816.33M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/13890738/files/denoised_data_synthetic.zip/content"><code>denoised_data_synthetic.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">42.97M</td>
      </tr>
    </tbody>
  </table>
</details>
