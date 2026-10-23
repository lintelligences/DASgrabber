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

### Validated Global Datasets (12/12 Passed)

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
      <td>North America — Offshore Pacific City, Oregon, USA</td>
      <td><code>http_directory</code></td>
      <td>Multi-TB</td>
      <td align="right">19</td>
      <td><code>PASS (PDF Document (%PDF))</code></td>
      <td><a href="http://piweb.ooirsn.uw.edu/das/">Endpoint</a> · <a href="manifests/uw-ooi-rca-2021.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>uw-ooi-rca-2024</code></td>
      <td>North America — Offshore Central Oregon, USA</td>
      <td><code>http_directory</code></td>
      <td>Multi-TB</td>
      <td align="right">2787</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="http://piweb.ooirsn.uw.edu/das24/data/">Endpoint</a> · <a href="manifests/uw-ooi-rca-2024.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>uw-ooi-rca-2025-optodas</code></td>
      <td>North America — Offshore Oregon, USA (OOI Southern Cable)</td>
      <td><code>http_directory</code></td>
      <td>1.2 TB</td>
      <td align="right">570</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="http://piweb.ooirsn.uw.edu/das25/data/OptoDAS/">Endpoint</a> · <a href="manifests/uw-ooi-rca-2025-optodas.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>uw-ooi-rca-2025-multidas</code></td>
      <td>North America — Offshore Oregon, USA (OOI North &amp; South Cables)</td>
      <td><code>http_directory</code></td>
      <td>3.9 TB</td>
      <td align="right">480</td>
      <td><code>PASS (HDF5 (\x89HDF))</code></td>
      <td><a href="http://piweb.ooirsn.uw.edu/das25/data/MultiDAS/">Endpoint</a> · <a href="manifests/uw-ooi-rca-2025-multidas.json">Manifest</a></td>
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
      <td><code>zenodo-muroto-japan</code></td>
      <td>Asia-Pacific — Offshore Cape Muroto, Shikoku, Japan (Nankai Trough)</td>
      <td><code>zenodo_api</code></td>
      <td>2.72 GB</td>
      <td align="right">5</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/7935235">Endpoint</a> · <a href="manifests/zenodo-muroto-japan.json">Manifest</a></td>
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
      <td><code>zenodo-longriqu-tibetan-plateau</code></td>
      <td>Asia — Longriqu Fault, Eastern Tibetan Plateau, Sichuan, China</td>
      <td><code>zenodo_api</code></td>
      <td>25.4 MB</td>
      <td align="right">1</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/22282258">Endpoint</a> · <a href="manifests/zenodo-longriqu-tibetan-plateau.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-svalbard-whale</code></td>
      <td>Europe / Arctic — Isfjorden, Svalbard, Norway</td>
      <td><code>zenodo_api</code></td>
      <td>13.5 GB</td>
      <td align="right">11</td>
      <td><code>PASS (MATLAB v5 MAT-file)</code></td>
      <td><a href="https://zenodo.org/api/records/5823343">Endpoint</a> · <a href="manifests/zenodo-svalbard-whale.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-zugspitze-alps</code></td>
      <td>Europe — Mt. Zugspitze, Bavarian/Tyrolean Alps, Germany/Austria</td>
      <td><code>zenodo_api</code></td>
      <td>4.9 GB</td>
      <td align="right">4</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/19226183">Endpoint</a> · <a href="manifests/zenodo-zugspitze-alps.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-reykjanes-iceland</code></td>
      <td>Europe — Grindavík / Svartsengi / Thorbjörn, Reykjanes Peninsula, Iceland</td>
      <td><code>zenodo_api</code></td>
      <td>2.2 MB</td>
      <td align="right">1</td>
      <td><code>PASS (UTF-8 Text / CSV / Script)</code></td>
      <td><a href="https://zenodo.org/api/records/6337788">Endpoint</a> · <a href="manifests/zenodo-reykjanes-iceland.json">Manifest</a></td>
    </tr>
    <tr>
      <td><code>zenodo-rhonegletscher-alps</code></td>
      <td>Europe — Rhonegletscher, Valais, Swiss Alps, Switzerland</td>
      <td><code>zenodo_api</code></td>
      <td>13.5 GB (denoised + synthetic bundles)</td>
      <td align="right">2</td>
      <td><code>PASS (ZIP Archive (PK\x03\x04))</code></td>
      <td><a href="https://zenodo.org/api/records/13890738">Endpoint</a> · <a href="manifests/zenodo-rhonegletscher-alps.json">Manifest</a></td>
    </tr>
  </tbody>
