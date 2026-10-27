#!/usr/bin/env python3
"""
convert_to_optodas_h5.py — Directory-globbing converter & zero-copy header injector
to make foreign DAS datasets readable as Alcatel Submarine Networks (ASN) OptoDAS HDF5.

Performance Modes (`--mode`):
  1. `in-place` (Fastest for .h5/.hdf5 — ~1 ms/file, 0 extra disk space):
     Opens existing foreign HDF5 files in `r+` mode, writes Alcatel `/header`,
     `/cableSpec`, and `/demodSpec` groups, and creates an internal HDF5 hard link
     `/data -> /DAS` (no waveform bytes are copied).
  2. `link` (Zero-copy sidecar for .h5/.hdf5 — ~2 ms/file, ~8 KB/file):
     Writes a lightweight `*_optodas.hdf5` file containing full Alcatel headers
     while `/data` is an `h5py.ExternalLink` pointing to the source HDF5 dataset.
  3. `copy` (Standalone file copy — required for .mat v5 or when transposing axes):
     Streams `/data` in chunks into a new standalone `.hdf5` file, preserving native
     compact dtype (e.g. `int16` for Muroto) when `dataScale` is applied.
"""

from __future__ import annotations

import argparse
import math
import os
import re
import struct
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore

# MAT-file Level 5 data types
MI_INT8 = 1
MI_UINT8 = 2
MI_INT16 = 3
MI_UINT16 = 4
MI_INT32 = 5
MI_UINT32 = 6
MI_SINGLE = 7
MI_DOUBLE = 9
MI_INT64 = 12
MI_UINT64 = 13
MI_MATRIX = 14
MI_UTF8 = 16
MI_UTF16 = 17
MI_UTF32 = 18

# MATLAB Array classes (mxClassID)
MX_CELL_CLASS = 1
MX_STRUCT_CLASS = 2
MX_CHAR_CLASS = 4
MX_DOUBLE_CLASS = 6
MX_SINGLE_CLASS = 7

MI_TO_DTYPE = {
    MI_INT8: "<i1",
    MI_UINT8: "<u1",
    MI_INT16: "<i2",
    MI_UINT16: "<u2",
    MI_INT32: "<i4",
    MI_UINT32: "<u4",
    MI_SINGLE: "<f4",
    MI_DOUBLE: "<f8",
    MI_INT64: "<i8",
    MI_UINT64: "<u8",
}

MUROTO_TS_RE = re.compile(
    r"(?P<yr>\d{4})-(?P<mo>\d{2})-(?P<da>\d{2})[_T](?P<hr>\d{2})[.:](?P<mi>\d{2})[.:](?P<se>\d{2})(?:\.(?P<us>\d+))?"
)
COMPACT_TS_RE = re.compile(
    r"(?P<yr>20\d{2})(?P<mo>\d{2})(?P<da>\d{2})[_T ]?(?P<hr>\d{2}):?(?P<mi>\d{2}):?(?P<se>\d{2})"
)
CH_RANGE_RE = re.compile(r"ch(?P<c0>\d+)_to_ch(?P<c1>\d+)", re.IGNORECASE)


def detect_file_format(path: Path) -> str:
    with path.open("rb") as f:
        head = f.read(528)
    if head.startswith(b"\x89HDF\r\n\x1a\n"):
        return "hdf5"
    if len(head) >= 520 and head[512:520] == b"\x89HDF\r\n\x1a\n":
        return "hdf5_mat73"
    if head.startswith(b"MATLAB 5.0"):
        return "mat_v5"
    if head.startswith(b"\x93NUMPY"):
        return "npy"
    raise RuntimeError(
        f"Unrecognized file signature in '{path.name}' (first 16 bytes: {head[:16]!r})."
    )


def parse_timestamp_epoch(text: str) -> Optional[float]:
    m = MUROTO_TS_RE.search(text)
    if m:
        us = int((m.group("us") or "0").ljust(6, "0")[:6])
        dt = datetime(
            int(m.group("yr")),
            int(m.group("mo")),
            int(m.group("da")),
            int(m.group("hr")),
            int(m.group("mi")),
            int(m.group("se")),
            us,
            tzinfo=timezone.utc,
        )
        return dt.timestamp()
    m2 = COMPACT_TS_RE.search(text)
    if m2:
        try:
            dt = datetime(
                int(m2.group("yr")),
                int(m2.group("mo")),
                int(m2.group("da")),
                int(m2.group("hr")),
                int(m2.group("mi")),
                int(m2.group("se")),
                tzinfo=timezone.utc,
            )
            return dt.timestamp()
        except ValueError:
            return None
    return None


def read_tag(buf: memoryview, offset: int) -> Tuple[int, int, int, int]:
    w0, w1 = struct.unpack_from("<II", buf, offset)
    if (w0 >> 16) != 0:
        dtype = w0 & 0xFFFF
        nbytes = w0 >> 16
        return dtype, nbytes, offset + 4, offset + 8
    else:
        dtype = w0
        nbytes = w1
        padded = (nbytes + 7) & ~7
        return dtype, nbytes, offset + 8, offset + 8 + padded


