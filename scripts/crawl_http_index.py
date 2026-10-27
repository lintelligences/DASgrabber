#!/usr/bin/env python3
"""
crawl_http_index.py — Build lightweight JSON file manifests (`manifests/<dataset_id>.json`)
for cataloged public DAS datasets WITHOUT downloading bulk waveform files.

Supports three direct, unauthenticated protocols:
  1. `http_directory`   — Open Apache/Nginx HTML autoindex trees (e.g. UW piweb.ooirsn.uw.edu)
  2. `aws_s3_anonymous` — Public AWS S3 buckets via standard HTTPS ListObjectsV2 XML API
  3. `zenodo_api`       — Zenodo open-access records via https://zenodo.org/api/records/<id>

Usage examples:
  python3 scripts/crawl_http_index.py --dataset uw-ooi-rca-2024
  python3 scripts/crawl_http_index.py --dataset oedi-porotomo-brady
  python3 scripts/crawl_http_index.py --dataset zenodo-muroto-japan
  python3 scripts/crawl_http_index.py --all
"""

import argparse
import html.parser
import json
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "catalog" / "datasets.json"
MANIFESTS_DIR = REPO_ROOT / "manifests"
UA_HEADERS = {"User-Agent": "DAS-Catalog-Indexer/2.0 (Metadata-Only; No-Bulk-Download)"}

PRIMARY_WAVEFORM_EXTS = {
    ".h5", ".hdf5", ".mat", ".mseed", ".sgy", ".segy", ".npy", ".npz", ".tdms", ".bin", ".sac",
}
ARCHIVE_WAVEFORM_EXTS = {".zip", ".7z", ".tar", ".gz", ".tgz"}


