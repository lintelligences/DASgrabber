#!/usr/bin/env python3
"""
server.py — Zero-dependency local HTTP server to manage and monitor
public DAS dataset manifests, selective downloads, and Alcatel OptoDAS conversions.

Usage:
  python3 scripts/server.py --port 8765
"""

import argparse
import importlib
import json
import re
import ssl
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

import convert_to_optodas_h5
from crawl_http_index import DEFAULT_CATALOG, MANIFESTS_DIR, REPO_ROOT, build_manifest_for_dataset
from download_dataset import ensure_local_gitignore, verify_safe_destination

UI_FILE = REPO_ROOT / "ui" / "index.html"
ACTIVE_DEST_ROOT = REPO_ROOT / "downloads"

JOBS_LOCK = threading.Lock()
JOBS: Dict[str, Dict[str, Any]] = {}


def get_dest_root(custom_dir: Optional[str] = None) -> Path:
    global ACTIVE_DEST_ROOT
    if custom_dir and custom_dir.strip():
        p = Path(custom_dir.strip()).expanduser()
        if not p.is_absolute():
            p = REPO_ROOT / p
        ACTIVE_DEST_ROOT = verify_safe_destination(p)
    ACTIVE_DEST_ROOT.mkdir(parents=True, exist_ok=True)
    ensure_local_gitignore(ACTIVE_DEST_ROOT)
    return verify_safe_destination(ACTIVE_DEST_ROOT)


def open_url_with_ssl_fallback(req: urllib.request.Request, timeout: int = 60):
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as exc:
        if isinstance(getattr(exc, "reason", None), ssl.SSLError) or "CERTIFICATE_VERIFY_FAILED" in str(exc):
            ctx = ssl._create_unverified_context()
            return urllib.request.urlopen(req, timeout=timeout, context=ctx)
        raise


def load_catalog_data() -> List[Dict[str, Any]]:
    if not DEFAULT_CATALOG.exists():
        return []
    with DEFAULT_CATALOG.open("r", encoding="utf-8") as f:
        return json.load(f).get("datasets", [])


def load_manifest_data(dataset_id: str) -> Optional[Dict[str, Any]]:
    path = MANIFESTS_DIR / f"{dataset_id}.json"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_local_file(dataset_id: str, rel_path: str, dest_root: Path) -> Optional[Path]:
    """Check both `<dest_root>/<dataset_id>/<rel_path>` and `<dest_root>/<rel_path>`."""
    cand_sub = dest_root / dataset_id / rel_path
    if cand_sub.exists():
        return cand_sub
    cand_direct = dest_root / rel_path
    if cand_direct.exists():
        return cand_direct
    cand_name = dest_root / Path(rel_path).name
    if cand_name.exists():
        return cand_name
    return None


def local_dataset_stats(dataset_id: str, dest_root: Path) -> Dict[str, int]:
    ds_dir = dest_root / dataset_id
    count = 0
    total = 0
    optodas_count = 0
    seen_paths = set()

    if ds_dir.exists():
        for p in ds_dir.rglob("*"):
            if p.is_file() and p.name != ".gitignore" and not p.name.endswith(".part") and not p.name.startswith("."):
                seen_paths.add(p.resolve())
                count += 1
                total += p.stat().st_size
                if p.name.endswith("_optodas.hdf5"):
                    optodas_count += 1

    # Also check if manifest files were placed directly in dest_root
    m = load_manifest_data(dataset_id)
    if m and dest_root.exists():
        for f_item in m.get("files", []):
            rel = f_item.get("relative_path", "")
            for cand in (dest_root / rel, dest_root / Path(rel).name):
                if cand.exists() and cand.is_file() and cand.resolve() not in seen_paths:
                    seen_paths.add(cand.resolve())
                    count += 1
                    total += cand.stat().st_size

    return {"file_count": count, "total_bytes": total, "optodas_count": optodas_count}


