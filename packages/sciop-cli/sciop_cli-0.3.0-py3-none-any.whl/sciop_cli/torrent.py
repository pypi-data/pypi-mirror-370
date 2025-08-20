import warnings
from collections.abc import Generator
from dataclasses import dataclass
from math import ceil, sqrt
from pathlib import Path
from statistics import median
from typing import Any, TypedDict, cast, overload
from typing import Literal as L

import bencode_rs
import libtorrent
from pydantic import TypeAdapter
from tqdm import tqdm

from sciop_cli.const import DEFAULT_TORRENT_CREATOR, EXCLUDE_FILES, PIECE_SIZES, GiB
from sciop_cli.exceptions import NoTrackersWarning
from sciop_cli.types import PieceSize


@dataclass
class PieceParams:
    target_pieces: int = 5000
    """Pick the piece size that gets us closest to this number of pieces"""
    small_torrent_threshold: int = GiB
    """
    For torrents with total sizes below this threshold (in bytes), 
    use the small_target_pieces target instead
    """
    small_target_pieces: int = 250
    """Target pieces when the total size is beneath the small torrent threshold"""
    target_weight: float = 1
    """Relative weight of the target_pieces value on piece size"""

    @overload
    @classmethod
    def from_version(cls, version: L["v1"], **kwargs: Any) -> "V1PieceParams": ...

    @overload
    @classmethod
    def from_version(cls, version: L["v2"], **kwargs: Any) -> "V2PieceParams": ...

    @overload
    @classmethod
    def from_version(cls, version: L["hybrid"], **kwargs: Any) -> "HybridPieceParams": ...

    @classmethod
    def from_version(cls, version: L["v1", "v2", "hybrid"] | str, **kwargs: Any) -> "PieceParams":
        """Create params for specific version"""
        if version == "v1":
            return V1PieceParams(**kwargs)
        elif version == "v2":
            return V2PieceParams(**kwargs)
        elif version == "hybrid":
            return HybridPieceParams(**kwargs)
        else:
            raise ValueError(f"Unknown torrent version: {version}")


@dataclass
class V1PieceParams(PieceParams):
    overhead_weight: float = 1.0e-10
    """
    Relative weight of the v1 overhead induced by pad files.
    
    Tiny tiny penalty, effectively only for breaking ties,
    because v1 torrents don't really have a overhead per se

    See :func:`.score_overhead` for details.
    """


@dataclass
class V2PieceParams(PieceParams):
    """
    Piece size is less important in v2-only torrents because the root hash ends up the same.

    By default we only care about the number of pieces and use overhead weight as a tiebreaker,
    but if you want to optimize a torrent for streaming (making pieces smaller),
    increase the overhead weight.
    """

    overhead_weight: float = 1.0e-10
    """
    Tiny overhead penalty that favors smaller piece sizes to break ties.
    """


@dataclass
class HybridPieceParams(PieceParams):
    overhead_weight: float = 0.1
    """
    Relative weight of the v1 overhead induced by pad files.
    This term is *not* normalized to force its range to 0-1 like the other penalties,
    it is instead normalized to the total size of the torrent:
    the absolute value of the size of the overhead matters as well as 
    the relative magnitude per each piece size.
    """


class Penalty(TypedDict):
    piece_size: int
    type: str
    value: float


@overload
def find_optimal_piece_size(path: Path | list[Path]) -> int: ...


@overload
def find_optimal_piece_size(
    path: Path | list[Path], version: L["v1", "v2", "hybrid"] | str
) -> int: ...


@overload
def find_optimal_piece_size(
    path: Path | list[Path],
    version: L["v1"],
    sizes: list[int] | None,
    params: V1PieceParams | None = None,
) -> int: ...


@overload
def find_optimal_piece_size(
    path: Path | list[Path],
    version: L["v2"],
    sizes: list[int] | None,
    params: V2PieceParams | None = None,
) -> int: ...