def parse_mi_matrix(buf: memoryview, elem_start: int, elem_nbytes: int) -> Tuple[str, Any]:
    end_off = elem_start + elem_nbytes
    _, _, af_start, pos = read_tag(buf, elem_start)
    flags0, _ = struct.unpack_from("<II", buf, af_start)
    mx_class = flags0 & 0xFF

    _, dim_bytes, dim_start, pos = read_tag(buf, pos)
    ndims = dim_bytes // 4
    dims = struct.unpack_from(f"<{ndims}i", buf, dim_start)

    _, name_bytes, name_start, pos = read_tag(buf, pos)
    name = bytes(buf[name_start : name_start + name_bytes]).split(b"\x00", 1)[0].decode("utf-8", errors="replace")

    if mx_class == MX_STRUCT_CLASS:
        _, _, fnl_start, pos = read_tag(buf, pos)
        max_fn_len = struct.unpack_from("<i", buf, fnl_start)[0]
        _, fns_bytes, fns_start, pos = read_tag(buf, pos)
        raw_fns = bytes(buf[fns_start : fns_start + fns_bytes])
        field_names = [
            raw_fns[i : i + max_fn_len].split(b"\x00", 1)[0].decode("utf-8", errors="replace")
            for i in range(0, fns_bytes, max_fn_len)
        ]
        n_elems = math.prod(dims) if dims else 1
        if n_elems == 1:
            struct_dict: Dict[str, Any] = {}
            for fn in field_names:
                if pos >= end_off:
                    break
                f_dtype, f_nbytes, f_start, pos = read_tag(buf, pos)
                if f_dtype == MI_MATRIX:
                    _, val = parse_mi_matrix(buf, f_start, f_nbytes)
                    struct_dict[fn] = val
            return name, struct_dict
        else:
            items: List[Dict[str, Any]] = []
            for _ in range(n_elems):
                item_dict: Dict[str, Any] = {}
                for fn in field_names:
                    if pos >= end_off:
                        break
                    f_dtype, f_nbytes, f_start, pos = read_tag(buf, pos)
                    if f_dtype == MI_MATRIX:
                        _, val = parse_mi_matrix(buf, f_start, f_nbytes)
                        item_dict[fn] = val
                items.append(item_dict)
            return name, items

    if mx_class == MX_CELL_CLASS:
        n_elems = math.prod(dims) if dims else 0
        cells = []
        for _ in range(n_elems):
            if pos >= end_off:
                break
            c_dtype, c_nbytes, c_start, pos = read_tag(buf, pos)
            if c_dtype == MI_MATRIX:
                _, val = parse_mi_matrix(buf, c_start, c_nbytes)
                cells.append(val)
        return name, cells

    if mx_class == MX_CHAR_CLASS:
        val_dtype, val_nbytes, val_start, _ = read_tag(buf, pos)
        raw = bytes(buf[val_start : val_start + val_nbytes])
        if val_dtype in (MI_UINT16, MI_INT16, MI_UTF16):
            chars = raw.decode("utf-16le", errors="replace")
        else:
            chars = raw.decode("utf-8", errors="replace")
        if len(dims) == 2 and dims[0] > 1 and len(chars) == dims[0] * dims[1]:
            rows = []
            nrows, ncols = dims[0], dims[1]
            for r in range(nrows):
                row_str = "".join(chars[r + c * nrows] for c in range(ncols)).rstrip("\x00 ")
                if row_str:
                    rows.append(row_str)
            text = "\n".join(rows)
        else:
            text = chars.rstrip("\x00 ")
        return name, text

    val_dtype, val_nbytes, val_start, _ = read_tag(buf, pos)
    np_dt = MI_TO_DTYPE.get(val_dtype)
    if np_dt is None or val_nbytes == 0:
        return name, ([] if np is None else np.array([], dtype=np.float64))

    if np is None:
        fmt_map = {
            MI_INT8: "b", MI_UINT8: "B", MI_INT16: "h", MI_UINT16: "H",
            MI_INT32: "i", MI_UINT32: "I", MI_SINGLE: "f", MI_DOUBLE: "d",
            MI_INT64: "q", MI_UINT64: "Q",
        }
        ch = fmt_map.get(val_dtype, "d")
        item_sz = struct.calcsize(f"<{ch}")
        count = val_nbytes // item_sz
        vals = struct.unpack_from(f"<{count}{ch}", buf, val_start)
        return name, (vals[0] if count == 1 else list(vals))

    arr = np.frombuffer(buf[val_start : val_start + val_nbytes], dtype=np_dt).copy()
    if arr.size == 1:
        return name, arr.reshape(())[()]
    if len(dims) == 2 and (dims[0] == 1 or dims[1] == 1):
        return name, arr.ravel()
    if len(dims) >= 2:
        try:
            arr = arr.reshape(dims, order="F")
        except ValueError:
            pass
    return name, arr


def inspect_and_load_mat_v5(path: Path) -> Tuple[Any, Tuple[int, int], Dict[str, Any]]:
    file_size = path.stat().st_size
    with path.open("rb") as f:
        pos = 128
        data_offset: Optional[int] = None
        data_dims: Optional[Tuple[int, int]] = None
        data_dtype: str = "<f8"
        variables: Dict[str, Any] = {}

        while pos + 8 <= file_size:
            f.seek(pos)
            tag_bytes = f.read(8)
            if len(tag_bytes) < 8:
                break
            dtype, nbytes = struct.unpack("<II", tag_bytes)
            if dtype != MI_MATRIX:
                break

            peek = memoryview(f.read(min(nbytes, 128)))
            _, _, _, p1 = read_tag(peek, 0)
            _, dim_b, dim_s, p2 = read_tag(peek, p1)
            dims = struct.unpack_from(f"<{dim_b // 4}i", peek, dim_s)
            _, name_b, name_s, p3 = read_tag(peek, p2)
            var_name = bytes(peek[name_s : name_s + name_b]).split(b"\x00", 1)[0].decode("utf-8", errors="replace")

            if var_name == "data" and nbytes > 10 * 1024 * 1024:
                val_dtype, _, val_s_rel, _ = read_tag(peek, p3)
                data_offset = pos + 8 + val_s_rel
                data_dims = (int(dims[0]), int(dims[1]))
                data_dtype = MI_TO_DTYPE.get(val_dtype, "<f8")
            else:
                f.seek(pos + 8)
                elem_bytes = memoryview(f.read(nbytes))
                parsed_name, parsed_val = parse_mi_matrix(elem_bytes, 0, nbytes)
                variables[parsed_name] = parsed_val

            pos += 8 + ((nbytes + 7) & ~7)

    if data_offset is None or data_dims is None:
        raise RuntimeError(f"Could not locate 2D 'data' matrix in {path}")

    mm = (
        np.memmap(path, dtype=data_dtype, mode="r", offset=data_offset, shape=data_dims, order="F")
        if np is not None
        else None
    )
    return mm, data_dims, variables


def write_h5_group_recursively(h5_group: Any, struct_dict: Dict[str, Any]) -> None:
    for key, val in struct_dict.items():
        if not key:
            continue
        if isinstance(val, dict):
            sub_grp = h5_group.require_group(key)
            write_h5_group_recursively(sub_grp, val)
        elif isinstance(val, list):
            if val and all(isinstance(x, str) for x in val):
                if key in h5_group:
                    del h5_group[key]
                h5_group.create_dataset(key, data=np.array(val, dtype="S"))
            elif val and all(isinstance(x, (int, float, np.number)) for x in val):
                if key in h5_group:
                    del h5_group[key]
                h5_group.create_dataset(key, data=np.asarray(val).ravel())
        elif isinstance(val, str):
            if key in h5_group:
                del h5_group[key]
            h5_group.create_dataset(key, data=np.bytes_(val))
        elif isinstance(val, (int, float, np.number, np.ndarray)):
            arr = np.asarray(val)
            if arr.dtype.kind in ("U", "O"):
                continue
            if arr.ndim == 2 and (arr.shape[0] == 1 or arr.shape[1] == 1):
                arr = arr.ravel()
            if key in h5_group:
                del h5_group[key]
            h5_group.create_dataset(key, data=arr)


