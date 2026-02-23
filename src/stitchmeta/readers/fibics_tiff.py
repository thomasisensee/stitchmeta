"""Reader for Fibics Atlas TIFF files with XML metadata in tag 51023."""

from pathlib import Path
from xml.etree import ElementTree

import tifffile

from stitchmeta.models import TileMetadata
from stitchmeta.readers.base import TileReader, TileReaderError

_FIBICS_XML_TAG = 51023


def _get_tag_text(root: ElementTree.Element, paths: list[str]) -> str | None:
    """Return text from the first matching XML path."""
    for path in paths:
        element = root.find(path)
        if element is not None and element.text not in (None, ""):
            return element.text
    return None


def _parse_float_tag(root: ElementTree.Element, paths: list[str], label: str) -> float:
    """Parse a required float tag from one of several fallback XML paths."""
    value = _get_tag_text(root, paths)
    if value is None:
        raise TileReaderError(f"missing {label} in Fibics XML")
    try:
        return float(value)
    except ValueError as exc:
        raise TileReaderError(f"invalid {label} value: {value!r}") from exc


class FibicsTiffReader(TileReader):
    """Extract tile metadata from Fibics TIFF page-0 tags."""

    @classmethod
    def supported_suffixes(cls) -> tuple[str, ...]:
        return (".tif", ".tiff")

    @classmethod
    def parse_tile(cls, tile_path: Path) -> TileMetadata:
        """Read dimensions and Fibics mosaic metadata from one TIFF."""
        try:
            with tifffile.TiffFile(tile_path) as tif:
                page = tif.pages[0]
                width_px = int(page.imagewidth)
                height_px = int(page.imagelength)
                xml_data = page.tags[_FIBICS_XML_TAG].value
        except IndexError as exc:
            raise TileReaderError("no readable TIFF pages found") from exc
        except KeyError as exc:
            raise TileReaderError(f"missing Fibics XML tag {_FIBICS_XML_TAG}") from exc
        except tifffile.TiffFileError as exc:
            raise TileReaderError(f"invalid TIFF: {exc}") from exc

        xml_text: str
        if isinstance(xml_data, bytes):
            xml_text = xml_data.decode("iso-8859-1", errors="replace")
        else:
            xml_text = str(xml_data)
        xml_text = xml_text.rstrip("\x00").strip()

        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as exc:
            raise TileReaderError(
                f"invalid Fibics XML in tag {_FIBICS_XML_TAG}"
            ) from exc

        fov_x_um = _parse_float_tag(root, ["Scan/FOV_X"], "FOV_X")
        fov_y_um = _parse_float_tag(root, ["Scan/FOV_Y"], "FOV_Y")
        x_um = _parse_float_tag(
            root,
            [
                "MosaicInfo/X",
                "StitchingInfo/UpdatedStagePositionX",
                "TilePositionHistory/TilePositionEntry/X",
            ],
            "tile X position",
        )
        y_um = _parse_float_tag(
            root,
            [
                "MosaicInfo/Y",
                "StitchingInfo/UpdatedStagePositionY",
                "TilePositionHistory/TilePositionEntry/Y",
            ],
            "tile Y position",
        )

        return TileMetadata(
            name=tile_path.name,
            width_px=width_px,
            height_px=height_px,
            fov_x_um=fov_x_um,
            fov_y_um=fov_y_um,
            x_um=x_um,
            y_um=y_um,
        )
