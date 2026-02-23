"""Metadata extraction orchestration and FEABAS file generation."""

import math
from pathlib import Path
from typing import Iterable

from stitchmeta.models import (
    ErrorPolicy,
    FeabasSectionData,
    FeabasTilePlacement,
    RunSummary,
    SectionResult,
    TileMetadata,
)
from stitchmeta.readers.registry import get_reader


def _iround(value: float) -> int:
    """Round to nearest integer using Python's built-in rounding semantics."""
    return int(round(value))


def _discover_sections(input_root: Path) -> list[Path]:
    """Return immediate subdirectories sorted by name."""
    return sorted(path for path in input_root.iterdir() if path.is_dir())


def _discover_tiles(section_dir: Path, suffixes: Iterable[str]) -> list[Path]:
    """Return sorted tile file paths in one section."""
    suffix_set = {suffix.lower() for suffix in suffixes}
    return sorted(
        path
        for path in section_dir.iterdir()
        if path.is_file() and path.suffix.lower() in suffix_set
    )


def _validate_tile_geometry(reference: TileMetadata, tile: TileMetadata) -> None:
    """Validate metadata consistency required for FEABAS section headers."""
    if tile.width_px != reference.width_px or tile.height_px != reference.height_px:
        raise ValueError(
            "inconsistent tile size "
            f"({tile.width_px}x{tile.height_px} vs "
            f"{reference.width_px}x{reference.height_px})"
        )
    if not math.isclose(tile.fov_x_um, reference.fov_x_um, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(
            "inconsistent FOV "
            f"({tile.fov_x_um}x{tile.fov_y_um} vs "
            f"{reference.fov_x_um}x{reference.fov_y_um})"
        )
    if not math.isclose(tile.fov_y_um, reference.fov_y_um, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(
            "inconsistent FOV "
            f"({tile.fov_x_um}x{tile.fov_y_um} vs "
            f"{reference.fov_x_um}x{reference.fov_y_um})"
        )


def build_feabas_section_data(
    tiles: list[TileMetadata], *, section_dir: Path, invert_y: bool
) -> FeabasSectionData:
    """Build FEABAS section data from parsed tile metadata."""
    if not tiles:
        raise ValueError("cannot build FEABAS data from an empty tile list")

    reference = tiles[0]
    if reference.width_px <= 0 or reference.height_px <= 0:
        raise ValueError("tile dimensions must be positive")
    if reference.fov_x_um <= 0.0 or reference.fov_y_um <= 0.0:
        raise ValueError("FOV values must be positive")

    for tile in tiles[1:]:
        _validate_tile_geometry(reference, tile)

    px_per_um_x = reference.width_px / reference.fov_x_um
    px_per_um_y = reference.height_px / reference.fov_y_um
    transformed_y_um = [(-tile.y_um if invert_y else tile.y_um) for tile in tiles]
    min_x_um = min(tile.x_um for tile in tiles)
    min_y_um = min(transformed_y_um)

    placements: list[FeabasTilePlacement] = []
    for tile, y_um in zip(tiles, transformed_y_um):
        x_px = _iround((tile.x_um - min_x_um) * px_per_um_x)
        y_px = _iround((y_um - min_y_um) * px_per_um_y)
        placements.append(FeabasTilePlacement(name=tile.name, x_px=x_px, y_px=y_px))

    resolution_x_nm = reference.fov_x_um * 1000.0 / reference.width_px
    resolution_y_nm = reference.fov_y_um * 1000.0 / reference.height_px
    resolution_nm = (resolution_x_nm + resolution_y_nm) / 2.0

    return FeabasSectionData(
        root_dir=section_dir.resolve(),
        resolution_nm=resolution_nm,
        tile_height_px=reference.height_px,
        tile_width_px=reference.width_px,
        placements=tuple(placements),
    )


def write_feabas_file(output_path: Path, section_data: FeabasSectionData) -> None:
    """Serialize one section in FEABAS tab-separated text format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{{ROOT_DIR}}\t{section_data.root_dir}\n")
        handle.write(f"{{RESOLUTION}}\t{section_data.resolution_nm:.3f}\n")
        handle.write(
            f"{{TILE_SIZE}}\t{section_data.tile_height_px}\t{section_data.tile_width_px}\n"
        )
        for placement in section_data.placements:
            handle.write(f"{placement.name}\t{placement.x_px}\t{placement.y_px}\n")


def extract(
    input_root: Path | str,
    output_dir: Path | str,
    *,
    reader_name: str = "fibics_tiff",
    invert_y: bool = True,
    error_policy: ErrorPolicy = "partial",
) -> RunSummary:
    """Extract section tile layout and write FEABAS files.

    Parameters
    ----------
    input_root:
        Directory containing section subdirectories (`001`, `002`, ...).
    output_dir:
        Directory where one output file per section will be written.
    reader_name:
        Registered reader used to parse source images.
    invert_y:
        Whether to invert Y coordinates before normalization.
    error_policy:
        `partial`: skip invalid tiles and write remaining valid ones.
        `section`: skip entire section if any tile fails.
        `abort`: stop extraction on first tile failure.
    """
    input_root = Path(input_root)
    output_dir = Path(output_dir)
    if not input_root.is_dir():
        raise ValueError(f"input root is not a directory: {input_root}")
    if error_policy not in {"partial", "section", "abort"}:
        raise ValueError(f"unsupported error policy: {error_policy}")

    reader = get_reader(reader_name)
    summary = RunSummary()
    output_dir.mkdir(parents=True, exist_ok=True)

    for section_dir in _discover_sections(input_root):
        tile_paths = _discover_tiles(section_dir, reader.supported_suffixes())
        if not tile_paths:
            continue

        section_result = SectionResult(
            section_name=section_dir.name,
            section_dir=section_dir,
            output_path=None,
            files_seen=len(tile_paths),
            tiles_written=0,
            tiles_skipped=0,
        )
        parsed_tiles: list[TileMetadata] = []
        section_has_errors = False
        reference_tile: TileMetadata | None = None

        for tile_path in tile_paths:
            try:
                tile = reader.parse_tile(tile_path)
                if reference_tile is None:
                    reference_tile = tile
                else:
                    _validate_tile_geometry(reference_tile, tile)
                parsed_tiles.append(tile)
            except Exception as exc:  # noqa: BLE001
                section_result.tiles_skipped += 1
                section_result.errors.append(f"{tile_path.name}: {exc}")
                section_has_errors = True
                if error_policy == "abort":
                    summary.section_results.append(section_result)
                    summary.aborted = True
                    summary.abort_reason = f"{section_dir.name}/{tile_path.name}: {exc}"
                    return summary

        if not parsed_tiles:
            summary.section_results.append(section_result)
            continue

        if error_policy == "section" and section_has_errors:
            summary.section_results.append(section_result)
            continue

        section_data = build_feabas_section_data(
            parsed_tiles, section_dir=section_dir, invert_y=invert_y
        )
        output_path = output_dir / f"{section_dir.name}.txt"
        write_feabas_file(output_path, section_data)
        section_result.output_path = output_path
        section_result.tiles_written = len(parsed_tiles)
        summary.section_results.append(section_result)

    return summary
