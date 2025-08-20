import json as json_
from collections import defaultdict
from pathlib import Path
from typing import Literal as L
from typing import cast

import click
import humanize
from pydantic import TypeAdapter, ValidationError
from rich import print
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from sciop_cli.const import DEFAULT_TORRENT_CREATOR, PIECE_SIZES
from sciop_cli.data import get_default_trackers
from sciop_cli.torrent import (
    calculate_overhead,
    calculate_total_pieces,
    create_torrent,
    find_optimal_piece_size,
    iter_files,
)
from sciop_cli.types import PieceSize


@click.group()
def torrent() -> None:
    """
    Create and manage torrents
    """


@torrent.command()
def pack() -> None:
    """
    Pack a directory to prepare it for torrent creation

    - Generate a manifest for the directory
    - Archive small files
    - Emit a .packmap.json description of the packing operation
    """
    raise NotImplementedError()


@torrent.command()
@click.option(
    "-p",
    "--path",
    required=True,
    help="Path to a directory or file to create .torrent from",
    type=click.Path(exists=True),
)
@click.option(
    "-t",
    "--tracker",
    required=False,
    default=None,
    multiple=True,
    help="Trackers to add to the torrent. can be used multiple times for multiple trackers. "
    "If not present, use the default trackers from https://sciop.net/docs/uploading/default_trackers.txt",
)
@click.option(
    "--default-trackers/--no-default-trackers",
    is_flag=True,
    default=None,
    help="If trackers are specified with --tracker, "
    "--default-trackers appends the default trackers to that list, "
    "otherwise just use the supplied trackers (--no-default-trackers has no effect). "
    "If no trackers are specified, "
    "--no-default-trackers prevents adding the default tracker list,"
    "which is done by default (--default-trackers has no effect).",
)
@click.option(
    "-s",
    "--piece-size",
    default=None,
    help="Piece size, in bytes. If not given, calculate piece size automatically."
    "Use `sciop-cli torrent piece-size` to preview the ",
    show_default=True,
)
@click.option(
    "--comment",
    default=None,
    required=False,
    help="Optional comment field for torrent",
)
@click.option(
    "--creator",
    default=DEFAULT_TORRENT_CREATOR,
    show_default=True,
    required=False,
    help="Optional creator field for torrent",
)
@click.option(
    "-w",
    "--webseed",
    required=False,
    default=None,
    multiple=True,
    help="Add HTTP webseeds as additional sources for torrent. Can be used multiple times. "
    "See https://www.bittorrent.org/beps/bep_0019.html",
)
@click.option(
    "--similar",
    required=False,
    default=None,
    multiple=True,
    help="Add infohash of a similar torrent. "
    "Similar torrents are torrents who have files in common with this torrent, "
    "clients are able to reuse files from the other torrents if they already have them downloaded.",
)
@click.option(
    "-2",
    "--v2",
    is_flag=True,
    default=False,
    help="Make a v2-only torrent (otherwise, hybrid v1/v2)",
)
@click.option("--progress/--no-progress", default=True, help="Enable progress bar (default True)")
@click.option(
    "-o",
    "--output",
    required=False,
    default=None,
    type=click.Path(exists=False),
    help=".torrent file to write to. Otherwise to stdout",
)
def create(
    path: Path,
    tracker: list[str] | tuple[str] | None = None,
    default_trackers: bool | None = None,
    piece_size: PieceSize | None = None,
    comment: str | None = None,
    creator: str = DEFAULT_TORRENT_CREATOR,
    webseed: list[str] | None = None,
    similar: list[str] | None = None,
    v2: bool = False,
    progress: bool = True,
    output: Path | None = None,
) -> None:
    """
    Create a torrent from a file or directory.

    Uses libtorrent to create standard torrent files.
    Will create a hybrid v1/v2 torrent file.

    See https://www.libtorrent.org/reference-Create_Torrents.html
    form details on fields, all input here is passed through to
    libtorrent's creation methods.
    """
    # recast tuple to list or none rather than tuple or empty tuple
    tracker = list(tracker) if tracker else None
    version = "v2" if v2 else "hybrid"
    version = cast(L["v2", "hybrid"], version)

    if piece_size is None:
        click.echo("No piece size specified, estimating optimal piece size")
        piece_size = find_optimal_piece_size(path=Path(path).absolute(), version=version)

        click.echo(f"Piece size estimated as {humanize.naturalsize(piece_size, binary=True)}")
    if not tracker and (default_trackers is None or default_trackers):
        click.echo(
            "No trackers specified, using default trackers from "
            "sciop.net/docs/uploading/default_trackers.txt"
        )
        tracker = get_default_trackers()
    elif tracker and default_trackers:
        default_tracker_list = get_default_trackers()
        tracker.extend(default_tracker_list)

    result = create_torrent(
        path,
        trackers=tracker,
        piece_size=piece_size,
        comment=comment,
        creator=creator,
        webseeds=webseed,
        similar=similar,
        version=version,
        pbar=progress,
        bencode=True,
    )
    result = cast(bytes, result)
    if output:
        with open(output, "wb") as f:
            f.write(result)
    else:
        click.echo(result)