@overload
def find_optimal_piece_size(
    path: Path | list[Path],
    version: L["hybrid"],
    sizes: list[int] | None,
    params: HybridPieceParams | None,
) -> int: ...


@overload
def find_optimal_piece_size(
    path: Path | list[Path],
    version: L["v1", "v2", "hybrid"] | str,
    sizes: list[int] | None,
) -> int: ...


@overload
def find_optimal_piece_size(
    path: Path | list[Path],
    version: str,
    sizes: list[int] | None,
    params: dict | None,
) -> int: ...


@overload
def find_optimal_piece_size(
    path: Path | list[Path],
    version: L["v1", "v2", "hybrid"] | str,
    sizes: list[int] | None,
    params: V1PieceParams | V2PieceParams | HybridPieceParams | dict | None,
    return_penalties: L[True],
) -> tuple[int, dict[str, list[Penalty]]]: ...


def find_optimal_piece_size(
    path: Path | str | list[Path] | list[str],
    version: L["v1", "v2", "hybrid"] | str = "hybrid",
    sizes: list[int] | None = None,
    params: V1PieceParams | V2PieceParams | HybridPieceParams | dict | None = None,
    return_penalties: bool = False,
) -> int | tuple[int, dict[str, list[Penalty]]]:
    """
    Estimate an optimal piece size for the given file(s).

    Each version has slightly different considerations for piece size
    - v1: Piece size determined by total size, pick a piece size that makes a
        reasonable number of pieces (i.e. 1000 - 50000-ish)
    - v2: Piece size determined by total size and size distribution.
        Pick a piece size that balances a reasonable number of pieces with
        the piece size being roughly the size of the median file.
    - hybrid: Piece size determined by total size and padding overhead.
        Pick a piece size that balances a reasonable number of pieces
        without creating an enormous amount of padding overhead.

    See the docstrings on the *PieceParams models for more details.

    Args:
        path (Path): File or directory of files to be added to torrent
        version ("v1", "v2", "hybrid"): version of torrent to be created.
        params (V1PieceParams | V2PieceParams | HybridPieceParams | dict):
            Parameterization of piece size optimization.
            See model docstrings for more detail.
        return_penalties (bool): If ``True``, return the calculated penalties

    Returns:

    """
    version = cast(L["v1", "v2", "hybrid"], version)
    if isinstance(path, list):
        paths = [Path(p) for p in path] if isinstance(path[0], str) else path
    else:
        path = Path(path)
        paths = [path] if path.is_file() else list(iter_files(path))

    paths = cast(list[Path], paths)

    if sizes is None:
        sizes = [p.stat().st_size for p in paths]

    assert len(sizes) == len(
        paths
    ), "Length of provided sizes does not match length of detected paths"

    if isinstance(params, dict):
        params = PieceParams.from_version(version=version, **params)
    elif params is None:
        params = PieceParams.from_version(version=version)

    if version == "v1":
        params = cast(V1PieceParams | None, params)
        return find_optimal_piece_size_v1(
            paths=paths, sizes=sizes, params=params, return_penalties=return_penalties
        )
    elif version == "v2":
        params = cast(V2PieceParams | None, params)
        return find_optimal_piece_size_v2(
            paths=paths, sizes=sizes, params=params, return_penalties=return_penalties
        )
    elif version == "hybrid":
        params = cast(HybridPieceParams | None, params)
        return find_optimal_piece_size_hybrid(
            paths=paths, sizes=sizes, params=params, return_penalties=return_penalties
        )
    else:
        raise ValueError(f"Unkown torrent version {version}")