def write_dimension_metadata(
    hdr: Any,
    n_samples: int,
    n_channels: int,
    dt: float,
    dx: float,
    ch_start: int = 0,
    ch_end: Optional[int] = None,
) -> None:
    """
    Writes exact Alcatel Submarine Networks (ASN) OptoDAS v8 dimension metadata
    expected by `simpleDAS` (`simpleDASreader.py` / `h5pydict.py`):
      - /header/dimensionNames = [b"time", b"distance"]
      - /header/dimensionUnits = [b"s", b"m"]
      - /header/dimensionSizes = [n_samples, n_channels]
      - /header/dimensionRanges/dimension0: {min: 0, max: n_samples - 1, size: n_samples, unitScale: dt}
      - /header/dimensionRanges/dimension1: {min: [ch_start], max: [ch_end], size: [n_channels], unitScale: dx}
    """
    if ch_end is None:
        ch_end = ch_start + max(0, n_channels - 1)

    for k, v in [
        ("dimensionNames", np.array([b"time", b"distance"], dtype="S")),
        ("dimensionUnits", np.array([b"s", b"m"], dtype="S")),
        ("dimensionSizes", np.array([n_samples, n_channels], dtype=np.int64)),
    ]:
        if k in hdr:
            del hdr[k]
        hdr.create_dataset(k, data=v)

    if "dimensionRanges" in hdr:
        del hdr["dimensionRanges"]
    dim_ranges = hdr.create_group("dimensionRanges")

    d0 = dim_ranges.create_group("dimension0")
    d0.create_dataset("min", data=np.int64(0))
    d0.create_dataset("max", data=np.int64(max(0, n_samples - 1)))
    d0.create_dataset("size", data=np.int64(n_samples))
    d0.create_dataset("unitScale", data=np.float64(dt))

    d1 = dim_ranges.create_group("dimension1")
    d1.create_dataset("min", data=np.array([int(ch_start)], dtype=np.int64))
    d1.create_dataset("max", data=np.array([int(ch_end)], dtype=np.int64))
    d1.create_dataset("size", data=np.array([int(n_channels)], dtype=np.int64))
    d1.create_dataset("unitScale", data=np.float64(dx))


def write_mat_v5_headers_to_h5(
    h5f: Any,
    in_path: Path,
    n_samples: int,
    n_channels: int,
    meta_vars: Dict[str, Any],
) -> None:
    """
    Populates OptoDAS v8 groups (/fileVersion, /header, /acqSpec, /demodSpec,
    /cableSpec, /monitoring, /timing) from the parsed MATLAB v5 metadata variables
    (`info_DAS_meta_raw`, `info_*`, `x1_*`) in strict compliance with `ASN-Norway/simpleDAS`.
    """
    raw_alcatel = meta_vars.get("info_DAS_meta_raw")
    if isinstance(raw_alcatel, dict):
        write_h5_group_recursively(h5f, raw_alcatel)

    if "fileVersion" in h5f:
        del h5f["fileVersion"]
    h5f.create_dataset("fileVersion", data=np.int32(8))

    hdr = h5f.require_group("header")
    raw_hdr = raw_alcatel.get("header", {}) if isinstance(raw_alcatel, dict) else {}
    raw_demod = raw_alcatel.get("demodSpec", {}) if isinstance(raw_alcatel, dict) else {}

    dt = float(np.asarray(meta_vars.get("info_sample_interval_s", raw_hdr.get("dt", 1.0 / 645.16129))).ravel()[0])
    gl = float(np.asarray(meta_vars.get("info_GL_m", 8.170401526197452)).ravel()[0])

    # Determine ROI decimation and channel indices
    if "x1_relative_channel" in meta_vars:
        ch_arr = np.asarray(meta_vars["x1_relative_channel"], dtype=np.int32).ravel()
    elif "x1_absolute_channel" in meta_vars:
        ch_arr = np.asarray(meta_vars["x1_absolute_channel"], dtype=np.int32).ravel()
    else:
        ch_arr = np.arange(n_channels, dtype=np.int32)

    if "x1_absolute_channel" in meta_vars:
        abs_ch = np.asarray(meta_vars["x1_absolute_channel"], dtype=np.int32).ravel()
        roi_start = int(abs_ch[0]) if abs_ch.size > 0 else 0
        roi_end = int(abs_ch[-1]) if abs_ch.size > 0 else n_channels - 1
        roi_dec = int(abs_ch[1] - abs_ch[0]) if abs_ch.size > 1 else int(raw_demod.get("roiDec", 1))
    else:
        roi_start = int(ch_arr[0]) if ch_arr.size > 0 else 0
        roi_end = int(ch_arr[-1]) if ch_arr.size > 0 else n_channels - 1
        roi_dec = int(ch_arr[1] - ch_arr[0]) if ch_arr.size > 1 else int(raw_demod.get("roiDec", 1))

    # Compute true inter-channel spacing dx in the decimated matrix:
    # Note: in Svalbard .mat files, `info_SSI_m` (1.0213 m) is the un-decimated optical spacing before roiDec=4,
    # whereas `x1_position_m` gives the actual channel positions spaced by `dx = 4.0852 m`.
    dx = 0.0
    if "x1_position_m" in meta_vars:
        pos_arr = np.asarray(meta_vars["x1_position_m"], dtype=np.float64).ravel()
        if pos_arr.size > 1:
            dx = float(abs(pos_arr[1] - pos_arr[0]))
    if dx <= 0.0:
        ssi = float(np.asarray(meta_vars.get("info_SSI_m", 4.0852)).ravel()[0])
        dx = ssi * roi_dec if (roi_dec > 1 and abs(gl / ssi - 8.0) < 0.5) else ssi

    # Timestamp t0 (prefer high-precision epoch in info_DAS_meta_raw.header.time)
    t0 = 0.0
    if isinstance(raw_hdr, dict) and "time" in raw_hdr:
        try:
            t0 = float(np.asarray(raw_hdr["time"]).ravel()[0])
        except Exception:
            t0 = 0.0
    if t0 == 0.0 and "info_timestamp" in meta_vars and isinstance(meta_vars["info_timestamp"], str):
        t0 = parse_timestamp_epoch(meta_vars["info_timestamp"]) or 0.0
    if t0 == 0.0:
        t0 = parse_timestamp_epoch(in_path.name) or 0.0

    exp_str = "Svalbard"
    if isinstance(raw_hdr, dict) and ("experiment" in raw_hdr or "exp" in raw_hdr):
        exp_str = str(raw_hdr.get("experiment") or raw_hdr.get("exp"))
    elif "whale" in in_path.name.lower():
        exp_str = "Svalbard"
    else:
        exp_str = in_path.stem

    # Determine physical units & scaling (Svalbard .mat is in nanostrain = 1e-9 strain, already time-integrated)
    units_info = str(meta_vars.get("info_units", "")).lower()
    data_scale = 1e-9 if ("1e-9" in units_info or "nanostrain" in units_info) else 1.0

    # Remove legacy v4 singular sensitivity keys so simpleDASreader doesn't overwrite 2D sensitivities
    for legacy_k in ("sensitivity", "sensitivityUnit"):
        if legacy_k in hdr:
            del hdr[legacy_k]

    for k, v in [
        ("dt", np.float64(dt)),
        ("dx", np.float64(dx)),
        ("gaugeLength", np.float64(gl)),
        ("time", np.float64(t0)),
        ("experiment", np.bytes_(exp_str)),
        ("exp", np.bytes_(exp_str)),
        ("name", np.bytes_("Strain")),
        ("dataType", np.int32(2)),  # 2 = integrated strain data (prevents double integration in simpleDASreader)
        ("dataScale", np.float32(data_scale)),
        ("unit", np.bytes_("strain")),
        ("sensitivities", np.ones((1, 1), dtype=np.float32)),  # Must be 2D (1, 1) for simpleDASreader[:, 0]
        ("sensitivityUnits", np.array([b""], dtype="S")),      # Empty denominator so unit_out = "strain" / "" = "strain"
        ("spatialUnwrRange", np.float32(0.0)),
        ("channels", ch_arr),
        ("sensorType", np.array([b"D"], dtype="S")),
    ]:
        if k in hdr:
            del hdr[k]
        hdr.create_dataset(k, data=v)

    ch_start = int(ch_arr[0]) if ch_arr.size > 0 else 0
    ch_end = int(ch_arr[-1]) if ch_arr.size > 0 else max(0, n_channels - 1)
    write_dimension_metadata(hdr, n_samples, n_channels, dt, dx, ch_start=ch_start, ch_end=ch_end)

    # Ensure /acqSpec and /demodSpec match the cropped matrix dimensions
    acq = h5f.require_group("acqSpec")
    for ak, av in [
        ("nSamples", np.int32(n_samples)),
        ("nChannels", np.int32(n_channels)),
    ]:
        if ak in acq:
            del acq[ak]
        acq.create_dataset(ak, data=av)

    demod = h5f.require_group("demodSpec")
    for dk, dv in [
        ("roiStart", np.int32(roi_start)),
        ("roiEnd", np.int32(roi_end)),
        ("roiDec", np.int32(roi_dec)),
    ]:
        if dk in demod:
            del demod[dk]
        demod.create_dataset(dk, data=dv)

    # Populate /cableSpec with standard ASN OptoDAS v8 keys + bathymetry/distances from .mat
    cable = h5f.require_group("cableSpec")
    for ck, cv in [
        ("fiberOverLength", np.float64(1.0)),
        ("refractiveIndex", np.float64(1.4677)),
        ("zeta", np.float64(0.78)),
    ]:
        if ck not in cable:
            cable.create_dataset(ck, data=cv)

    for src_k, dst_k in [
        ("x1_position_m", "sensorDistances"),
        ("x1_recwdepthz_m", "sensorDepths"),
        ("x1_distance_from_shore_m", "distanceFromShore"),
    ]:
        if src_k in meta_vars:
            if dst_k in cable:
                del cable[dst_k]
            cable.create_dataset(dst_k, data=np.asarray(meta_vars[src_k], dtype=np.float64).ravel())

    # Ensure /timing and /monitoring/Gps + /monitoring/Laser/itu exist for simpleDASreader.get_filemeta()
    timing = h5f.require_group("timing")
    if "SyncSource" not in timing:
        timing.create_dataset("SyncSource", data=np.bytes_("GPS"))
    if "ppses" not in timing:
        timing.create_dataset("ppses", data=np.array([int(t0)], dtype=np.int64))

    mon = h5f.require_group("monitoring")
    if "Gps" not in mon:
        gps = mon.create_group("Gps")
        gps.create_dataset("status", data=np.int32(1))
    if "Laser" not in mon:
        laser_v8 = mon.create_group("Laser")
        itu_val = 41
        if "laser" in mon and "itu" in mon["laser"]:
            try:
                itu_val = int(np.asarray(mon["laser"]["itu"][()]).ravel()[0])
            except Exception:
                itu_val = 41
        laser_v8.create_dataset("itu", data=np.int32(itu_val))


