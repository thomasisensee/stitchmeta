from pathlib import Path

import pytest

from stitchmeta.readers.base import TileReaderError
from stitchmeta.readers.fibics_tiff import FibicsTiffReader

from tests.conftest import fibics_xml, write_test_tiff


def test_fibics_reader_parses_mosaic_position(tmp_path: Path) -> None:
    tile_path = tmp_path / "tile.tif"
    write_test_tiff(
        tile_path,
        width_px=12,
        height_px=8,
        xml=fibics_xml(fov_x_um=24.0, fov_y_um=16.0, x_um=1.25, y_um=-2.5),
    )

    metadata = FibicsTiffReader.parse_tile(tile_path)

    assert metadata.name == "tile.tif"
    assert metadata.width_px == 12
    assert metadata.height_px == 8
    assert metadata.fov_x_um == 24.0
    assert metadata.fov_y_um == 16.0
    assert metadata.x_um == 1.25
    assert metadata.y_um == -2.5


def test_fibics_reader_fallback_to_stitching_info(tmp_path: Path) -> None:
    tile_path = tmp_path / "tile.tif"
    write_test_tiff(
        tile_path,
        xml=fibics_xml(
            fov_x_um=10.0,
            fov_y_um=10.0,
            x_um=3.0,
            y_um=4.0,
            include_mosaic=False,
            include_stitching=True,
            include_history=False,
        ),
    )

    metadata = FibicsTiffReader.parse_tile(tile_path)
    assert metadata.x_um == 3.0
    assert metadata.y_um == 4.0


def test_fibics_reader_raises_for_missing_xml_tag(tmp_path: Path) -> None:
    tile_path = tmp_path / "tile.tif"
    write_test_tiff(tile_path, xml=None)

    with pytest.raises(TileReaderError):
        FibicsTiffReader.parse_tile(tile_path)