def find_optimal_piece_size_v1(
    paths: list[Path],
    sizes: list[int],
    params: V1PieceParams | None = None,
    return_penalties: bool = False,
) -> int | tuple[int, dict[str, list[Penalty]]]:
    """
    Find a piece size that produces a reasonable number of pieces,
    using overhead as a tiebreaker (e.g. for very small torrents where most piece sizes
    would yield a single-piece torrent.)
    """
    if params is None:
        params = V1PieceParams()
    target_pieces = _normalize_penalties(
        _penalty_target_pieces(paths=paths, sizes=sizes, version="v1", params=params)
    )
    # mildly penalize overhead in the case of very small torrents
    overhead = _penalty_overhead(paths=paths, sizes=sizes)

    piece_size = _min_penalty(
        penalties=[target_pieces, overhead],
        weights=[params.target_weight, params.overhead_weight],
    )
    if return_penalties:
        return piece_size, {"target": target_pieces, "overhead": overhead}
    else:
        return piece_size


def find_optimal_piece_size_v2(
    paths: list[Path],
    sizes: list[int],
    params: V2PieceParams | None = None,
    return_penalties: bool = False,
) -> int | tuple[int, dict[str, list[Penalty]]]:
    """
    Find a piece size that balances having a reasonable number of pieces
    with the hashing overhead of having a piece size that is significantly larger
    than the median filesize in a torrent
    """
    if params is None:
        params = V2PieceParams()

    target_pieces = _normalize_penalties(
        _penalty_target_pieces(paths=paths, sizes=sizes, version="v2", params=params)
    )
    overhead = _penalty_overhead(paths=paths, sizes=sizes)
    piece_size = _min_penalty(
        penalties=[target_pieces, overhead],
        weights=[params.target_weight, params.overhead_weight],
    )
    if return_penalties:
        return piece_size, {"target": target_pieces, "overhead": overhead}
    else:
        return piece_size


def find_optimal_piece_size_hybrid(
    paths: list[Path],
    sizes: list[int],
    params: HybridPieceParams | None = None,
    return_penalties: bool = False,
) -> int | tuple[int, dict[str, list[Penalty]]]:
    """
    Find a piece size that minimizes padfile overhead and produces a reasonable number of pieces.
    """
    if params is None:
        params = HybridPieceParams()

    # don't normalize overhead - it's normalized w.r.t. to the total size
    # (e.g. a 100% overhead would be 1)
    overhead = _penalty_overhead(paths=paths, sizes=sizes)
    target_pieces = _normalize_penalties(
        _penalty_target_pieces(paths=paths, sizes=sizes, version="hybrid", params=params)
    )

    piece_size = _min_penalty(
        penalties=[overhead, target_pieces],
        weights=[params.overhead_weight, params.target_weight],
    )
    if return_penalties:
        return piece_size, {"target": target_pieces, "overhead": overhead}
    else:
        return piece_size


def _min_penalty(penalties: list[list[Penalty]], weights: list[float]) -> int:
    """
    Given a list of piece size penalties and weights,
    return the piece size that minimizes the sum of the weighted penalties.

    Args:
        penalties (list[list[Penalty]]): List of penalty terms per piece size
        weights (list[float]): list of weights, length == to number of penalty lists.
    """
    assert len(penalties) == len(weights)
    # collect penalties by piece size
    piece_penalties = {}
    for pens in zip(*penalties):
        assert all(
            [p["piece_size"] == pens[0]["piece_size"]] for p in pens
        ), "piece sizes must be sorted before scoring"
        piece_penalties[pens[0]["piece_size"]] = sum(
            [p["value"] * weight for p, weight in zip(pens, weights)]
        )

    # invert mapping to select piece size by penalty
    penalty_pieces = {v: k for k, v in piece_penalties.items()}
    return penalty_pieces[min(penalty_pieces.keys())]


def calculate_overhead(sizes: list[int], piece_size: int) -> list[float]:
    """
    Given a list of file sizes and a piece size, calculate expected v1 padfile overhead
    """
    return [piece_size - (size % piece_size) if size != piece_size else 0 for size in sizes]


def _penalty_overhead(paths: list[Path], sizes: list[int]) -> list[Penalty]:
    """
    Total v1 padfile overhead for a given piece size,
    Normalized to the total size of the given files.
    """
    penalties = []
    total_size = sum(sizes)
    for piece_size in PIECE_SIZES:
        overheads = calculate_overhead(sizes, piece_size)
        penalties.append(
            Penalty(
                piece_size=piece_size,
                type="overhead",
                value=sum(overheads) / total_size,
            )
        )
    return penalties