def convert_mat_v5_to_optodas_h5(in_path: Path, out_path: Path, chunk_samples: int = 10000) -> str:
    try:
        import h5py
    except ImportError:
        sys.exit("Error: Install h5py and numpy (`pip install h5py numpy`) to write OptoDAS HDF5 files.")

    mm, (dim0, dim1), meta_vars = inspect_and_load_mat_v5(in_path)

    ntraces = int(np.asarray(meta_vars.get("info_ntraces", dim0)).ravel()[0])
    nsamples = int(np.asarray(meta_vars.get("info_nsamples", dim1)).ravel()[0])
    transpose_needed = (dim0 == ntraces and dim1 == nsamples)
    n_samples, n_channels = (dim1, dim0) if transpose_needed else (dim0, dim1)

    # Fast path (~2 ms): if out_path already exists with the exact /data shape, update headers in-place
    # directly from the source .mat metadata without re-copying the 2.4 GB /data matrix!
    if out_path.exists():
        try:
            with h5py.File(out_path, "r+") as existing_h5:
                if "/data" in existing_h5 and tuple(existing_h5["/data"].shape) == (n_samples, n_channels):
                    write_mat_v5_headers_to_h5(existing_h5, in_path, n_samples, n_channels, meta_vars)
                    return "updated_headers_from_mat"
        except Exception:
            pass

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(out_path, "w") as h5f:
        write_mat_v5_headers_to_h5(h5f, in_path, n_samples, n_channels, meta_vars)

        dset = h5f.create_dataset(
            "data",
            shape=(n_samples, n_channels),
            dtype="float32",
            chunks=(min(chunk_samples, n_samples), min(256, n_channels)),
        )
        for s0 in range(0, n_samples, chunk_samples):
            s1 = min(s0 + chunk_samples, n_samples)
            chunk = np.asarray(mm[:, s0:s1].T if transpose_needed else mm[s0:s1, :], dtype=np.float32)
            dset[s0:s1, :] = chunk
    return "converted_mat"


