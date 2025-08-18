"""A CLI tool to duplicate and sync file content with advanced transformations."""

from .__about__ import __version__
from ._file_processing import process_files
from .common_transforms import embed_environ

__all__ = [
    "__version__",
    "embed_environ",
    "process_files",
]