def calculate_total_pieces(
    sizes: list[int], piece_size: int, version: L["v1", "v2", "hybrid"] | str
) -> int:
    if version == "v1":
        total_size = sum(sizes)
        total_pieces = ceil(total_size / piece_size)
    elif version in ("v2", "hybrid"):
        total_pieces = sum([ceil(size / piece_size) for size in sizes])
    else:
        raise ValueError(f"Unkown torrent version {version}")
    return total_pieces


def _penalty_target_pieces(
    paths: list[Path], sizes: list[int], version: L["v1", "v2", "hybrid"], params: PieceParams
) -> list[Penalty]:
    """
    Absolute value of difference in actual pieces vs. target pieces, with specializations.

    - If the largest possible piece size produces more pieces than the target number of pieces,
      then we squash the penalty range so that we preserve the relative penalization of
      the second to large pieces - i.e. we put stronger weight on making larger pieces,
      assuming the values will be normalized in the next step.
    - For piece sizes that make *fewer* pieces than the target piece number,
      exponentially penalize piece sizes that make us make a very small number of pieces.
      A torrent with a single piece is not very useful.
    """
    total_size = sum(sizes)
    if total_size < params.small_torrent_threshold:
        target = params.small_target_pieces
    else:
        target = params.target_pieces

    penalties = []
    for piece_size in PIECE_SIZES:
        total_pieces = calculate_total_pieces(sizes, piece_size, version)
        penalty = float(abs(total_pieces - target))

        # if we still can't make the target with the largest piece size,
        # squash the range because making half as many pieces is much worse than usual
        if (min_pieces := ceil(total_size / max(PIECE_SIZES))) > target:
            penalty = penalty ** min(((target * 2) / min_pieces), 1)
        # penalize going under more than going over
        elif total_pieces < target:
            # piece sizes that want to make us make one piece...
            # take the fraction of the target and total so e.g. making 1 piece is 0.999...
            # and making target-1 is 0.00001...
            # then square to make larger misses (like making one piece) matter more
            # then double so that we increase the penalty by up to 2 in the worst cases,
            # and otherwise leave unchangesd
            exponent = (((target - total_pieces) / target) ** 2) * 2
            penalty *= max(exponent, 1)

        penalties.append(
            Penalty(
                piece_size=piece_size,
                type="target",
                value=penalty,
            )
        )
    return penalties


def _penalty_median_size(paths: list[Path], sizes: list[int]) -> list[Penalty]:
    median_size = median(sizes)

    return [
        Penalty(piece_size=piece_size, type="median", value=max(piece_size - median_size, 0) ** 2)
        for piece_size in PIECE_SIZES
    ]


def _normalize_penalties(penalties: list[Penalty]) -> list[Penalty]:
    """Normalize the values of a single kind of penalty to be between 0 and 1"""
    penalties = sorted(penalties, key=lambda p: p["piece_size"])
    max_pen = max([p["value"] for p in penalties])
    min_pen = min([p["value"] for p in penalties])
    pen_range = max_pen - min_pen
    for i in range(len(penalties)):
        if pen_range == 0:
            # all are equal
            penalties[i]["value"] = 0
        else:
            # take the sqrt of the value after normalizing 0-1 to enlarge small errors around 0
            penalties[i]["value"] = sqrt((penalties[i]["value"] - min_pen) / (max_pen - min_pen))
    return penalties