def inspect_foreign_hdf5(in_path: Path) -> Dict[str, Any]:
    try:
        import h5py
    except ImportError:
        sys.exit("Error: Install h5py (`pip install h5py numpy`) to inspect or convert HDF5 files.")

    summary: Dict[str, Any] = {
        "datasets": {},
        "attributes": {},
        "primary_2d_path": None,
        "primary_2d_shape": None,
        "primary_2d_dtype": None,
        "is_native_optodas": False,
        "needs_optodas_repair": False,
    }

    with h5py.File(in_path, "r") as f:
        for ak, av in f.attrs.items():
            summary["attributes"][f"/{ak}"] = av.tolist() if hasattr(av, "tolist") else av

        def visitor(name: str, obj: Any) -> None:
            full_name = f"/{name}"
            for ak, av in obj.attrs.items():
                summary["attributes"][f"{full_name}@{ak}"] = av.tolist() if hasattr(av, "tolist") else av
            if isinstance(obj, h5py.Dataset):
                summary["datasets"][full_name] = {"shape": obj.shape, "dtype": str(obj.dtype)}
                # Only consider genuine 2D waveform matrices (both dims > 16), never 1xN metadata vectors
                if len(obj.shape) == 2 and min(obj.shape) > 16 and full_name != "/data":
                    if summary["primary_2d_path"] is None or math.prod(obj.shape) > math.prod(summary["primary_2d_shape"]):
                        summary["primary_2d_path"] = full_name
                        summary["primary_2d_shape"] = obj.shape
                        summary["primary_2d_dtype"] = str(obj.dtype)

        f.visititems(visitor)

        if "/data" in summary["datasets"]:
            data_shape = tuple(summary["datasets"]["/data"]["shape"])
            if summary["primary_2d_path"] is None:
                summary["primary_2d_path"] = "/data"
                summary["primary_2d_shape"] = data_shape
                summary["primary_2d_dtype"] = summary["datasets"]["/data"]["dtype"]

            has_dim_names = "/header/dimensionNames" in summary["datasets"]
            has_dim_sizes = "/header/dimensionSizes" in summary["datasets"]
            has_exp = "/header/experiment" in summary["datasets"]
            has_sensor_type = "/header/sensorType" in summary["datasets"]
            has_bad_dim_name_key = "/header/dimensionRanges/dimension0/name" in summary["datasets"]
            sens_is_2d = (
                "/header/sensitivities" in summary["datasets"]
                and len(summary["datasets"]["/header/sensitivities"]["shape"]) == 2
            )
            dim1_min_is_1d = (
                "/header/dimensionRanges/dimension1/min" in summary["datasets"]
                and len(summary["datasets"]["/header/dimensionRanges/dimension1/min"]["shape"]) == 1
            )
            dim_sizes_match = False
            if has_dim_sizes:
                try:
                    ds_vals = tuple(int(x) for x in np.asarray(f["/header/dimensionSizes"][()]).ravel())
                    dim_sizes_match = (ds_vals == data_shape)
                except Exception:
                    dim_sizes_match = False

            if (
                "/header/dt" in summary["datasets"]
                and has_dim_names
                and dim_sizes_match
                and has_exp
                and has_sensor_type
                and sens_is_2d
                and dim1_min_is_1d
                and not has_bad_dim_name_key
            ):
                summary["is_native_optodas"] = True
            else:
                summary["needs_optodas_repair"] = True

    return summary


def repair_converted_optodas_hdf5(in_path: Path) -> str:
    """
    Repairs or upgrades an existing OptoDAS HDF5 file in-place in ~2 ms without touching `/data`.
    If a sibling `.mat` file exists next to `*_optodas.hdf5`, reads the exact MATLAB metadata
    variables directly from the `.mat` file tail (~2 ms) and writes compliant OptoDAS v8 headers.
    """
    import h5py

    # 1. Check if the source .mat file exists alongside this *_optodas.hdf5 file
    if in_path.stem.endswith("_optodas"):
        base_stem = in_path.stem[: -len("_optodas")]
        sibling_mat = in_path.with_name(f"{base_stem}.mat")
        if sibling_mat.exists():
            _, _, meta_vars = inspect_and_load_mat_v5(sibling_mat)
            with h5py.File(in_path, "r+") as h5f:
                n_samples, n_channels = h5f["/data"].shape
                write_mat_v5_headers_to_h5(h5f, sibling_mat, n_samples, n_channels, meta_vars)
            return "repaired_from_sibling_mat"

    with h5py.File(in_path, "r+") as h5f:
        if "/data" not in h5f:
            raise RuntimeError(f"Cannot repair {in_path}: no /data dataset found.")
        n_samples, n_channels = h5f["/data"].shape

        if "fileVersion" in h5f:
            del h5f["fileVersion"]
        h5f.create_dataset("fileVersion", data=np.int32(8))

        hdr = h5f.require_group("header")
        is_svalbard = ("/sweepSpec" in h5f) or ("whale" in in_path.name.lower())

        # Recover accurate dt, dx, gaugeLength, time, and channels
        dt = float(np.asarray(hdr["dt"][()]).ravel()[0]) if "dt" in hdr else 0.01
        dx = float(np.asarray(hdr["dx"][()]).ravel()[0]) if "dx" in hdr else 1.0
        gl = float(np.asarray(hdr["gaugeLength"][()]).ravel()[0]) if "gaugeLength" in hdr else 10.0
        t0 = float(np.asarray(hdr["time"][()]).ravel()[0]) if "time" in hdr else 0.0

        if "/cableSpec/sensorDistances" in h5f:
            sd = np.asarray(h5f["/cableSpec/sensorDistances"][()]).ravel()
            if sd.size > 1:
                dx = float(abs(sd[1] - sd[0]))
                if is_svalbard and (abs(gl - 10.0) < 1e-3 or abs(gl / dx - 2.0) > 0.5):
                    gl = 2.0 * dx

        if is_svalbard:
            if abs(dt - 0.01) < 1e-6:
                dt = 0.00155
            if t0 == 0.0:
                t0 = parse_timestamp_epoch(in_path.name) or 0.0

            ch_match = CH_RANGE_RE.search(in_path.name)
            if ch_match:
                c0, c1 = int(ch_match.group("c0")), int(ch_match.group("c1"))
                if (c1 - c0 + 1) == n_channels:
                    ch_arr = np.arange(c0, c1 + 1, dtype=np.int32)
                else:
                    ch_arr = np.arange(n_channels, dtype=np.int32)
            elif "channels" in hdr and np.asarray(hdr["channels"][()]).size == n_channels:
                ch_arr = np.asarray(hdr["channels"][()], dtype=np.int32).ravel()
            else:
                ch_arr = np.arange(n_channels, dtype=np.int32)

            for legacy_k in ("sensitivity", "sensitivityUnit"):
                if legacy_k in hdr:
                    del hdr[legacy_k]

            for k, v in [
                ("dt", np.float64(dt)),
                ("dx", np.float64(dx)),
                ("gaugeLength", np.float64(gl)),
                ("time", np.float64(t0)),
                ("experiment", np.bytes_("Svalbard")),
                ("exp", np.bytes_("Svalbard")),
                ("name", np.bytes_("Strain")),
                ("dataType", np.int32(2)),
                ("dataScale", np.float32(1e-9)),
                ("unit", np.bytes_("strain")),
                ("sensitivities", np.ones((1, 1), dtype=np.float32)),
                ("sensitivityUnits", np.array([b""], dtype="S")),
                ("spatialUnwrRange", np.float32(0.0)),
                ("channels", ch_arr),
                ("sensorType", np.array([b"D"], dtype="S")),
            ]:
                if k in hdr:
                    del hdr[k]
                hdr.create_dataset(k, data=v)

            if "/acqSpec" in h5f:
                acq = h5f["/acqSpec"]
                for ak, av in [("nSamples", np.int32(n_samples)), ("nChannels", np.int32(n_channels))]:
                    if ak in acq:
                        del acq[ak]
                    acq.create_dataset(ak, data=av)

            if "/demodSpec" in h5f:
                demod = h5f["/demodSpec"]
                roi_dec = int(np.asarray(demod["roiDec"][()]).ravel()[0]) if "roiDec" in demod else 4
                roi_start = int(ch_arr[0]) * roi_dec if ch_arr.size > 0 else 0
                roi_end = int(ch_arr[-1]) * roi_dec if ch_arr.size > 0 else (n_channels - 1) * roi_dec
                for dk, dv in [
                    ("roiStart", np.int32(roi_start)),
                    ("roiEnd", np.int32(roi_end)),
                    ("roiDec", np.int32(roi_dec)),
                ]:
                    if dk in demod:
                        del demod[dk]
                    demod.create_dataset(dk, data=dv)
        else:
            if "channels" in hdr and np.asarray(hdr["channels"][()]).size == n_channels:
                ch_arr = np.asarray(hdr["channels"][()], dtype=np.int32).ravel()
            else:
                ch_arr = np.arange(n_channels, dtype=np.int32)
            if "experiment" not in hdr:
                exp_val = hdr["exp"][()] if "exp" in hdr else np.bytes_(in_path.stem)
                hdr.create_dataset("experiment", data=exp_val)
            if "sensorType" not in hdr:
                hdr.create_dataset("sensorType", data=np.array([b"D"], dtype="S"))
            if "sensitivities" in hdr:
                s_val = np.asarray(hdr["sensitivities"][()], dtype=np.float32)
                if s_val.ndim < 2:
                    del hdr["sensitivities"]
                    hdr.create_dataset("sensitivities", data=np.atleast_2d(s_val))

        ch_start = int(ch_arr[0]) if ch_arr.size > 0 else 0
        ch_end = int(ch_arr[-1]) if ch_arr.size > 0 else max(0, n_channels - 1)
        write_dimension_metadata(hdr, n_samples, n_channels, dt, dx, ch_start=ch_start, ch_end=ch_end)

    return "repaired_in_place"


