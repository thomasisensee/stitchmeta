"""Public package interface for stitchmeta."""

from importlib import metadata

from stitchmeta.extractor import extract
from stitchmeta.models import ErrorPolicy, RunSummary, SectionResult, TileMetadata
from stitchmeta.readers.registry import get_reader, list_readers, register_reader

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = "0+unknown"
del metadata

__all__ = [
    "ErrorPolicy",
    "RunSummary",
    "SectionResult",
    "TileMetadata",
    "extract",
    "get_reader",
    "list_readers",
    "register_reader",
]
