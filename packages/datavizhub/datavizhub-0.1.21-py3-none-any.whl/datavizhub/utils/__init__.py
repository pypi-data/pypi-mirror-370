"""Utilities used across DataVizHub (dates, files, images, credentials).

Avoid importing optional heavy dependencies at package import time to keep the
CLI lightweight when only a subset of functionality is needed (e.g., pipeline
runner). Submodules can still be imported directly when required.
"""

# image_manager depends on optional heavy deps (numpy/Pillow). Detect lazily.
import importlib.util as _ilu  # noqa: E402

from .credential_manager import CredentialManager
from .date_manager import DateManager
from .file_utils import FileUtils, remove_all_files_in_directory
from .json_file_manager import JSONFileManager

_HAS_IMAGE = _ilu.find_spec(__name__ + ".image_manager") is not None
if _HAS_IMAGE:  # pragma: no cover - optional path
    from .image_manager import (
        ImageManager as ImageManager,  # type: ignore  # noqa: F401
    )

__all__ = [
    "CredentialManager",
    "DateManager",
    "FileUtils",
    "remove_all_files_in_directory",
    "JSONFileManager",
]
if _HAS_IMAGE:
    __all__.append("ImageManager")