def write_alcatel_metadata_groups(
    dst_h5: Any,
    in_path: Path,
    dt: float,
    dx: float,
    gauge_length: float,
    start_epoch: float,
    data_scale: float,
    sensitivity: float,
    n_samples: int,
    n_channels: int,
    n_eff: float,
    zeta: float,
    wavelength_m: float,
    roi_dec: int,
) -> None:
    if "fileVersion" in dst_h5:
        del dst_h5["fileVersion"]
    dst_h5.create_dataset("fileVersion", data=np.int32(8))

    hdr = dst_h5.require_group("header")
    for legacy_k in ("sensitivity", "sensitivityUnit"):
        if legacy_k in hdr:
            del hdr[legacy_k]

    for k, v in [
        ("dt", np.float64(dt)),
        ("dx", np.float64(dx)),
        ("gaugeLength", np.float64(gauge_length)),
        ("time", np.float64(start_epoch)),
        ("dataScale", np.float32(data_scale)),
        ("sensitivities", np.array([[sensitivity]], dtype=np.float32)),  # 2D (1, 1) required by simpleDASreader
        ("sensitivityUnits", np.array([b"rad/m/strain"], dtype="S")),
        ("unit", np.bytes_("rad/m/s")),
        ("spatialUnwrRange", np.float32(8.0 * math.pi / dt / gauge_length if (dt > 0 and gauge_length > 0) else 2.0 * math.pi)),
        ("channels", np.arange(n_channels, dtype=np.int32)),
        ("sensorType", np.array([b"D"], dtype="S")),
        ("dataType", np.int32(3)),
        ("name", np.bytes_("Phase rate per distance")),
        ("experiment", np.bytes_(in_path.stem)),
        ("exp", np.bytes_(in_path.stem)),
    ]:
        if k in hdr:
            del hdr[k]
        hdr.create_dataset(k, data=v)

    write_dimension_metadata(hdr, n_samples, n_channels, dt, dx, ch_start=0, ch_end=max(0, n_channels - 1))

    cable = dst_h5.require_group("cableSpec")
    for k, v in [
        ("fiberOverLength", np.float64(1.0)),
        ("refractiveIndex", np.float64(n_eff)),
        ("fiberRefractiveIndex", np.float64(n_eff)),
        ("zeta", np.float64(zeta)),
        ("wavelength", np.float64(wavelength_m)),
        ("sensorDistances", np.arange(n_channels, dtype=np.float64) * dx),
    ]:
        if k in cable:
            del cable[k]
        cable.create_dataset(k, data=v)

    timing = dst_h5.require_group("timing")
    if "SyncSource" not in timing:
        timing.create_dataset("SyncSource", data=np.bytes_("GPS"))
    if "ppses" not in timing:
        timing.create_dataset("ppses", data=np.array([int(start_epoch)], dtype=np.int64))

    mon = dst_h5.require_group("monitoring")
    if "Gps" not in mon:
        gps = mon.create_group("Gps")
        gps.create_dataset("status", data=np.int32(1))
    if "Laser" not in mon:
        laser_v8 = mon.create_group("Laser")
        laser_v8.create_dataset("itu", data=np.int32(51))

    for cand_ch in [in_path.parent / "channelinfo.txt", in_path.parent.parent / "channelinfo.txt"]:
        if cand_ch.exists():
            ch_nums, lats, lons, deps = [], [], [], []
            for line in cand_ch.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    ch_nums.append(int(parts[0]))
                    lats.append(float(parts[1]))
                    lons.append(float(parts[2]))
                    deps.append(float(parts[3]))
            for k, arr in [
                ("calibratedChannels", np.array(ch_nums, dtype=np.int32)),
                ("calibratedLat", np.array(lats, dtype=np.float64)),
                ("calibratedLon", np.array(lons, dtype=np.float64)),
                ("calibratedDepth_m", np.array(deps, dtype=np.float64)),
            ]:
                if k in cable:
                    del cable[k]
                cable.create_dataset(k, data=arr)
            break

    demod = dst_h5.require_group("demodSpec")
    for k, v in [
        ("roiStart", np.int32(0)),
        ("roiEnd", np.int32(n_channels - 1)),
        ("roiDec", np.int32(roi_dec)),
    ]:
        if k in demod:
            del demod[k]
        demod.create_dataset(k, data=v)


