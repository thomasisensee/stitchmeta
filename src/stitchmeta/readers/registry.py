"""Reader registry for metadata extraction backends."""

from stitchmeta.readers.base import TileReader
from stitchmeta.readers.fibics_tiff import FibicsTiffReader

_READERS: dict[str, type[TileReader]] = {"fibics_tiff": FibicsTiffReader}


def register_reader(
    name: str, reader_class: type[TileReader], *, overwrite: bool = False
) -> None:
    """Register a reader class under a stable lookup name."""
    if not name:
        raise ValueError("reader name must not be empty")
    if name in _READERS and not overwrite:
        raise ValueError(f"reader {name!r} is already registered")
    _READERS[name] = reader_class


def get_reader(name: str) -> type[TileReader]:
    """Return a registered reader class by name."""
    try:
        return _READERS[name]
    except KeyError as exc:
        known = ", ".join(sorted(_READERS))
        raise ValueError(f"unknown reader {name!r}; known readers: {known}") from exc


def list_readers() -> tuple[str, ...]:
    """Return available reader names in sorted order."""
    return tuple(sorted(_READERS))
