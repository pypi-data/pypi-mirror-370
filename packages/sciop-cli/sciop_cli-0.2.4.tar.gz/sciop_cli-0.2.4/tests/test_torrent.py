import json
from pathlib import Path
from random import gammavariate
from typing import Literal as L

import pytest

from sciop_cli.const import GiB, KiB, MiB, TiB
from sciop_cli.torrent import find_optimal_piece_size

from .conftest import DATA_DIR

DISTS = DATA_DIR / "distributions"


@pytest.mark.parametrize(
    "version",
    (
        pytest.param("v1", marks=pytest.mark.v1),
        pytest.param("v2", marks=pytest.mark.v2),
        pytest.param("hybrid", marks=pytest.mark.hybrid),
    ),
)
@pytest.mark.parametrize(
    "sizes,expected",
    [
        pytest.param([16 * KiB], 16 * KiB, id="single-block"),
        pytest.param([KiB for _ in range(10)], 16 * KiB, id="10-10kb"),
        pytest.param(
            [MiB for _ in range(10)],
            32 * KiB,
            id="10-10mb",
        ),
        pytest.param(
            [10 * MiB + 1 for _ in range(10)],
            512 * KiB,
            id="10-100mb",
        ),
        pytest.param(
            [(100 * MiB) + 1 for _ in range(10)],
            4 * MiB,
            id="10-1gb",
        ),
        pytest.param(
            [10 * (2**30) + 1 for _ in range(10)],
            16 * MiB,
            id="10-100gb",
        ),
        pytest.param(
            [50 * (2**30) for _ in range(10)],
            128 * MiB,
            id="10-500gb",
        ),
        pytest.param(
            [100 * (2**30) for _ in range(10)],
            128 * MiB,
            id="10-1tb",
        ),
        pytest.param(
            [TiB for _ in range(10)],
            128 * MiB,
            id="10-10tb",
        ),
        # --------------------------------------------------
        # Weird size distributions
        # --------------------------------------------------
        pytest.param(
            [100 * GiB] + [1 * KiB for _ in range(100)],
            16 * MiB,
            id="101-100gb-one-big-file",
        ),
        pytest.param(
            [100 * GiB] + [1 * KiB for _ in range(1000)],
            {"v1": 16 * MiB, "v2": 32 * MiB, "hybrid": 16 * MiB},
            id="1001-100gb-one-big-file",
        ),
        pytest.param(
            [100 * GiB] + [1 * KiB for _ in range(100000)],
            {"v1": 16 * MiB, "v2": 128 * MiB, "hybrid": 1 * MiB},
            id="100001-100gb-one-big-file",
        ),
        # --------------------------------------------------
        # Gamma distributions
        # --------------------------------------------------
        pytest.param(
            [gammavariate(5, 100) * KiB for _ in range(100)],
            {"v1": 256 * KiB, "v2": 256 * KiB, "hybrid": (128 * KiB, 256 * KiB)},
            id="100-1kb-gamma-5-100",
        ),
        pytest.param(
            [gammavariate(5, 100) * KiB for _ in range(10000)],
            {"v1": MiB, "v2": (4 * MiB, 2 * MiB), "hybrid": 1 * MiB},
            id="10000-1kb-gamma-5-100",
        ),
        pytest.param(
            [gammavariate(5, 100) * MiB for _ in range(100)],
            (8 * MiB, 16 * MiB),
            id="100-1mb-gamma-5-100",
        ),
        pytest.param(
            [gammavariate(5, 100) * GiB for _ in range(100)],
            128 * MiB,
            id="100-1gb-gamma-5-100",
        ),
        pytest.param(
            DISTS / "nbu_arwen_ver01.json",
            {"v1": 256 * KiB, "v2": 512 * KiB, "hybrid": 256 * KiB},
            id="chronam-arwen",
        ),
        pytest.param(
            DISTS / "dlc_chrysler_ver02.json",
            {"v1": 16 * MiB, "v2": 16 * MiB, "hybrid": 2 * MiB},
            id="chronam-chrysler",
        ),
    ],
)
def test_auto_piece_size(sizes: list[int] | Path, version: L["v1", "v2", "hybrid"], expected):
    """
    Auto piece sizing with default params should give us the piece size we expect :)
    """
    if isinstance(sizes, (Path, str)):
        with open(sizes) as f:
            sizes = json.load(f)

    paths = [str(idx) for idx in range(len(sizes))]
    piece_size, penalties = find_optimal_piece_size(
        path=paths, sizes=sizes, version=version, return_penalties=True
    )
    if isinstance(expected, int):
        assert piece_size == expected
    elif isinstance(expected, tuple):
        assert piece_size in expected
    else:
        exp_val = expected[version]
        if isinstance(exp_val, int):
            assert piece_size == exp_val
        else:
            assert piece_size in exp_val
