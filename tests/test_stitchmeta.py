from pathlib import Path

from stitchmeta import ErrorPolicy, extract, list_readers

from tests.conftest import fibics_xml, write_test_tiff


def _write_good_section(section_dir: Path) -> None:
    tiles = [
        ("tile_r1_c1.tif", -5.0, 5.0),
        ("tile_r1_c2.tif", 5.0, 5.0),
        ("tile_r2_c1.tif", -5.0, -5.0),
        ("tile_r2_c2.tif", 5.0, -5.0),
    ]
    for filename, x_um, y_um in tiles:
        write_test_tiff(
            section_dir / filename,
            xml=fibics_xml(fov_x_um=10.0, fov_y_um=10.0, x_um=x_um, y_um=y_um),
        )


def test_default_reader_is_registered() -> None:
    assert "fibics_tiff" in list_readers()


def test_extract_writes_feabas_file(tmp_path: Path) -> None:
    input_root = tmp_path / "input"
    output_dir = tmp_path / "output"
    section_dir = input_root / "001"
    section_dir.mkdir(parents=True)
    _write_good_section(section_dir)

    summary = extract(input_root=input_root, output_dir=output_dir)

    assert summary.sections_seen == 1
    assert summary.sections_written == 1
    assert summary.tiles_written == 4
    assert summary.tiles_skipped == 0
    assert summary.aborted is False

    output_file = output_dir / "001.txt"
    assert output_file.exists()
    lines = output_file.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0] == f"{{ROOT_DIR}}\t{section_dir.resolve()}"
    assert lines[1] == "{RESOLUTION}\t1000.000"
    assert lines[2] == "{TILE_SIZE}\t10\t10"
    assert lines[3:] == [
        "tile_r1_c1.tif\t0\t0",
        "tile_r1_c2.tif\t10\t0",
        "tile_r2_c1.tif\t0\t10",
        "tile_r2_c2.tif\t10\t10",
    ]


def test_extract_partial_skips_invalid_tiles(tmp_path: Path) -> None:
    input_root = tmp_path / "input"
    output_dir = tmp_path / "output"
    section_dir = input_root / "001"
    section_dir.mkdir(parents=True)
    _write_good_section(section_dir)
    write_test_tiff(section_dir / "tile_bad.tif", xml=None)

    summary = extract(
        input_root=input_root, output_dir=output_dir, error_policy="partial"
    )

    assert summary.sections_written == 1
    assert summary.tiles_written == 4
    assert summary.tiles_skipped == 1
    assert len(summary.errors) == 1
    output_file = output_dir / "001.txt"
    assert output_file.exists()


def test_extract_section_policy_skips_output(tmp_path: Path) -> None:
    input_root = tmp_path / "input"
    output_dir = tmp_path / "output"
    section_dir = input_root / "001"
    section_dir.mkdir(parents=True)
    _write_good_section(section_dir)
    write_test_tiff(section_dir / "tile_bad.tif", xml=None)

    summary = extract(
        input_root=input_root, output_dir=output_dir, error_policy="section"
    )

    assert summary.sections_seen == 1
    assert summary.sections_written == 0
    assert summary.tiles_written == 0
    assert summary.tiles_skipped == 1
    assert not (output_dir / "001.txt").exists()


def test_extract_abort_policy_stops_run(tmp_path: Path) -> None:
    input_root = tmp_path / "input"
    output_dir = tmp_path / "output"
    section_a = input_root / "001"
    section_b = input_root / "002"
    section_a.mkdir(parents=True)
    section_b.mkdir(parents=True)

    write_test_tiff(section_a / "a_bad.tif", xml=None)
    _write_good_section(section_b)

    summary = extract(
        input_root=input_root, output_dir=output_dir, error_policy="abort"
    )

    assert summary.aborted is True
    assert summary.abort_reason is not None
    assert summary.sections_seen == 1
    assert not (output_dir / "001.txt").exists()
    assert not (output_dir / "002.txt").exists()


def test_extract_accepts_error_policy_enum(tmp_path: Path) -> None:
    input_root = tmp_path / "input"
    output_dir = tmp_path / "output"
    section_dir = input_root / "001"
    section_dir.mkdir(parents=True)
    _write_good_section(section_dir)
    write_test_tiff(section_dir / "tile_bad.tif", xml=None)

    summary = extract(
        input_root=input_root,
        output_dir=output_dir,
        error_policy=ErrorPolicy.SECTION,
    )

    assert summary.sections_written == 0
    assert summary.tiles_skipped == 1
    assert not (output_dir / "001.txt").exists()
