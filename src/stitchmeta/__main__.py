"""Command line interface for stitchmeta."""

from pathlib import Path

import click

from stitchmeta import __version__
from stitchmeta.extractor import extract
from stitchmeta.models import ErrorPolicy


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
def main() -> None:
    """Extract microscopy tile metadata for downstream stitching."""


@main.command("extract")
@click.option(
    "-i",
    "--input-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Dataset root with section subdirectories (e.g., 001, 002).",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="Output directory for FEABAS files.",
)
@click.option(
    "-r",
    "--reader",
    "reader_name",
    default="fibics_tiff",
    show_default=True,
    help="Registered metadata reader.",
)
@click.option(
    "--invert-y/--no-invert-y",
    default=True,
    show_default=True,
    help="Invert Y-axis from SEM-style to image-style coordinates.",
)
@click.option(
    "-e",
    "--error-policy",
    type=click.Choice([policy.value for policy in ErrorPolicy], case_sensitive=False),
    default="partial",
    show_default=True,
    help="Failure handling mode for tile parse errors.",
)
def extract_command(
    input_root: Path,
    output_dir: Path,
    reader_name: str,
    invert_y: bool,
    error_policy: str,
) -> None:
    """Extract and write FEABAS metadata files."""
    try:
        typed_error_policy = ErrorPolicy.from_value(error_policy)
    except ValueError as exc:
        raise click.BadParameter(
            "error-policy must be one of: partial, section, abort",
            param_hint="--error-policy",
        ) from exc

    summary = extract(
        input_root=input_root,
        output_dir=output_dir,
        reader_name=reader_name,
        invert_y=invert_y,
        error_policy=typed_error_policy,
    )

    for section in summary.section_results:
        if section.wrote_output:
            click.echo(
                f"wrote {section.section_name}: "
                f"{section.tiles_written} tiles -> {section.output_path}"
            )
        else:
            click.echo(
                f"skipped {section.section_name}: {section.tiles_skipped} tiles skipped"
            )

    click.echo(
        "summary: "
        f"sections_seen={summary.sections_seen} "
        f"sections_written={summary.sections_written} "
        f"tiles_written={summary.tiles_written} "
        f"tiles_skipped={summary.tiles_skipped}"
    )

    if summary.aborted:
        raise click.ClickException(summary.abort_reason or "extraction aborted")


if __name__ == "__main__":
    main()