def _urlopen_with_ssl_fallback(req: urllib.request.Request, timeout: int = 30):
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as exc:
        if isinstance(getattr(exc, "reason", None), ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in str(exc):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return urllib.request.urlopen(req, timeout=timeout, context=ctx)
        raise


def _file_priority_key(f: Dict[str, Any]) -> Tuple[int, int, str]:
    """Sort primary observed waveform files first, then large waveform archives (>5 MB), then auxiliary/geometry/simulation files."""
    ext = (f.get("extension") or "").lower()
    size_bytes = int(f.get("size_bytes") or 0)
    rel = (f.get("relative_path") or "").lower()
    is_aux_name = any(
        kw in rel for kw in ("geometry", "position", "simulation", "synthetic", "readme", "license", "channelinfo", "model")
    )
    if is_aux_name:
        return (2, -size_bytes, rel)
    if ext in PRIMARY_WAVEFORM_EXTS and (size_bytes == 0 or size_bytes >= 100 * 1024):
        return (0, -size_bytes, rel)
    if ext in ARCHIVE_WAVEFORM_EXTS and (size_bytes == 0 or size_bytes >= 5 * 1024 * 1024):
        return (1, -size_bytes, rel)
    return (3, -size_bytes, rel)


class DirectoryIndexParser(html.parser.HTMLParser):
    """Parses standard Apache/Nginx autoindex HTML pages to extract hrefs."""

    def __init__(self) -> None:
        super().__init__()
        self.links: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() == "a":
            for k, v in attrs:
                if k.lower() == "href" and v:
                    self.links.append(v)


def is_parent_or_sort_link(href: str, base_url: str) -> bool:
    if href.startswith(("?", "#", "mailto:", "javascript:")):
        return True
    if href in ("/", "../", "./"):
        return True
    resolved = urllib.parse.urljoin(base_url, href)
    if not resolved.startswith(base_url):
        return True
    return False


def parse_apache_row_metadata(raw_html: str, href: str) -> Dict[str, Optional[str]]:
    pattern = re.compile(
        re.escape(f'href="{href}"')
        + r".*?</a>\s*([0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2}|[0-9]{2}-[A-Za-z]{3}-[0-9]{4}\s+[0-9]{2}:[0-9]{2})?\s*([0-9.]+[KMGTP]?|-)?",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(raw_html)
    if match:
        return {
            "last_modified": (match.group(1) or "").strip() or None,
            "size_hint": (match.group(2) or "").strip() or None,
        }
    return {"last_modified": None, "size_hint": None}


def fetch_text(url: str, timeout: int = 30, retries: int = 3) -> str:
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA_HEADERS)
            with _urlopen_with_ssl_fallback(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_err = exc
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_err}")


def crawl_http_directory(
    root_url: str,
    max_depth: int = 2,
    max_dirs: int = 25,
    delay_sec: float = 0.1,
) -> Dict[str, Any]:
    if not root_url.endswith("/"):
        root_url += "/"

    visited_dirs: Set[str] = set()
    directories: List[str] = []
    files: List[Dict[str, Any]] = []
    queue: List[Tuple[str, int]] = [(root_url, 0)]

    while queue and len(visited_dirs) < max_dirs:
        current_url, depth = queue.pop(0)
        if current_url in visited_dirs:
            continue
        visited_dirs.add(current_url)
        print(f"  [http_directory depth={depth}] {current_url}")

        try:
            raw_html = fetch_text(current_url)
        except Exception as exc:
            print(f"    ! Warning: {exc}", file=sys.stderr)
            continue

        parser = DirectoryIndexParser()
        parser.feed(raw_html)

        for href in parser.links:
            if is_parent_or_sort_link(href, current_url):
                continue
            full_url = urllib.parse.urljoin(current_url, href)
            rel_path = urllib.parse.unquote(full_url[len(root_url):] if full_url.startswith(root_url) else href)
            meta = parse_apache_row_metadata(raw_html, href)

            if href.endswith("/"):
                directories.append(rel_path)
                if depth + 1 <= max_depth:
                    queue.append((full_url, depth + 1))
            else:
                ext = Path(urllib.parse.urlparse(full_url).path).suffix.lower()
                files.append(
                    {
                        "relative_path": rel_path,
                        "url": full_url,
                        "extension": ext,
                        "last_modified": meta["last_modified"],
                        "size_hint": meta["size_hint"],
                    }
                )

        if delay_sec > 0 and queue:
            time.sleep(delay_sec)

    return {
        "protocol": "http_directory",
        "root_url": root_url,
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "directories_visited": len(visited_dirs),
        "subdirectories_found": len(directories),
        "files_found": len(files),
        "directories": sorted(set(directories)),
        "files": files,
    }


def crawl_s3_anonymous(base_url: str, prefix: str = "", max_keys: int = 100) -> Dict[str, Any]:
    if not base_url.endswith("/"):
        base_url += "/"
    list_url = f"{base_url}?list-type=2&max-keys={max_keys}&prefix={urllib.parse.quote(prefix)}"
    print(f"  [aws_s3_anonymous] {list_url}")
    xml_text = fetch_text(list_url)
    root = ET.fromstring(xml_text)
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

    files: List[Dict[str, Any]] = []
    for item in root.findall("s3:Contents", ns):
        key_el = item.find("s3:Key", ns)
        size_el = item.find("s3:Size", ns)
        lm_el = item.find("s3:LastModified", ns)
        if key_el is None or not key_el.text or key_el.text.endswith("/"):
            continue
        key = key_el.text
        size_bytes = int(size_el.text) if (size_el is not None and size_el.text) else 0
        lm = lm_el.text if lm_el is not None else None
        full_url = urllib.parse.urljoin(base_url, urllib.parse.quote(key, safe="/"))
        ext = Path(key).suffix.lower()
        files.append(
            {
                "relative_path": key,
                "url": full_url,
                "extension": ext,
                "last_modified": lm,
                "size_bytes": size_bytes,
                "size_hint": f"{size_bytes / (1024 * 1024):.1f}M" if size_bytes >= 1024 * 1024 else f"{size_bytes}B",
            }
        )

    return {
        "protocol": "aws_s3_anonymous",
        "root_url": base_url,
        "s3_prefix": prefix,
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "files_found": len(files),
        "files": files,
    }


def crawl_zenodo_record(record_id: str) -> Dict[str, Any]:
    api_url = f"https://zenodo.org/api/records/{record_id}"
    print(f"  [zenodo_api] {api_url}")
    data = json.loads(fetch_text(api_url))
    files: List[Dict[str, Any]] = []
    for f in data.get("files", []):
        key = f.get("key", "")
        size_bytes = int(f.get("size", 0))
        checksum = f.get("checksum")
        content_url = f.get("links", {}).get("self") or f"https://zenodo.org/records/{record_id}/files/{urllib.parse.quote(key)}?download=1"
        ext = Path(key).suffix.lower()
        files.append(
            {
                "relative_path": key,
                "url": content_url,
                "extension": ext,
                "size_bytes": size_bytes,
                "size_hint": f"{size_bytes / (1024 * 1024):.2f}M" if size_bytes >= 1024 * 1024 else f"{size_bytes}B",
                "checksum": checksum,
            }
        )

    return {
        "protocol": "zenodo_api",
        "root_url": api_url,
        "zenodo_record_id": record_id,
        "doi": data.get("doi"),
        "title": data.get("metadata", {}).get("title"),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "files_found": len(files),
        "files": files,
    }


def build_manifest_for_dataset(ds: Dict[str, Any], max_depth: int = 2, max_dirs: int = 15) -> Dict[str, Any]:
    ds_id = ds["id"]
    proto = ds.get("access_protocol")
    print(f"\n=== Indexing {ds_id} ({proto}) ===")

    if proto == "http_directory":
        target_url = ds.get("crawl_url") or ds["base_url"]
        manifest = crawl_http_directory(target_url, max_depth=max_depth, max_dirs=max_dirs)
    elif proto == "aws_s3_anonymous":
        manifest = crawl_s3_anonymous(ds["base_url"], prefix=ds.get("s3_prefix", ""))
    elif proto == "zenodo_api":
        manifest = crawl_zenodo_record(str(ds["zenodo_record_id"]))
    else:
        raise ValueError(f"Unsupported protocol '{proto}' for dataset {ds_id}")

    manifest["files"] = sorted(manifest.get("files", []), key=_file_priority_key)
    manifest["dataset_id"] = ds_id
    out_path = MANIFESTS_DIR / f"{ds_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  -> Wrote {out_path} ({manifest['files_found']} files indexed)")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Index remote DAS datasets into lightweight local JSON manifests.")
    parser.add_argument("--dataset", help="Dataset ID from catalog/datasets.json")
    parser.add_argument("--all", action="store_true", help="Crawl and build manifests for all datasets in catalog/datasets.json")
    parser.add_argument("--max-depth", type=int, default=2, help="Max depth for HTTP directories (default: 2)")
    parser.add_argument("--max-dirs", type=int, default=15, help="Max directories to visit per HTTP dataset (default: 15)")
    args = parser.parse_args()

    if not args.dataset and not args.all:
        parser.error("Specify --dataset <id> or --all")

    with DEFAULT_CATALOG.open("r", encoding="utf-8") as f:
        catalog = json.load(f)

    datasets = catalog.get("datasets", [])
    if args.dataset:
        datasets = [d for d in datasets if d.get("id") == args.dataset]
        if not datasets:
            sys.exit(f"Dataset '{args.dataset}' not found in catalog.")

    for ds in datasets:
        build_manifest_for_dataset(ds, max_depth=args.max_depth, max_dirs=args.max_dirs)


if __name__ == "__main__":
    main()