def run_download_worker(job_id: str, dataset_id: str, files: List[Dict[str, Any]], dest_root: Path) -> None:
    ds_dest = verify_safe_destination(dest_root) / dataset_id
    ensure_local_gitignore(verify_safe_destination(dest_root))
    ensure_local_gitignore(ds_dest)

    with JOBS_LOCK:
        JOBS[job_id]["status"] = "downloading"
        JOBS[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()

    for idx, f_item in enumerate(files, start=1):
        with JOBS_LOCK:
            if JOBS[job_id].get("cancel_requested"):
                JOBS[job_id]["status"] = "cancelled"
                JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
                return
            JOBS[job_id]["current_file_index"] = idx
            JOBS[job_id]["current_file"] = f"{dataset_id}/{f_item['relative_path']}"
            JOBS[job_id]["current_file_bytes"] = 0
            JOBS[job_id]["current_file_total"] = f_item.get("size_bytes") or 0

        rel_path = f_item["relative_path"]
        url = f_item["url"]
        target_path = ds_dest / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        part_path = target_path.with_suffix(target_path.suffix + ".part")

        try:
            existing = part_path.stat().st_size if part_path.exists() else 0
            headers = {"User-Agent": "DAS-Download-Manager/1.0"}
            if existing > 0:
                headers["Range"] = f"bytes={existing}-"

            req = urllib.request.Request(url, headers=headers)
            with open_url_with_ssl_fallback(req, timeout=60) as resp:
                status = resp.status
                content_len = resp.headers.get("Content-Length")
                total_expected = (
                    (existing + int(content_len))
                    if (status == 206 and content_len)
                    else (int(content_len) if content_len else (f_item.get("size_bytes") or 0))
                )
                with JOBS_LOCK:
                    JOBS[job_id]["current_file_total"] = total_expected
                    JOBS[job_id]["current_file_bytes"] = existing if status == 206 else 0

                mode = "ab" if (status == 206 and existing > 0) else "wb"
                with part_path.open(mode) as out_f:
                    while True:
                        with JOBS_LOCK:
                            if JOBS[job_id].get("cancel_requested"):
                                JOBS[job_id]["status"] = "cancelled"
                                JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
                                return
                        chunk = resp.read(256 * 1024)
                        if not chunk:
                            break
                        out_f.write(chunk)
                        with JOBS_LOCK:
                            JOBS[job_id]["current_file_bytes"] += len(chunk)
                            JOBS[job_id]["total_bytes_downloaded"] += len(chunk)

            part_path.replace(target_path)
            with JOBS_LOCK:
                JOBS[job_id]["files_completed"] += 1
        except Exception as exc:
            with JOBS_LOCK:
                JOBS[job_id]["status"] = "error"
                JOBS[job_id]["error"] = f"{rel_path}: {exc}"
                JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
            return

    with JOBS_LOCK:
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["current_file"] = f"Saved to {ds_dest}"
        JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()


def run_convert_worker(job_id: str, dataset_id: str, mode: str, dest_root: Path) -> None:
    """
    Background worker thread that crawls the target directory (either `<dest_root>/<dataset_id>/`,
    matching files directly in `<dest_root>/`, or all subdirectories of `<dest_root>/`),
    extracts any `.zip` archives into their respective subdirectories, and converts all
    `.h5`, `.hdf5`, and `.mat` files into Alcatel OptoDAS HDF5 format in their subdirectories.
    """
    importlib.reload(convert_to_optodas_h5)

    safe_root = verify_safe_destination(dest_root)
    ds_dir = safe_root if dataset_id in ("__all__", "", "*") else (safe_root / dataset_id)

    with JOBS_LOCK:
        JOBS[job_id]["status"] = f"converting ({mode})"
        JOBS[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()

    try:
        search_roots: List[Path] = []
        if ds_dir.exists():
            search_roots.append(ds_dir)

        # Also check if files for this dataset were downloaded directly into safe_root
        direct_files: List[Path] = []
        if dataset_id not in ("__all__", "", "*") and safe_root.exists():
            m = load_manifest_data(dataset_id)
            if m:
                for f_item in m.get("files", []):
                    rel = f_item.get("relative_path", "")
                    for cand in (safe_root / rel, safe_root / Path(rel).name):
                        if cand.exists() and cand.is_file():
                            direct_files.append(cand)
            if not search_roots and not direct_files:
                # Fall back to scanning safe_root so Convert Data works on any files in Target Directory
                search_roots.append(safe_root)

        # 1. Extract any .zip archives into their respective subdirectories if needed
        zip_candidates: List[Path] = []
        for sroot in search_roots:
            zip_candidates.extend(p for p in sroot.rglob("*.zip") if p.is_file())
        for df in direct_files:
            if df.suffix.lower() == ".zip" and df not in zip_candidates:
                zip_candidates.append(df)

        for zpath in zip_candidates:
            extract_dir = ds_dir if (zpath.parent == safe_root and dataset_id not in ("__all__", "", "*")) else zpath.parent
            extract_dir.mkdir(parents=True, exist_ok=True)
            existing_extracted = [
                p for p in convert_to_optodas_h5.discover_files(extract_dir, "*")
                if p.suffix.lower() in (".h5", ".hdf5", ".mat")
            ]
            if existing_extracted:
                continue

            with JOBS_LOCK:
                if JOBS[job_id].get("cancel_requested"):
                    JOBS[job_id]["status"] = "cancelled"
                    return
                JOBS[job_id]["current_file"] = f"Extracting {zpath.name} -> {extract_dir.name}/"
            with zipfile.ZipFile(zpath, "r") as zf:
                members = [
                    m for m in zf.infolist()
                    if not m.is_dir() and Path(m.filename).suffix.lower() in (".h5", ".hdf5", ".mat", ".txt")
                ]
                with JOBS_LOCK:
                    JOBS[job_id]["files_total"] = max(1, len(members))
                for idx, m in enumerate(members, start=1):
                    with JOBS_LOCK:
                        if JOBS[job_id].get("cancel_requested"):
                            JOBS[job_id]["status"] = "cancelled"
                            return
                        JOBS[job_id]["current_file"] = f"Unzipping {m.filename}"
                        JOBS[job_id]["current_file_bytes"] = idx
                        JOBS[job_id]["current_file_total"] = len(members)
                    zf.extract(m, path=extract_dir)
            if extract_dir not in search_roots:
                search_roots.append(extract_dir)

        # 2. Collect all .h5, .hdf5, and .mat files to convert
        targets: List[Path] = []
        seen = set()
        for sroot in search_roots:
            for p in convert_to_optodas_h5.discover_files(sroot, "*"):
                rp = p.resolve()
                if rp not in seen:
                    seen.add(rp)
                    targets.append(p)
        for df in direct_files:
            if df.suffix.lower() in (".h5", ".hdf5", ".mat"):
                rp = df.resolve()
                if rp not in seen:
                    seen.add(rp)
                    targets.append(df)

        if not targets:
            with JOBS_LOCK:
                JOBS[job_id]["status"] = "error"
                JOBS[job_id]["error"] = (
                    f"No .h5, .hdf5, .mat, or .zip files found in {ds_dir} (or {safe_root}). "
                    f"Click Download first or set Target directory to where your files are located."
                )
                JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
            return

        with JOBS_LOCK:
            JOBS[job_id]["files_total"] = len(targets)
            JOBS[job_id]["files_completed"] = 0

        for idx, fpath in enumerate(targets, start=1):
            with JOBS_LOCK:
                if JOBS[job_id].get("cancel_requested"):
                    JOBS[job_id]["status"] = "cancelled"
                    JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
                    return
                try:
                    rel_name = str(fpath.relative_to(safe_root))
                except ValueError:
                    rel_name = fpath.name
                JOBS[job_id]["current_file_index"] = idx
                JOBS[job_id]["current_file"] = rel_name
                JOBS[job_id]["current_file_bytes"] = idx - 1
                JOBS[job_id]["current_file_total"] = len(targets)

            fmt = convert_to_optodas_h5.detect_file_format(fpath)
            # Place converted output in the dataset's subdirectory if the source file was flat in safe_root
            if fpath.parent == safe_root and dataset_id not in ("__all__", "", "*"):
                out_dir = safe_root / dataset_id
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / f"{fpath.stem}_optodas.hdf5"
            else:
                out_path = fpath.with_name(f"{fpath.stem}_optodas.hdf5")

            if fmt == "mat_v5":
                convert_to_optodas_h5.convert_mat_v5_to_optodas_h5(fpath, out_path)
                written_bytes = out_path.stat().st_size if out_path.exists() else 0
            else:
                action = convert_to_optodas_h5.convert_foreign_hdf5_to_optodas(fpath, out_path, mode=mode)
                if action in ("linked", "copied") and out_path.exists():
                    written_bytes = out_path.stat().st_size
                else:
                    written_bytes = fpath.stat().st_size

            with JOBS_LOCK:
                JOBS[job_id]["files_completed"] = idx
                JOBS[job_id]["current_file_bytes"] = idx
                JOBS[job_id]["total_bytes_downloaded"] += written_bytes

        with JOBS_LOCK:
            JOBS[job_id]["status"] = "completed"
            JOBS[job_id]["current_file"] = f"Converted {len(targets)} file(s) [{mode}]"
            JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
    except Exception as exc:
        with JOBS_LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = str(exc)
            JOBS[job_id]["finished_at"] = datetime.now(timezone.utc).isoformat()


class DASHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            if not UI_FILE.exists():
                self.send_error(404, "UI file not found")
                return
            content = UI_FILE.read_bytes()
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)
            return

        if path == "/api/catalog":
            custom_dir = (qs.get("target_dir", [""])[0] or "").strip()
            try:
                dest_root = get_dest_root(custom_dir if custom_dir else None)
            except SystemExit as exc:
                self._send_json({"error": str(exc)}, status=400)
                return

            datasets = load_catalog_data()
            enriched = []
            for d in datasets:
                ds_id = d["id"]
                m = load_manifest_data(ds_id)
                local_st = local_dataset_stats(ds_id, dest_root)
                enriched.append(
                    {
                        **d,
                        "manifest_files_count": len(m.get("files", [])) if m else 0,
                        "manifest_crawled_at": m.get("crawled_at") if m else None,
                        "local_files_count": local_st["file_count"],
                        "local_bytes": local_st["total_bytes"],
                        "optodas_count": local_st["optodas_count"],
                    }
                )
            self._send_json(
                {
                    "dest_root": str(dest_root),
                    "datasets": enriched,
                }
            )
            return

        if path.startswith("/api/manifest/"):
            dataset_id = path.split("/api/manifest/", 1)[1].strip("/")
            m = load_manifest_data(dataset_id)
            if not m:
                self._send_json({"error": f"No manifest for {dataset_id}"}, status=404)
                return
            files = m.get("files", [])
            match_expr = (qs.get("match", [""])[0] or "").strip()
            limit = int(qs.get("limit", ["100"])[0] or 100)
            if match_expr:
                try:
                    rx = re.compile(match_expr, re.IGNORECASE)
                    files = [f for f in files if rx.search(f.get("relative_path", "")) or rx.search(f.get("url", ""))]
                except re.error as exc:
                    self._send_json({"error": f"Invalid regex: {exc}"}, status=400)
                    return

            dest_root = get_dest_root()
            total_matched = len(files)
            sliced = []
            for f in files[:limit]:
                local_file = resolve_local_file(dataset_id, f["relative_path"], dest_root)
                is_downloaded = local_file is not None and local_file.exists()
                local_size = local_file.stat().st_size if is_downloaded else 0
                sliced.append(
                    {
                        **f,
                        "downloaded": is_downloaded,
                        "local_bytes": local_size,
                    }
                )
            self._send_json(
                {
                    "dataset_id": dataset_id,
                    "total_indexed": len(m.get("files", [])),
                    "total_matched": total_matched,
                    "files": sliced,
                }
            )
            return

        if path == "/api/jobs":
            with JOBS_LOCK:
                job_list = sorted(JOBS.values(), key=lambda j: j.get("created_at", ""), reverse=True)
            self._send_json({"jobs": job_list[:30]})
            return

        self._send_json({"error": f"Endpoint not found: {path}"}, status=404)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/target-dir":
            body = self._read_json_body()
            target_dir = (body.get("target_dir") or "").strip()
            if not target_dir:
                self._send_json({"error": "target_dir is required"}, status=400)
                return
            try:
                resolved = get_dest_root(target_dir)
                ensure_local_gitignore(resolved)
                self._send_json({"dest_root": str(resolved)})
            except SystemExit as exc:
                self._send_json({"error": str(exc)}, status=400)
            return

        if path == "/api/download":
            body = self._read_json_body()
            dataset_id = body.get("dataset_id", "")
            rel_paths: Optional[List[str]] = body.get("relative_paths")
            match_expr = (body.get("match") or "").strip()
            limit = int(body.get("limit") or 5)
            target_dir = body.get("target_dir")

            try:
                dest_root = get_dest_root(target_dir)
            except SystemExit as exc:
                self._send_json({"error": str(exc)}, status=400)
                return

            m = load_manifest_data(dataset_id)
            if not m:
                self._send_json({"error": f"Manifest not found for {dataset_id}"}, status=404)
                return

            files = m.get("files", [])
            if rel_paths:
                rel_set = set(rel_paths)
                selected = [f for f in files if f.get("relative_path") in rel_set]
            else:
                if match_expr:
                    try:
                        rx = re.compile(match_expr, re.IGNORECASE)
                        files = [f for f in files if rx.search(f.get("relative_path", ""))]
                    except re.error as exc:
                        self._send_json({"error": f"Invalid regex: {exc}"}, status=400)
                        return
                selected = files[:limit] if limit > 0 else files

            if not selected:
                self._send_json({"error": "No matching files to download"}, status=400)
                return

            job_id = str(uuid.uuid4())[:8]
            job_record = {
                "job_id": job_id,
                "dataset_id": dataset_id,
                "job_type": "download",
                "status": "queued",
                "files_total": len(selected),
                "files_completed": 0,
                "current_file_index": 0,
                "current_file": f"{dataset_id}/{selected[0]['relative_path']}",
                "current_file_bytes": 0,
                "current_file_total": selected[0].get("size_bytes") or 0,
                "total_bytes_downloaded": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "cancel_requested": False,
                "error": None,
            }
            with JOBS_LOCK:
                JOBS[job_id] = job_record

            t = threading.Thread(
                target=run_download_worker,
                args=(job_id, dataset_id, selected, dest_root),
                daemon=True,
            )
            t.start()
            self._send_json({"job": job_record})
            return

        if path == "/api/convert":
            body = self._read_json_body()
            dataset_id = body.get("dataset_id", "__all__")
            mode = body.get("mode", "in-place")
            target_dir = body.get("target_dir")
            if mode not in ("in-place", "link", "copy"):
                self._send_json({"error": f"Invalid mode: {mode}"}, status=400)
                return

            try:
                dest_root = get_dest_root(target_dir)
            except SystemExit as exc:
                self._send_json({"error": str(exc)}, status=400)
                return

            job_id = str(uuid.uuid4())[:8]
            job_record = {
                "job_id": job_id,
                "dataset_id": dataset_id,
                "job_type": f"convert:{mode}",
                "status": "queued",
                "files_total": 1,
                "files_completed": 0,
                "current_file_index": 0,
                "current_file": f"Scanning {dest_root}/{dataset_id if dataset_id != '__all__' else ''}...",
                "current_file_bytes": 0,
                "current_file_total": 1,
                "total_bytes_downloaded": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "cancel_requested": False,
                "error": None,
            }
            with JOBS_LOCK:
                JOBS[job_id] = job_record

            t = threading.Thread(
                target=run_convert_worker,
                args=(job_id, dataset_id, mode, dest_root),
                daemon=True,
            )
            t.start()
            self._send_json({"job": job_record})
            return

        if path.startswith("/api/jobs/") and path.endswith("/cancel"):
            job_id = path.split("/api/jobs/", 1)[1].rsplit("/cancel", 1)[0]
            with JOBS_LOCK:
                if job_id not in JOBS:
                    self._send_json({"error": "Job not found"}, status=404)
                    return
                JOBS[job_id]["cancel_requested"] = True
                job_copy = dict(JOBS[job_id])
            self._send_json({"job": job_copy})
            return

        if path.startswith("/api/index/"):
            dataset_id = path.split("/api/index/", 1)[1].strip("/")
            datasets = load_catalog_data()
            matched = next((d for d in datasets if d.get("id") == dataset_id), None)
            if not matched:
                self._send_json({"error": f"Dataset {dataset_id} not in catalog"}, status=404)
                return
            try:
                manifest = build_manifest_for_dataset(matched, max_depth=2, max_dirs=15)
                self._send_json({"dataset_id": dataset_id, "files_found": manifest.get("files_found", 0)})
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json({"error": f"Endpoint not found: {path}"}, status=404)


def main() -> None:
    global ACTIVE_DEST_ROOT
    parser = argparse.ArgumentParser(description="Start the minimal DAS dataset download & conversion manager web UI.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port (default: 8765)")
    parser.add_argument(
        "--dest",
        default=str(REPO_ROOT / "downloads"),
        help="Default target download/conversion directory (default: downloads/)",
    )
    args = parser.parse_args()
    ACTIVE_DEST_ROOT = verify_safe_destination(Path(args.dest))

    server = ThreadingHTTPServer((args.host, args.port), DASHandler)
    print(f"DAS Download & Conversion Manager running at http://{args.host}:{args.port}")
    print(f"Target directory: {ACTIVE_DEST_ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
