"""Typed domain models used by extraction and output formatting."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ErrorPolicy(str, Enum):
    """Tile-parse error handling mode.

    `partial`: skip invalid tiles and keep writing valid ones.
    `section`: skip the entire section if any tile fails.
    `abort`: stop extraction immediately on the first tile failure.
    """

    PARTIAL = "partial"
    SECTION = "section"
    ABORT = "abort"

    @classmethod
    def from_value(cls, value: "ErrorPolicy | str") -> "ErrorPolicy":
        """Normalize user input into a supported error policy enum."""
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise TypeError("error policy must be an ErrorPolicy or string value")
        try:
            return cls(value.lower())
        except ValueError as exc:
            raise ValueError(f"unsupported error policy: {value}") from exc


@dataclass(frozen=True, slots=True)
class TileMetadata:
    """Metadata extracted from one source tile image."""

    name: str
    width_px: int
    height_px: int
    fov_x_um: float
    fov_y_um: float
    x_um: float
    y_um: float


@dataclass(frozen=True, slots=True)
class FeabasTilePlacement:
    """One tile row in a FEABAS coordinate file."""

    name: str
    x_px: int
    y_px: int


@dataclass(frozen=True, slots=True)
class FeabasSectionData:
    """Serializable FEABAS output payload for one section."""

    root_dir: Path
    resolution_nm: float
    tile_height_px: int
    tile_width_px: int
    placements: tuple[FeabasTilePlacement, ...]


@dataclass(slots=True)
class SectionResult:
    """Per-section extraction result."""

    section_name: str
    section_dir: Path
    output_path: Path | None
    files_seen: int
    tiles_written: int
    tiles_skipped: int
    errors: list[str] = field(default_factory=list)

    @property
    def wrote_output(self) -> bool:
        """Whether a FEABAS file was written for this section."""
        return self.output_path is not None


@dataclass(slots=True)
class RunSummary:
    """Aggregate extraction result over all discovered sections."""

    section_results: list[SectionResult] = field(default_factory=list)
    aborted: bool = False
    abort_reason: str | None = None

    @property
    def sections_seen(self) -> int:
        """Number of sections that contained candidate tile files."""
        return len(self.section_results)

    @property
    def sections_written(self) -> int:
        """Number of sections for which FEABAS files were written."""
        return sum(1 for section in self.section_results if section.wrote_output)

    @property
    def tiles_written(self) -> int:
        """Total number of written tile rows across sections."""
        return sum(section.tiles_written for section in self.section_results)

    @property
    def tiles_skipped(self) -> int:
        """Total number of skipped tiles across sections."""
        return sum(section.tiles_skipped for section in self.section_results)

    @property
    def errors(self) -> list[str]:
        """Flattened list of section-scoped error messages."""
        messages: list[str] = []
        for section in self.section_results:
            for message in section.errors:
                messages.append(f"{section.section_name}/{message}")
        return messages