</table>

### Manifest File Inspector (Static Preview)

<details>
  <summary><strong><code>uw-ooi-rca-2021</code></strong> — OOI Regional Cabled Array (RCA) RAPID Community DAS Experiment (2021) (19 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–5 of 19)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/processed/metadata/changes.pdf"><code>changes.pdf</code></a></td>
        <td><code>.pdf</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/processed/metadata/readme.pdf"><code>readme.pdf</code></a></td>
        <td><code>.pdf</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/processed/metadata/Geometry/RCA_RPL%20%28Segment%20S1%20and%20S5%29.xlsx"><code>Geometry/RCA_RPL (Segment S1 and S5).xlsx</code></a></td>
        <td><code>.xlsx</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/processed/metadata/Optasense/OOI_RCA_OptaSense_DAS_intro.ipynb"><code>Optasense/OOI_RCA_OptaSense_DAS_intro.ipynb</code></a></td>
        <td><code>.ipynb</code></td>
        <td align="right">-</td>
      </tr>
      <tr>
        <td><a href="http://piweb.ooirsn.uw.edu/das/processed/metadata/Optasense/Summary-UW-OOI-QuantX-DataAcquisition-October2021%20-%20Issue%202.pdf"><code>Optasense/Summary-UW-OOI-QuantX-DataAcquisition-October2021 - Issue 2.pdf</code></a></td>
        <td><code>.pdf</code></td>
        <td align="right">-</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>uw-ooi-rca-2024</code></strong> — OOI Regional Cabled Array Multiplexed DAS Experiment (May 2024) (2787 indexed files)</summary>
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
  <summary><strong><code>uw-ooi-rca-2025-optodas</code></strong> — OOI Regional Cabled Array OptoDAS Experiment (Nov 2025 – Jan 2026) (570 indexed files)</summary>
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
  <summary><strong><code>uw-ooi-rca-2025-multidas</code></strong> — OOI Regional Cabled Array Nokia Multi-Span DAS Experiment (Nov 2025 – Jan 2026) (480 indexed files)</summary>
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
  <summary><strong><code>zenodo-longriqu-tibetan-plateau</code></strong> — Longriqu Fault Earthquake DAS Observations (Eastern Tibetan Plateau, China) (1 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–1 of 1)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/22282258/files/Data-origin.zip/content"><code>Data-origin.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">24.21M</td>
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
  <summary><strong><code>zenodo-zugspitze-alps</code></strong> — Mt. Zugspitze Alpine Permafrost DAS Dataset (German/Austrian Alps) (4 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–4 of 4)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/19226183/files/PPSD.zip/content"><code>PPSD.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">2335.91M</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/19226183/files/stack_xcorr.py/content"><code>stack_xcorr.py</code></a></td>
        <td><code>.py</code></td>
        <td align="right">1655B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/19226183/files/read_data.py/content"><code>read_data.py</code></a></td>
        <td><code>.py</code></td>
        <td align="right">256B</td>
      </tr>
      <tr>
        <td><a href="https://zenodo.org/api/records/19226183/files/CROSS-CORRELATIONS.zip/content"><code>CROSS-CORRELATIONS.zip</code></a></td>
        <td><code>.zip</code></td>
        <td align="right">9751.02M</td>
      </tr>
    </tbody>
  </table>
</details>
<details>
  <summary><strong><code>zenodo-reykjanes-iceland</code></strong> — Thorbjörn / Reykjanes Peninsula Volcanic Unrest DAS Dataset (Iceland) (1 indexed files)</summary>
  <table>
    <thead>
      <tr><th align="left">Relative Path (Sample 1–1 of 1)</th><th align="left">Ext</th><th align="right">Remote Size</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><a href="https://zenodo.org/api/records/6337788/files/events_merged-all.csv/content"><code>events_merged-all.csv</code></a></td>
        <td><code>.csv</code></td>
        <td align="right">2.09M</td>
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
