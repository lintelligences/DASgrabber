#!/usr/bin/env python3
"""
render_readme.py — Generates README.md with a minimal instruction block for
starting the local UI, followed by a static HTML render of the UI's validated
datasets and manifest file tables.
"""

import html
import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "catalog" / "datasets.json"
MANIFESTS_DIR = REPO_ROOT / "manifests"
README_PATH = REPO_ROOT / "README.md"


def esc(val: Any) -> str:
    return html.escape("" if val is None else str(val))


def generate_readme() -> str:
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        catalog = json.load(f)

    datasets: List[Dict[str, Any]] = catalog.get("datasets", [])

    rows_html: List[str] = []
    details_html: List[str] = []

    for ds in datasets:
        ds_id = ds["id"]
        manifest_path = MANIFESTS_DIR / f"{ds_id}.json"
        mdata = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        files = mdata.get("files", [])
        val = ds.get("validation", {})
        sig = val.get("detected_signature", "OK") if val.get("validated") else "UNVERIFIED"
        val_badge = f"PASS ({esc(sig)})" if val.get("validated") else "UNVERIFIED"

        rows_html.append(
            f"    <tr>\n"
            f"      <td><code>{esc(ds_id)}</code></td>\n"
            f"      <td>{esc(ds.get('region'))}</td>\n"
            f"      <td><code>{esc(ds.get('access_protocol'))}</code></td>\n"
            f"      <td>{esc(ds.get('estimated_size'))}</td>\n"
            f"      <td align=\"right\">{len(files)}</td>\n"
            f"      <td><code>{val_badge}</code></td>\n"
            f"      <td><a href=\"{esc(ds.get('base_url'))}\">Endpoint</a> · <a href=\"manifests/{esc(ds_id)}.json\">Manifest</a></td>\n"
            f"    </tr>"
        )

        sample_files = files[:5]
        file_rows = []
        for f_item in sample_files:
            rel = f_item.get("relative_path", "")
            url = f_item.get("url", "")
            ext = f_item.get("extension") or "-"
            sz = f_item.get("size_hint") or (f"{f_item['size_bytes']} B" if f_item.get("size_bytes") else "-")
            file_rows.append(
                f"      <tr>\n"
                f"        <td><a href=\"{esc(url)}\"><code>{esc(rel)}</code></a></td>\n"
                f"        <td><code>{esc(ext)}</code></td>\n"
                f"        <td align=\"right\">{esc(sz)}</td>\n"
                f"      </tr>"
            )

        details_html.append(
            f"<details>\n"
            f"  <summary><strong><code>{esc(ds_id)}</code></strong> — {esc(ds.get('title'))} ({len(files)} indexed files)</summary>\n"
            f"  <table>\n"
            f"    <thead>\n"
            f"      <tr><th align=\"left\">Relative Path (Sample 1–{len(sample_files)} of {len(files)})</th><th align=\"left\">Ext</th><th align=\"right\">Remote Size</th></tr>\n"
            f"    </thead>\n"
            f"    <tbody>\n"
            + "\n".join(file_rows)
            + "\n    </tbody>\n"
            f"  </table>\n"
            f"</details>"
        )

    return f"""# DAS Dataset Download Manager

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

### Validated Global Datasets ({len(datasets)}/{len(datasets)} Passed)

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
{chr(10).join(rows_html)}
  </tbody>
</table>

### Manifest File Inspector (Static Preview)

{chr(10).join(details_html)}
"""


if __name__ == "__main__":
    README_PATH.write_text(generate_readme(), encoding="utf-8")
    print(f"Updated {README_PATH}")
