from click.testing import CliRunner

from stitchmeta.__main__ import main

from tests.conftest import fibics_xml, write_test_tiff


def test_stitchmeta_cli_extract(tmp_path):
    input_root = tmp_path / "input"
    output_dir = tmp_path / "output"
    section_dir = input_root / "001"
    section_dir.mkdir(parents=True)

    write_test_tiff(
        section_dir / "tile.tif",
        xml=fibics_xml(fov_x_um=10.0, fov_y_um=10.0, x_um=0.0, y_um=0.0),
    )

    runner = CliRunner()
    result = runner.invoke(
        main,
        (
            "extract",
            "--input-root",
            str(input_root),
            "--output-dir",
            str(output_dir),
        ),
    )

    assert result.exit_code == 0
    assert (output_dir / "001.txt").exists()
    assert "sections_written=1" in result.output


def test_stitchmeta_cli_abort_nonzero_exit(tmp_path):
    input_root = tmp_path / "input"
    output_dir = tmp_path / "output"
    section_dir = input_root / "001"
    section_dir.mkdir(parents=True)
    write_test_tiff(section_dir / "broken.tif", xml=None)

    runner = CliRunner()
    result = runner.invoke(
        main,
        (
            "extract",
            "--input-root",
            str(input_root),
            "--output-dir",
            str(output_dir),
            "--error-policy",
            "abort",
        ),
    )

    assert result.exit_code != 0
