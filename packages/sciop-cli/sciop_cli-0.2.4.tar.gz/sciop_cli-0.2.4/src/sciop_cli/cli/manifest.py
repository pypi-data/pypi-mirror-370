from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import BinaryIO, Iterable, TextIO

import click
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup

from sciop_cli.schema import (
    EmptyDir,
    IgnorePattern,
    Manifest,
    SingleFileManifest,
    UnstableManifest,
)

logger = logging.getLogger(__name__)


@click.group()
def manifest() -> None:
    """
    Create and manage dataset manifests.
    """


@manifest.command()
@optgroup.group(
    "Dataset source",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="The file(s) making up the dataset to create a manifest from.",
)
@optgroup.option("-f", "--file", type=click.File("rb"), help="Path to single-file dataset.")
@optgroup.option(
    "-d",
    "--dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to directory dataset.",
)
@optgroup.group("Manifest generation", help="How to generate the manifest.")
@optgroup.option(
    "-o", "--output", type=click.File(mode="w"), default="-", help="Where to write the manifest."
)
@optgroup.option(
    "-i",
    "--ignore",
    type=str,
    multiple=True,
    default=[],
    help="Glob strings to ignore when scanning a directory.",
)
def create(file: BinaryIO | None, dir: Path | None, output: TextIO, ignore: Iterable[str]) -> None:
    """
    Create a manifest from a dataset on the local filesystem.
    """
    if file is not None:
        assert dir is None, dir
        if ignore:
            warnings.warn(
                "ignore strings are not processed for single-file datasets.", stacklevel=1
            )
        manifest = UnstableManifest.generate_from_file(file)
    else:
        assert dir is not None
        ignores = [IgnorePattern.compile(i) for i in ignore]
        try:
            manifest = UnstableManifest.generate_from_directory(dir, ignores=ignores)
        except EmptyDir as e:
            raise ValueError(f"metadata could not be generated: directory {dir} was empty.") from e
    output.write(manifest.model_dump_json())


@manifest.command()
@optgroup.group("Manifest analysis", help="How to interpret the manifest.")
@optgroup.option(
    "-m", "--manifest", type=click.File("rb"), required=True, help="Manifest file to analyze."
)
@optgroup.option(
    "--allow-extra-files/--no-allow-extra-files",
    type=bool,
    default=True,
    help="Whether to allow files in a directory dataset that are not specified in the manifest.",
)
@optgroup.group(
    "Dataset source",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="The file(s) making up the dataset to verify the manifest against.",
)
@optgroup.option("-f", "--file", type=click.File("rb"), help="Path to single-file dataset.")
@optgroup.option(
    "-d",
    "--dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Path to directory dataset.",
)
def verify(
    manifest: BinaryIO, allow_extra_files: bool, file: BinaryIO | None, dir: Path | None
) -> None:
    """
    Validate a manifest against a local copy of the dataset.
    """
    parsed_manifest = Manifest.model_validate_json(manifest.read())

    if isinstance(parsed_manifest.contents, SingleFileManifest):
        if file is None:
            raise ValueError(
                "manifest was for a single-file dataset, but input was not a single file."
            )
        parsed_manifest.contents.verify(file)
    else:
        if dir is None:
            raise ValueError("manifest was for a directory dataset, but input was not a directory.")
        if allow_extra_files:
            parsed_manifest.contents.verify_inexact(dir)
        else:
            try:
                parsed_manifest.contents.verify_exact(dir)
            except EmptyDir as e:
                raise ValueError(
                    f"metadata could not be generated: directory {dir} was empty."
                ) from e

    logger.debug("verification succeeded!")
