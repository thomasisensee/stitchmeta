from pathlib import Path
from typing import Any

import numpy as np
import tifffile


def fibics_xml(
    *,
    fov_x_um: float,
    fov_y_um: float,
    x_um: float,
    y_um: float,
    include_mosaic: bool = True,
    include_stitching: bool = True,
    include_history: bool = True,
) -> str:
    """Build minimal Fibics XML payload for tests."""
    parts = [
        "<Fibics>",
        "<Scan>",
        f"<FOV_X>{fov_x_um}</FOV_X>",
        f"<FOV_Y>{fov_y_um}</FOV_Y>",
        "</Scan>",
    ]
    if include_mosaic:
        parts.extend(
            [
                "<MosaicInfo>",
                f"<X>{x_um}</X>",
                f"<Y>{y_um}</Y>",
                "</MosaicInfo>",
            ]
        )
    if include_stitching:
        parts.extend(
            [
                "<StitchingInfo>",
                f"<UpdatedStagePositionX>{x_um}</UpdatedStagePositionX>",
                f"<UpdatedStagePositionY>{y_um}</UpdatedStagePositionY>",
                "</StitchingInfo>",
            ]
        )
    if include_history:
        parts.extend(
            [
                "<TilePositionHistory>",
                "<TilePositionEntry>",
                f"<X>{x_um}</X>",
                f"<Y>{y_um}</Y>",
                "</TilePositionEntry>",
                "</TilePositionHistory>",
            ]
        )
    parts.append("</Fibics>")
    return "".join(parts)


def write_test_tiff(
    path: Path,
    *,
    width_px: int = 10,
    height_px: int = 10,
    xml: str | None,
) -> None:
    """Write a tiny TIFF file with an optional Fibics XML tag."""
    data = np.zeros((height_px, width_px), dtype=np.uint8)
    extra_tags: list[tuple[int, str, int, Any, bool]] = []
    if xml is not None:
        extra_tags.append((51023, "s", 0, xml, False))
    tifffile.imwrite(path, data, extratags=extra_tags)
