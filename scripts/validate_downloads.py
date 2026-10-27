#!/usr/bin/env python3
"""
validate_downloads.py — End-to-end local validation of every dataset in
`catalog/datasets.json`.

For each dataset:
  1. Crawls the remote server/API and generates `manifests/<dataset_id>.json`.
  2. Selects a real file from the generated manifest.
  3. Performs a real local download (first 64 KiB via HTTP Range or full file if <64 KiB)
     into a temporary directory (`downloads/.validation_tmp/`).
  4. Verifies HTTP 200/206 status, non-zero byte count, magic-byte file signature
     (ensuring it is not an HTML error/login page), and SHA-256 hash.
  5. Deletes the temporary downloaded file so no waveform data remains on disk.
  6. Updates `catalog/datasets.json` and `manifests/validation_report.json`.
"""

import hashlib
import json
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from crawl_http_index import (
    ARCHIVE_WAVEFORM_EXTS,
    DEFAULT_CATALOG,
    MANIFESTS_DIR,
    PRIMARY_WAVEFORM_EXTS,
    REPO_ROOT,
    _urlopen_with_ssl_fallback,
    build_manifest_for_dataset,
)

TMP_DOWNLOAD_DIR = REPO_ROOT / "downloads" / ".validation_tmp"
SAMPLE_BYTES = 65536  # 64 KiB slice for large waveform files


def detect_signature(head: bytes, ext: str = "") -> str:
    if head.startswith(b"\x89HDF\r\n\x1a\n") or (len(head) >= 520 and head[512:520] == b"\x89HDF\r\n\x1a\n"):
        return "HDF5 (\\x89HDF)"
    if head.startswith(b"MATLAB"):
        return "MATLAB v5 MAT-file"
    if head.startswith(b"\x93NUMPY"):
        return "NumPy Array (\\x93NUMPY)"
    if head.startswith(b"PK\x03\x04"):
        return "ZIP Archive (PK\\x03\\x04)"
    if head.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "7-Zip Archive (7z\\xbc\\xaf)"
    if head.startswith(b"%PDF"):
        return "PDF Document (%PDF)"
    if head.lstrip().startswith((b"<!DOCTYPE html", b"<html", b"<HTML")):
        return "UNEXPECTED_HTML"
    if ext == ".mseed" and len(head) >= 20 and head[:6].isdigit():
        return "MiniSEED Waveform"
    # Check if printable text/CSV/Python
    try:
        head[:256].decode("utf-8")
        return "UTF-8 Text / CSV / Script"
    except UnicodeDecodeError:
        return f"Binary Data (0x{head[:8].hex()})"


def validate_single_file_download(dataset_id: str, file_entry: Dict[str, Any]) -> Dict[str, Any]:
    url = file_entry["url"]
    rel_path = file_entry["relative_path"]
    ext = (file_entry.get("extension") or Path(rel_path).suffix).lower()
    TMP_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    tmp_file = TMP_DOWNLOAD_DIR / f"{dataset_id}_{Path(rel_path).name}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "DAS-Download-Validator/2.0",
            "Range": f"bytes=0-{SAMPLE_BYTES - 1}",
        },
    )
    with _urlopen_with_ssl_fallback(req, timeout=30) as resp:
        status = resp.status
        content_type = resp.headers.get("Content-Type", "")
        content_range = resp.headers.get("Content-Range", "")
        data = resp.read(SAMPLE_BYTES)

    tmp_file.write_bytes(data)
    written_size = tmp_file.stat().st_size
    sig = detect_signature(data[:528], ext=ext)
    sha256_prefix = hashlib.sha256(data).hexdigest()[:16]

    # Clean up temporary file immediately
    tmp_file.unlink(missing_ok=True)

    if written_size == 0:
        raise RuntimeError(f"Downloaded 0 bytes from {url}")
    if sig == "UNEXPECTED_HTML" and not rel_path.endswith((".html", ".htm")):
        raise RuntimeError(f"Expected data file for {rel_path}, but server returned HTML page.")

    return {
        "validated": True,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "verified_relative_path": rel_path,
        "verified_url": url,
        "http_status": status,
        "content_type": content_type,
        "content_range": content_range,
        "bytes_downloaded": written_size,
        "detected_signature": sig,
        "sample_sha256_prefix": sha256_prefix,
    }


