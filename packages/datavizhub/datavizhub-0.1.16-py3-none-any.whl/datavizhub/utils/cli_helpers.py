from __future__ import annotations

import contextlib
import os
import tempfile
from typing import BinaryIO, Iterator, Optional, List

from .io_utils import open_input, open_output  # re-export


def read_all_bytes(path_or_dash: str) -> bytes:
    """Read all bytes from a path or '-' (stdin)."""
    with open_input(path_or_dash) as f:
        return f.read()


def is_netcdf_bytes(b: bytes) -> bool:
    """Return True if bytes look like NetCDF (classic CDF or HDF5-based).

    Recognizes magic headers:
    - Classic NetCDF: ``b"CDF"``
    - NetCDF4/HDF5:  ``b"\x89HDF"``
    """
    return b.startswith(b"CDF") or b.startswith(b"\x89HDF")


def is_grib2_bytes(b: bytes) -> bool:
    """Return True if bytes look like GRIB (``b"GRIB"``)."""
    return b.startswith(b"GRIB")


def detect_format_bytes(b: bytes) -> str:
    """Detect basic format from magic bytes.

    Returns one of: ``"netcdf"``, ``"grib2"``, or ``"unknown"``.
    """
    if is_netcdf_bytes(b):
        return "netcdf"
    if is_grib2_bytes(b):
        return "grib2"
    return "unknown"


@contextlib.contextmanager
def temp_file_from_bytes(data: bytes, *, suffix: str = "") -> Iterator[str]:
    """Write bytes to a NamedTemporaryFile and yield its path; delete on exit."""
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        tmp.write(data)
        tmp.flush()
        tmp.close()
        yield tmp.name
    finally:
        try:
            os.remove(tmp.name)
        except Exception:
            pass


def parse_levels_arg(val) -> int | List[float]:
    """Parse levels from int or comma-separated floats."""
    if isinstance(val, int):
        return val
    if isinstance(val, (list, tuple)):
        return [float(x) for x in val]
    s = str(val)
    try:
        return int(s)
    except ValueError:
        parts = [p.strip() for p in s.split(",") if p.strip()]
        return [float(p) for p in parts]


def configure_logging_from_env(default: str = "info") -> None:
    """Set logging levels based on DATAVIZHUB_VERBOSITY env.

    Values: debug|info|quiet. Defaults to 'info'.
    - debug: root=DEBUG
    - info: root=INFO
    - quiet: root=ERROR (suppress most logs)
    Also dials down noisy third-party loggers (matplotlib, cartopy, botocore, requests).
    """
    import logging
    import os

    level_map = {"debug": logging.DEBUG, "info": logging.INFO, "quiet": logging.ERROR}
    verb = os.environ.get("DATAVIZHUB_VERBOSITY", default).lower()
    level = level_map.get(verb, logging.INFO)

    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    for name in ("matplotlib", "cartopy", "botocore", "urllib3", "requests"):
        try:
            logging.getLogger(name).setLevel(max(level, logging.WARNING) if verb != "debug" else level)
        except Exception:
            pass
