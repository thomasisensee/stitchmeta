"""Reader interfaces and shared reader errors."""

from abc import ABC, abstractmethod
from pathlib import Path

from stitchmeta.models import TileMetadata


class TileReaderError(RuntimeError):
    """Raised when metadata parsing fails for a source tile."""


class TileReader(ABC):
    """Abstract interface for tile metadata readers."""

    @classmethod
    @abstractmethod
    def supported_suffixes(cls) -> tuple[str, ...]:
        """Return lowercase file suffixes handled by the reader."""

    @classmethod
    @abstractmethod
    def parse_tile(cls, tile_path: Path) -> TileMetadata:
        """Parse metadata from one tile image."""
