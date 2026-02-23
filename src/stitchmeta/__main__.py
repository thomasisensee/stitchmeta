"""Command line interface for stitchmeta."""

from pathlib import Path
from typing import cast

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
    "--input-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Dataset root with section subdirectories (e.g., 001, 002).",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="Output directory for FEABAS files.",
)
@click.option(
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
    "--error-policy",
    type=click.Choice(["partial", "section", "abort"], case_sensitive=False),
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
    normalized_error_policy = error_policy.lower()
    if normalized_error_policy not in {"partial", "section", "abort"}:
        raise click.BadParameter(
            "error-policy must be one of: partial, section, abort",
            param_hint="--error-policy",
        )
    typed_error_policy = cast(ErrorPolicy, normalized_error_policy)

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