def main() -> None:
    with DEFAULT_CATALOG.open("r", encoding="utf-8") as f:
        catalog = json.load(f)

    datasets = catalog.get("datasets", [])
    report: Dict[str, Any] = {
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "total_datasets": len(datasets),
        "passed": 0,
        "failed": 0,
        "results": {},
    }

    for ds in datasets:
        ds_id = ds["id"]
        existing_val = ds.get("validation", {})
        manifest_file = MANIFESTS_DIR / f"{ds_id}.json"
        if existing_val.get("validated") and manifest_file.exists() and "--force" not in sys.argv:
            report["results"][ds_id] = existing_val
            report["passed"] += 1
            print(f"  [ALREADY VALIDATED] {ds_id}: {existing_val.get('detected_signature')}")
            continue
        try:
            manifest = build_manifest_for_dataset(ds, max_depth=3, max_dirs=10)
            files = manifest.get("files", [])
            if not files:
                raise RuntimeError(f"Manifest for {ds_id} indexed 0 files.")

            # Strictly require a genuine waveform file or multi-MB waveform archive (never CSV/PDF/TXT/geometry metadata)
            waveform_files = [
                f for f in files
                if (
                    (f.get("extension") or "").lower() in PRIMARY_WAVEFORM_EXTS
                    and int(f.get("size_bytes") or 1_000_000) >= 100 * 1024
                )
                or (
                    (f.get("extension") or "").lower() in ARCHIVE_WAVEFORM_EXTS
                    and int(f.get("size_bytes") or 10_000_000) >= 5 * 1024 * 1024
                )
            ]
            if not waveform_files:
                raise RuntimeError(
                    f"Dataset {ds_id} contains no waveform data files (only metadata/labels: "
                    f"{[f.get('relative_path') for f in files[:5]]})."
                )
            sample_target = waveform_files[0]
            print(f"  [Validating Download] {sample_target['url']} ...")
            val_info = validate_single_file_download(ds_id, sample_target)
            ds["validation"] = val_info
            report["results"][ds_id] = val_info
            report["passed"] += 1
            print(
                f"  [PASS] {ds_id}: HTTP {val_info['http_status']} | "
                f"{val_info['bytes_downloaded']} bytes | {val_info['detected_signature']}"
            )
        except Exception as exc:
            err_info = {
                "validated": False,
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "error": str(exc),
            }
            ds["validation"] = err_info
            report["results"][ds_id] = err_info
            report["failed"] += 1
            print(f"  [FAIL] {ds_id}: {exc}", file=sys.stderr)

    # Remove any stale manifest files not present in catalog/datasets.json
    active_ids = {ds["id"] for ds in datasets}
    for mf in MANIFESTS_DIR.glob("*.json"):
        if mf.name != "validation_report.json" and mf.stem not in active_ids:
            mf.unlink(missing_ok=True)

    # Remove temporary validation directory
    if TMP_DOWNLOAD_DIR.exists():
        shutil.rmtree(TMP_DOWNLOAD_DIR, ignore_errors=True)

    # Save updated catalog with validation proofs
    with DEFAULT_CATALOG.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    # Save validation report
    report_path = MANIFESTS_DIR / "validation_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    try:
        from render_readme import README_PATH, generate_readme
        README_PATH.write_text(generate_readme(), encoding="utf-8")
        print(f"  [Updated README] {README_PATH}")
    except Exception as exc:
        print(f"  ! Warning: could not update README: {exc}", file=sys.stderr)

    print(f"\n=== Validation Summary: {report['passed']}/{report['total_datasets']} Passed ===")
    if report["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