@torrent.command("piece-size")
@click.option(
    "-p",
    "--path",
    required=True,
    help="Path to a directory or file to create .torrent from",
    type=click.Path(exists=True),
)
@click.option(
    "--json",
    is_flag=True,
    default=False,
    help="Rather than evaluating a directory, "
    "path is a json array of integers representing a theoretical distribution of file sizes",
)
@click.option(
    "--view",
    type=click.Choice(["optimal", "comparison"]),
    default="optimal",
    show_default=True,
    help="What type of piece size table to show.\n"
    "- optimal (default): the piece size that the optimizer would pick with default params "
    "for each torrent version + associated stats\n"
    "- comparison: the number of pieces (and stats) for each choice of piece size."
    "usually used with --version to just show one at a time",
)
@click.option(
    "-v",
    "--version",
    type=click.Choice(["v1", "v2", "hybrid", "all"]),
    default="hybrid",
    show_default=True,
    help='When view == "comparison", which version to show',
)
@click.option(
    "-w",
    "--weight",
    multiple=True,
    help="version=key=val pairs of weight parameters, "
    "can be passed multiple times for multiple kwargs. "
    "E.g. --weight hybrid=overhead_weight=0.5",
)
def piece_size(
    path: Path,
    json: bool = False,
    view: L["optimal", "comparison"] = "optimal",
    version: L["v1", "v2", "hybrid", "all"] = "hybrid",
    weight: list[str] | None = None,
) -> None:
    """
    Show the optimal piece sizes calculated for each torrent version
    for a given file or directory.

    Any additional kwargs passed from the CLI are collected and passed on to the
    "optimal piece size" calculation when view == optimal.
    This allows you to see what different weights on the params might do.
    """
    path = Path(path)
    if json:
        with open(path) as f:
            sizes = json_.load(f)
        adapter = TypeAdapter(list[int])
        try:
            adapter.validate_python(sizes)
        except ValidationError as e:
            raise ValueError("JSON sizes must be given as an array of integers") from e
        # fake paths are fine, we are passing the sizes explicitly
        paths = [Path(f"__{i}.notafile") for i in range(len(sizes))]
    else:
        paths = [path] if path.is_file() else list(iter_files(path))
        sizes = [p.stat().st_size for p in paths]

    if view == "optimal":
        if weight:
            weight_kwargs: dict[str, dict] = defaultdict(dict)
            for arg in weight:
                ver, key, val = arg.split("=")
                weight_kwargs[ver][key] = float(val)
            # weight_kwargs = cast(V1PieceParams | V2PieceParams | HybridPieceParams, weight_kwargs)
        else:
            weight_kwargs = {}
        panel = _optional_piece_size(path, paths, sizes, weight_kwargs=weight_kwargs)
    elif view == "comparison":
        panel = _comparison_piece_size(path, paths, sizes, version)
    else:
        raise ValueError("unknown view type")
    print(panel)


def _summary_table(paths: list[Path], sizes: list[int]) -> Table:
    summary = Table(show_header=False)
    summary.add_column("", style="bold magenta")
    summary.add_column("")
    summary.add_row("N Files", humanize.number.intcomma(len(paths)))
    summary.add_row("Total size", humanize.naturalsize(sum(sizes), binary=True))
    return summary


def _optional_piece_size(
    path: Path, paths: list[Path], sizes: list[int], weight_kwargs: dict[str, dict] | None = None
) -> Panel:
    versions = ("v1", "v2", "hybrid")
    params = {} if weight_kwargs is None else weight_kwargs
    piece_sizes = {
        v: find_optimal_piece_size(path=paths, version=v, sizes=sizes, params=params.get(v))
        for v in versions
    }
    n_pieces = {v: calculate_total_pieces(sizes, piece_sizes[v], v) for v in versions}
    hybrid_overhead = sum(calculate_overhead(sizes, piece_sizes["hybrid"]))

    summary = _summary_table(paths, sizes)

    pieces = Table(title="Piece sizes")
    pieces.add_column("Version")
    pieces.add_column("Piece Size")
    pieces.add_column("N Pieces")
    pieces.add_column("Padding Overhead")
    for v in ("v1", "v2", "hybrid"):
        row = [v, str(piece_sizes[v]), humanize.number.intcomma(n_pieces[v])]

        if v == "hybrid":
            row.append(humanize.naturalsize(hybrid_overhead, binary=True))
        pieces.add_row(*row)

    header = Text("Optimal piece sizes")

    panel = Panel(Group(header, summary, pieces), title=str(path))
    return panel


def _comparison_piece_size(
    path: Path, paths: list[Path], sizes: list[int], version: L["v1", "v2", "hybrid", "all"]
) -> Panel:

    header = Text("Piece size comparison")
    summary = _summary_table(paths, sizes)
    if version == "all":
        panels = [_comparison_table(paths, sizes, v) for v in ("v1", "v2", "hybrid")]
    else:
        panels = [_comparison_table(paths, sizes, version)]

    panel = Panel(Group(header, summary, *panels), title=str(path))
    return panel


def _comparison_table(paths: list[Path], sizes: list[int], version: str) -> Table:
    pieces = Table(title=version)
    pieces.add_column("Piece Size")
    pieces.add_column("N Pieces")
    if version == "hybrid":
        pieces.add_column("Padding Overhead")

    for ps in PIECE_SIZES:
        row = [str(ps), humanize.number.intcomma(calculate_total_pieces(sizes, ps, version))]
        if version == "hybrid":
            row.append(humanize.naturalsize(sum(calculate_overhead(sizes, ps)), binary=True))
        pieces.add_row(*row)
    return pieces
