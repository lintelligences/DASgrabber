#!/usr/bin/env python3
"""
das_catalog.py — Query, filter, inspect, and verify public DAS dataset entries
in catalog/datasets.json without downloading raw waveform data.

Usage examples:
  python3 scripts/das_catalog.py list
  python3 scripts/das_catalog.py list --protocol http_directory
  python3 scripts/das_catalog.py show uw-ooi-rca-2025-optodas
  python3 scripts/das_catalog.py probe uw-ooi-rca-2024
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "catalog" / "datasets.json"
MANIFESTS_DIR = REPO_ROOT / "manifests"


def load_catalog(path: Path = DEFAULT_CATALOG) -> Dict[str, Any]:
    if not path.exists():
        sys.exit(f"Error: Catalog file not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def cmd_list(args: argparse.Namespace) -> None:
    catalog = load_catalog(Path(args.catalog))
    datasets: List[Dict[str, Any]] = catalog.get("datasets", [])

    if args.protocol:
        datasets = [
            d for d in datasets
            if d.get("access_protocol", "").lower() == args.protocol.lower()
        ]
    if args.search:
        q = args.search.lower()
        datasets = [
            d for d in datasets
            if q in json.dumps(d).lower()
        ]

    if not datasets:
        print("No matching datasets found.")
        return

    print(f"{'ID':<28} {'PROTOCOL':<18} {'EST. SIZE':<12} {'REGION / TITLE'}")
    print("-" * 105)
    for d in datasets:
        ds_id = d.get("id", "")
        proto = d.get("access_protocol", "")
        size = d.get("estimated_size", "unknown")
        title = d.get("title", "")
        print(f"{ds_id:<28} {proto:<18} {size:<12} {title}")


def cmd_show(args: argparse.Namespace) -> None:
    catalog = load_catalog(Path(args.catalog))
    for d in catalog.get("datasets", []):
        if d.get("id") == args.dataset_id:
            print(json.dumps(d, indent=2))
            manifest_path = MANIFESTS_DIR / f"{args.dataset_id}.json"
            if manifest_path.exists():
                with manifest_path.open("r", encoding="utf-8") as mf:
                    mdata = json.load(mf)
                file_count = len(mdata.get("files", []))
                print(f"\n[Local Manifest Available]: {manifest_path} ({file_count} indexed files)")
            else:
                print(f"\n[No Local Manifest Yet]: Run `python3 scripts/crawl_http_index.py --dataset {args.dataset_id}` to index files.")
            return
    sys.exit(f"Dataset '{args.dataset_id}' not found in catalog.")


def cmd_probe(args: argparse.Namespace) -> None:
    """Send lightweight HEAD/GET requests to HTTP entrypoints to verify reachability."""
    catalog = load_catalog(Path(args.catalog))
    targets = [
        d for d in catalog.get("datasets", [])
        if args.dataset_id in (None, "all", d.get("id"))
    ]
    if not targets:
        sys.exit(f"Dataset '{args.dataset_id}' not found.")

    for d in targets:
        print(f"\n=== Probing {d['id']} ({d['title']}) ===")
        entrypoints = d.get("entrypoints", {})
        for name, url in entrypoints.items():
            if not url.startswith(("http://", "https://")):
                print(f"  [{name}] {url} -> skipped (non-HTTP protocol: {d.get('access_protocol')})")
                continue
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "DAS-Catalog-Probe/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    print(f"  [{name}] {url} -> HTTP {resp.status} OK")
            except urllib.error.HTTPError as e:
                print(f"  [{name}] {url} -> HTTP {e.code} ({e.reason})")
            except Exception as e:
                print(f"  [{name}] {url} -> ERROR: {e}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect and query the public DAS dataset catalog.")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Path to datasets.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List cataloged DAS datasets")
    p_list.add_argument("--protocol", help="Filter by access_protocol (e.g. http_directory, aws_s3_anonymous)")
    p_list.add_argument("--search", help="Keyword filter across all metadata fields")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Show full metadata for a dataset ID")
    p_show.add_argument("dataset_id", help="Dataset ID (e.g. uw-ooi-rca-2025-optodas)")
    p_show.set_defaults(func=cmd_show)

    p_probe = sub.add_parser("probe", help="Check HTTP reachability of dataset entrypoints")
    p_probe.add_argument("dataset_id", nargs="?", default="all", help="Dataset ID or 'all'")
    p_probe.set_defaults(func=cmd_probe)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    parsed_args = parser.parse_args()
    parsed_args.func(parsed_args)