def convert_foreign_hdf5_to_optodas(
    in_path: Path,
    out_path: Path,
    mode: str = "in-place",
    chunk_samples: int = 6000,
) -> str:
    import h5py

    info = inspect_foreign_hdf5(in_path)
    if info["is_native_optodas"]:
        return "skipped_already_optodas"

    # If this is an existing OptoDAS / converted MAT file that only needs its /header/dimensionSizes repaired
    if info.get("needs_optodas_repair") and info["primary_2d_path"] == "/data":
        return repair_converted_optodas_hdf5(in_path)

    src_2d_path = info["primary_2d_path"]
    if not src_2d_path:
        raise RuntimeError(f"No 2D waveform dataset found in {in_path}")

    attrs_flat = {k.lower(): v for k, v in info["attributes"].items()}

    def find_attr_or_dset(h5f_in: Any, candidates: List[str], default: float) -> float:
        for c in candidates:
            cl = c.lower()
            for ak, av in attrs_flat.items():
                if ak.endswith(f"@{cl}") or ak.endswith(f"/{cl}"):
                    try:
                        val = av[0] if isinstance(av, (list, tuple, np.ndarray)) else av
                        return float(val)
                    except Exception:
                        pass
            for dk in info["datasets"]:
                if dk.lower().endswith(f"/{cl}"):
                    try:
                        val = h5f_in[dk][()]
                        return float(np.asarray(val).ravel()[0])
                    except Exception:
                        pass
        return default

    with h5py.File(in_path, "r") as src_h5:
        src_dset = src_h5[src_2d_path]
        dim0, dim1 = src_dset.shape
        src_dtype = src_dset.dtype

        is_muroto_apsensing = ("/DAS" in info["datasets"]) or any(
            k.startswith(("/Metadata", "/DAQ", "/ProcessingServer"))
            for k in list(info["datasets"]) + list(info["attributes"])
        )

        gauge_length = find_attr_or_dset(
            src_h5, ["GaugeLength", "gauge_length", "MeasureLength"], 40.8 if is_muroto_apsensing else 10.0
        )
        dx = find_attr_or_dset(
            src_h5, ["SpatialSampling", "SpatialResolution", "dx", "channel_spacing"], 51.0 if is_muroto_apsensing else 1.0
        )
        dt = find_attr_or_dset(src_h5, ["dt", "SampleInterval", "time_step"], 0.01 if is_muroto_apsensing else 0.0)
        if dt <= 0:
            fs = find_attr_or_dset(src_h5, ["SamplingFrequency", "PulseRate", "fs", "sample_rate"], 100.0)
            dt = 1.0 / fs if fs > 0 else 0.01

        if is_muroto_apsensing and dim1 == 6000 and dim0 != 6000:
            transpose_needed = True
        else:
            transpose_needed = False

        n_samples, n_channels = (dim1, dim0) if transpose_needed else (dim0, dim1)

        start_epoch = parse_timestamp_epoch(in_path.name) or 0.0
        if start_epoch == 0.0:
            for av in info["attributes"].values():
                if isinstance(av, (str, bytes)):
                    s_val = av.decode("utf-8", errors="replace") if isinstance(av, bytes) else av
                    ts = parse_timestamp_epoch(s_val)
                    if ts:
                        start_epoch = ts
                        break

        n_eff = 1.4682
        zeta = 0.78
        wavelength_m = 1550e-9
        data_scale = (math.pi / 32768.0) if (is_muroto_apsensing and np.issubdtype(src_dtype, np.integer)) else 1.0
        sensitivity = (4.0 * math.pi * n_eff * zeta * gauge_length) / wavelength_m
        roi_dec = 10 if is_muroto_apsensing else 1

    # Mode 1: Zero-copy in-place injection (~1 ms/file, 0 extra disk space)
    if mode == "in-place" and not transpose_needed:
        with h5py.File(in_path, "r+") as h5f:
            if "/data" not in h5f and src_2d_path in h5f:
                h5f["/data"] = h5f[src_2d_path]  # Instant HDF5 hard link (0 bytes copied!)
            actual_samples, actual_channels = h5f["/data"].shape
            write_alcatel_metadata_groups(
                h5f, in_path, dt, dx, gauge_length, start_epoch,
                data_scale, sensitivity, actual_samples, actual_channels, n_eff, zeta, wavelength_m, roi_dec,
            )
        return "in-place"

    # Mode 2: Zero-copy sidecar link (~2 ms/file, ~8 KB output file)
    if mode == "link" and not transpose_needed:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rel_target = os.path.relpath(in_path, out_path.parent)
        with h5py.File(out_path, "w") as dst_h5:
            write_alcatel_metadata_groups(
                dst_h5, in_path, dt, dx, gauge_length, start_epoch,
                data_scale, sensitivity, dim0, dim1, n_eff, zeta, wavelength_m, roi_dec,
            )
            dst_h5["/data"] = h5py.ExternalLink(rel_target, src_2d_path)
        return "linked"

    # Mode 3: Standalone copy (preserves compact source dtype like int16 instead of bloating to float32)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(in_path, "r") as src_h5, h5py.File(out_path, "w") as dst_h5:
        src_dset = src_h5[src_2d_path]
        write_alcatel_metadata_groups(
            dst_h5, in_path, dt, dx, gauge_length, start_epoch,
            data_scale, sensitivity, n_samples, n_channels, n_eff, zeta, wavelength_m, roi_dec,
        )
        orig_grp = dst_h5.create_group("vendorOriginal")
        for ak, av in src_h5.attrs.items():
            orig_grp.attrs[ak] = av
        for top_key in src_h5.keys():
            if f"/{top_key}" != src_2d_path and top_key not in (
                "header", "cableSpec", "demodSpec", "fileVersion", "vendorOriginal", "data"
            ):
                src_h5.copy(top_key, orig_grp, name=top_key)

        dst_data = dst_h5.create_dataset(
            "data",
            shape=(n_samples, n_channels),
            dtype=src_dset.dtype,
            chunks=(min(chunk_samples, n_samples), min(256, n_channels)),
        )
        for s0 in range(0, n_samples, chunk_samples):
            s1 = min(s0 + chunk_samples, n_samples)
            block = src_dset[:, s0:s1].T if transpose_needed else src_dset[s0:s1, :]
            dst_data[s0:s1, :] = block
    return "copied"