def create_torrent(
    path: Path,
    trackers: list[str] | None = None,
    comment: str | None = None,
    creator: str = DEFAULT_TORRENT_CREATOR,
    webseeds: list[str] | None = None,
    similar: list[str] | None = None,
    version: L["v1", "v2", "hybrid"] = "hybrid",
    bencode: bool = True,
    piece_size: PieceSize = 512 * (2**10),
    pbar: bool = False,
) -> dict | bytes:
    """
    Create a hybrid v1/v2 torrent with libtorrent

    Args:
        path: File or directory to create a torrent for
        trackers: list of trackers to add to the torrent.
            Each torrent is added on a separate tier, in order,
            so that by default clients announce to all trackers
        comment: Additional comment string embedded in the torrent
        creator: Annotation of what tool was used to create the torrent,
            defaults to `sciop-cli-{version}`
        webseeds: List of HTTP urls where the content can also be found.
            If `path` is a directory, the files on the server
            must match the directory structure of the torrent and their content exactly.
        similar: Infohashes of torrents that have identical files to those in this torrent.
            Clients can use this to deduplicate downloads.
        version: Torrent version to create. Default ``"hybrid"`` creates v1/v2 compatible torrents.
            v1 is *not recommended.*
        bencode: If ``True`` ( default ) return the bencoded bytestring.
            Otherwise return a python dictionary
        piece_size: The size of data chunks to hash.
            Choosing a piece size can be complicated, but ideally you want
            to pick a piece size that yields 20-50k pieces, and less than <100k.
            Smaller torrents can have fewer pieces, in that case match the piece size
            to being slightly smaller than the median file size.
            Once torrents start to have >200k pieces, clients suffer to efficiently
            track which peers have what pieces, and also struggle to cache the data.
        pbar: It ``True``, show a progress bar while hashing pieces.

    Returns:
        bytes: bencoded torrent ready for writing
        dict: python-formatted torrent file dict
    """
    path = Path(path)
    fs = libtorrent.file_storage()

    if path.is_dir():
        # get paths and sort
        paths = []
        for _path in iter_files(path):
            # no absolute paths in the torrent plz
            rel_path = _path.relative_to(path)
            # add the parent again as the root
            rel_path = Path(path.name) / rel_path
            paths.append((str(rel_path), _path.stat().st_size))

        paths = sorted(paths, key=lambda x: x[0])
        for p, size in paths:
            fs.add_file(p, size)

    else:
        fs.add_file(path.name, path.stat().st_size)

    if fs.num_files() == 0:
        raise

    piece_size = TypeAdapter(PieceSize).validate_python(piece_size)

    flags = 0
    if version == "v1":
        flags = libtorrent.create_torrent.v1_only
    elif version == "v2":
        flags = libtorrent.create_torrent.v2_only

    torrent = libtorrent.create_torrent(fs, piece_size=piece_size, flags=flags)

    if trackers:
        for tier, tracker in enumerate(trackers):
            torrent.add_tracker(tracker, tier)
    else:
        warnings.warn(
            "No trackers passed when creating a torrent. "
            "This torrent will likely not be able to be seeded efficiently. "
            "Consider adding trackers, or use the default trackers "
            "(with `sciop_cli.data.get_default_trackers()`)",
            NoTrackersWarning,
            stacklevel=2,
        )

    if webseeds:
        for webseed in webseeds:
            torrent.add_url_seed(webseed)

    if similar:
        for s in similar:
            torrent.add_similar_torrent(s)

    if comment:
        torrent.set_comment(comment)

    torrent.set_creator(creator)

    _pbar = None
    if pbar:
        _pbar = tqdm(desc="hashing pieces...", total=torrent.num_pieces())

        def _pbar_callback(piece_index: int) -> None:
            _pbar.update()

        libtorrent.set_piece_hashes(torrent, str(path.parent.resolve()), _pbar_callback)
        _pbar.close()
    else:
        libtorrent.set_piece_hashes(torrent, str(path.parent.resolve()))

    ret = torrent.generate()
    if bencode:
        return bencode_rs.bencode(ret)
    else:
        return ret


def iter_files(path: Path) -> Generator[Path, None, None]:
    """
    Recursively iterate through files, excluding system files
    """
    for p in path.rglob("*"):
        if p.name in EXCLUDE_FILES or p.is_dir():
            continue
        yield p