def convert_npy_to_optodas_h5(in_path: Path, out_path: Path, chunk_samples: int = 2000) -> str:
    try:
        import h5py
    except ImportError:
        sys.exit("h5py is required to write OptoDAS HDF5 files (`pip install h5py numpy`).")
    if np is None:
        sys.exit("numpy is required to convert .npy files (`pip install numpy h5py`).")

    arr = np.load(str(in_path), mmap_mode="r")
    if arr.ndim != 2:
        raise RuntimeError(f"Expected 2D array in '{in_path.name}', found shape {arr.shape}")

    n_samples, n_channels = int(arr.shape[0]), int(arr.shape[1])
    # Parse sampling frequency or duration from filename if present (e.g., _1490_seconds_10_Hz.npy)
    dt = 0.01
    hz_m = re.search(r"_(\d+(?:\.\d+)?)_Hz", in_path.name, re.IGNORECASE)
    if hz_m:
        fs = float(hz_m.group(1))
        if fs > 0:
            dt = 1.0 / fs
    sec_m = re.search(r"_(\d+(?:\.\d+)?)_seconds", in_path.name, re.IGNORECASE)
    transpose_needed = False
    if sec_m and hz_m:
        expected_samples = int(round(float(sec_m.group(1)) * float(hz_m.group(1))))
        if abs(n_channels - expected_samples) < abs(n_samples - expected_samples):
            transpose_needed = True
            n_samples, n_channels = n_channels, n_samples

    dx = 4.0
    gauge_length = 10.0
    start_epoch = parse_timestamp_epoch(in_path.name) or 0.0
    n_eff = 1.4682
    zeta = 0.78
    wavelength_m = 1550e-9
    data_scale = 1.0
    sensitivity = (4.0 * math.pi * n_eff * zeta * gauge_length) / wavelength_m

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(out_path, "w") as dst_h5:
        write_alcatel_metadata_groups(
            dst_h5, in_path, dt, dx, gauge_length, start_epoch,
            data_scale, sensitivity, n_samples, n_channels, n_eff, zeta, wavelength_m, 1,
        )
        dst_data = dst_h5.create_dataset(
            "data",
            shape=(n_samples, n_channels),
            dtype=arr.dtype if arr.dtype.kind in ("f", "i", "u") else "<f4",
            chunks=(min(chunk_samples, n_samples), min(256, n_channels)),
        )
        for s0 in range(0, n_samples, chunk_samples):
            s1 = min(s0 + chunk_samples, n_samples)
            block = arr[:, s0:s1].T if transpose_needed else arr[s0:s1, :]
            dst_data[s0:s1, :] = block
    return "converted_npy"


def discover_files(root: Path, pattern: str) -> List[Path]:
    if root.is_file():
        return [root]
    matched = sorted(
        p for p in root.rglob(pattern)
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in (".h5", ".hdf5", ".mat", ".npy")
    )
    return matched


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl a directory (or single file) and convert foreign DAS files into Alcatel OptoDAS HDF5."
    )
    parser.add_argument("--input", "-i", required=True, help="Input file or root directory to crawl")
    parser.add_argument("--output", "-o", help="Output file or root directory (optional when using --mode in-place)")
    parser.add_argument(
        "--glob",
        default="*",
        help="Glob pattern when crawling a directory (default: '*' — matches .h5, .hdf5, .mat, .npy)",
    )
    parser.add_argument(
        "--mode",
        choices=["in-place", "link", "copy"],
        default="in-place",
        help=(
            "'in-place' (default for HDF5: instant ~1ms/file, adds Alcatel /header & hard-links /data -> /DAS with 0 extra disk space), "
            "'link' (writes 8KB *_optodas.hdf5 ExternalLink wrapper files), "
            "or 'copy' (writes full standalone *_optodas.hdf5 files; always used for .mat/.npy)"
        ),
    )
    parser.add_argument("--inspect", action="store_true", help="Inspect without modifying or writing files")
    args = parser.parse_args()

    in_root = Path(args.input).expanduser().resolve()
    if not in_root.exists():
        sys.exit(f"Input path not found: {in_root}")

    targets = discover_files(in_root, args.glob)
    if not targets:
        sys.exit(f"No .h5, .hdf5, .mat, or .npy files found under {in_root} matching '{args.glob}'.")

    print(f"Found {len(targets)} file(s) under {in_root} (mode={args.mode})")
    t0 = time.time()

    for idx, fpath in enumerate(targets, start=1):
        fmt = detect_file_format(fpath)
        if args.inspect:
            if fmt == "mat_v5":
                _, dims, meta_vars = inspect_and_load_mat_v5(fpath)
                print(f"[{idx}/{len(targets)}] MAT v5: {fpath.name} dims={dims} vars={list(meta_vars.keys())}")
            elif fmt == "npy":
                arr = np.load(str(fpath), mmap_mode="r")
                print(f"[{idx}/{len(targets)}] NPY: {fpath.name} shape={arr.shape} dtype={arr.dtype}")
            else:
                info = inspect_foreign_hdf5(fpath)
                print(
                    f"[{idx}/{len(targets)}] HDF5: {fpath.name} "
                    f"native_optodas={info['is_native_optodas']} repair={info['needs_optodas_repair']} "
                    f"2d={info['primary_2d_path']} shape={info['primary_2d_shape']}"
                )
            continue

        if in_root.is_file():
            out_path = Path(args.output).expanduser().resolve() if args.output else fpath.with_name(f"{fpath.stem}_optodas.hdf5")
        else:
            rel = fpath.relative_to(in_root)
            out_base = Path(args.output).expanduser().resolve() if args.output else in_root
            out_path = (out_base / rel).with_name(f"{fpath.stem}_optodas.hdf5")

        file_t0 = time.time()
        if fmt == "mat_v5":
            action = convert_mat_v5_to_optodas_h5(fpath, out_path)
            elapsed = time.time() - file_t0
            print(f"[{idx}/{len(targets)}] MAT ({action}) -> {out_path.name} ({elapsed:.3f}s)")
        elif fmt == "npy":
            convert_npy_to_optodas_h5(fpath, out_path)
            elapsed = time.time() - file_t0
            print(f"[{idx}/{len(targets)}] Converted NPY -> {out_path.name} ({elapsed:.2f}s)")
        else:
            action = convert_foreign_hdf5_to_optodas(fpath, out_path, mode=args.mode)
            elapsed = (time.time() - file_t0) * 1000.0
            print(f"[{idx}/{len(targets)}] HDF5 ({action}) -> {fpath.name} ({elapsed:.1f} ms)")

    total_elapsed = time.time() - t0
    print(f"Done ({len(targets)} file(s) processed in {total_elapsed:.2f}s).")


if __name__ == "__main__":
    main()
