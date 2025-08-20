from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

import click.testing
import pytest

from sciop_cli.cli.main import cli
from sciop_cli.const import EXCLUDE_FILES
from sciop_cli.pack import (
    PACK_MODES,
    Compressor,
    DepthArgs,
    LeafArgs,
    PackArgs,
    PackManager,
    run_packing_pipeline,
)


def _make_fixture(root: Path, make_system_file: bool = False) -> None:
    """Dataset used by the full pipeline tests."""
    for sub, fname in (("a", "alpha.txt"), ("b", "beta.txt")):
        leaf = root / sub
        leaf.mkdir(parents=True, exist_ok=True)
        (leaf / fname).write_text("X")

    if make_system_file:
        (root / EXCLUDE_FILES[0]).write_text("ignore-me")


PACK_PARAMS: list[tuple[str, Literal[PACK_MODES], dict]] = [
    ("sha256", "leaf", {"skip_threshold": 1.0}),
    ("sha256", "depth", {"depth": 1}),
    ("sha256", "heuristic", {"min_filecount": 1}),
    ("sha512", "leaf", {"skip_threshold": 1.0}),
    ("sha512", "depth", {"depth": 1}),
    ("sha512", "heuristic", {"min_filecount": 1}),
]


@pytest.fixture(scope="function")
def packed_ds(tmp_path: Path, request):
    """Run one full pack pipeline & yield (base, args, packmap dict)."""
    algo, mode, extra = request.param
    base = tmp_path / "dataset"
    _make_fixture(base, make_system_file=True)

    args = PackArgs.from_kwargs(mode=mode, base_dir=str(base), hash_algo=algo, **extra)
    run_packing_pipeline(args)
    packm = json.loads((base / f"{base.name}.packmap.json").read_text())
    return base, args, packm


@pytest.mark.parametrize(
    "packed_ds", PACK_PARAMS, indirect=True, ids=lambda p: "-".join(map(str, p[:2]))
)
def test_manifest_and_packmap(packed_ds):
    base, args, packm = packed_ds
    manifest = base / f"manifest-{args.hash_algo}.txt"
    assert manifest.is_file()
    paths = {ln.split(maxsplit=1)[1] for ln in manifest.read_text().splitlines()}
    assert {"a/alpha.txt", "b/beta.txt"} == paths

    archives = packm["archives"]
    assert len(archives) == 2
    assert not any(EXCLUDE_FILES[0] in rec["archive"] for rec in archives)


@pytest.mark.parametrize("packed_ds", PACK_PARAMS, indirect=True)
def test_archives_exist_and_originals_removed(packed_ds):
    base, _args, packm = packed_ds
    for rec in packm["archives"]:
        assert (base / rec["archive"]).is_file()
        assert not (base / rec["src_dir"]).exists()


@pytest.mark.parametrize("packed_ds", PACK_PARAMS, indirect=True)
def test_roundtrip_restore(packed_ds):
    base, args, packm = packed_ds
    restored = PackManager(args).restore_directory()
    assert len(restored) == len(packm["archives"])
    for rel, fname in (("a", "alpha.txt"), ("b", "beta.txt")):
        assert (base / rel / fname).is_file()


def _selection_fixture(tmp_path: Path) -> Path:
    """
    sel/
      keep_me/x.dat
      skip_me/done.zip
      parent/child/y.dat
      parent/z.dat          (non-leaf; should **never** be selected)
      tiny/t.t
    """
    sel = tmp_path / "sel"
    (sel / "keep_me").mkdir(parents=True)
    (sel / "keep_me/x.dat").write_text("x")
    (sel / "skip_me").mkdir()
    (sel / "skip_me/done.zip").write_text("zip")
    (sel / "parent" / "child").mkdir(parents=True)
    (sel / "parent/child/y.dat").write_text("y")
    (sel / "parent/z.dat").write_text("z")  # non-leaf file
    (sel / "tiny").mkdir()
    (sel / "tiny/t.t").write_text("t")
    return sel


def _depth(path: str) -> int:
    """Component count in a relative POSIX path."""
    return len(Path(path).parents) if path else 0


def _is_leaf(base: Path, rel: str) -> bool:
    """
    Leaf = directory with **no sub-directories** (files are fine).
    """
    return all(not p.is_dir() for p in (base / rel).iterdir())


SELECTOR_CASES = [
    # DEPTH
    (DepthArgs, "depth", {"depth": 1}, {"keep_me", "skip_me", "tiny", "parent"}, {"parent/child"}),
    (DepthArgs, "depth", {"depth": 2}, {"parent/child"}, {"keep_me", "skip_me", "tiny", "parent"}),
    # LEAF
    (
        LeafArgs,
        "leaf",
        {"skip_threshold": 1.0},
        {"keep_me", "parent/child", "tiny"},
        {"skip_me", "parent"},
    ),
    (
        LeafArgs,
        "leaf",
        {"skip_threshold": 0.0},
        set(),
        {"keep_me", "skip_me", "parent/child", "tiny", "parent"},
    ),
]


@pytest.mark.parametrize("args_cls, mode, kwargs, must_have, must_not", SELECTOR_CASES)
def test_selector_positive_negative(
    tmp_path: Path,
    args_cls,
    mode: str,
    kwargs: dict,
    must_have: set[str] | None,
    must_not: set[str] | None,
):
    base = _selection_fixture(tmp_path)
    args = PackArgs.from_kwargs(mode=mode, base_dir=str(base), **kwargs)
    selected = set(Compressor.from_args(args).select_targets())

    if must_have is not None:
        assert must_have <= selected
    if must_not is not None:
        assert selected.isdisjoint(must_not)

    if mode == "depth":
        d = kwargs["depth"]
        assert all(_depth(p) == d for p in selected)

    if mode == "leaf":
        assert all(_is_leaf(base, p) for p in selected)


def _heuristic_fixture(tmp_path: Path) -> Path:
    """
    hsel/
      few/            (1 tiny file)           - should fail min_filecount
      many/           (3 tiny files)          - passes min_filecount
      small_mean/     (3 x 512-B files)       - mean 0.5 KiB
      large_mean/     (3 x 2 KiB files)       - mean 2 KiB
      low_total/      (10 x 50 KiB ≈ 0.5 MiB) - under 1 MiB
      high_total/     (2 x 1 MiB   ≈ 2 MiB)   - over 1 MiB
    """
    root = tmp_path / "hsel"
    spec = {
        "few": (1, 1),
        "many": (3, 1),
        "small_mean": (3, 512),
        "large_mean": (3, 2048),
        "low_total": (10, 50 * 1024),
        "high_total": (2, 1 * 1024 * 1024),
    }
    for dirname, (n, size) in spec.items():
        d = root / dirname
        d.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            (d / f"f{i}.bin").write_bytes(os.urandom(size))
    return root


HEURISTIC_RULES = [
    # rule, kwargs, must_have, must_not
    ("min_filecount", {"min_filecount": 2}, {"many"}, {"few"}),
    ("max_mean_kib", {"max_mean_kib": 1}, {"small_mean"}, {"large_mean"}),
    ("min_total_mib", {"min_total_mib": 1}, {"high_total"}, {"low_total"}),
]


@pytest.mark.parametrize("rule, kwargs, must_have, must_not", HEURISTIC_RULES)
def test_heuristic_rules(
    tmp_path: Path, rule: str, kwargs: dict, must_have: set[str], must_not: set[str]
):

    base = _heuristic_fixture(tmp_path)
    weights = {"file_count": 1, "mean_size": 1, "total_size": 1}
    if rule == "min_filecount":
        weights["file_count"] = 1
        weights["mean_size"] = weights["total_size"] = 0
    elif rule == "max_mean_kib":
        weights["mean_size"] = 1
        weights["file_count"] = weights["total_size"] = 0
    else:  # min_total_mib
        weights["total_size"] = 1
        weights["file_count"] = weights["mean_size"] = 0

    _rule_top_n = {"min_filecount": 2, "max_mean_kib": 3, "min_total_mib": 1}
    kw = dict(kwargs, top_n=_rule_top_n[rule])

    args = PackArgs.from_kwargs(
        mode="heuristic",
        base_dir=str(base),
        **kw,
        weights=weights,
    )
    selected = set(Compressor.from_args(args).select_targets())
    assert must_have <= selected
    assert selected.isdisjoint(must_not)


def test_cli_smoke(tmp_path: Path):
    base = tmp_path / "cli_ds"
    _make_fixture(base)

    runner = click.testing.CliRunner()
    result = runner.invoke(
        cli,
        [
            "pack",
            "--path",
            str(base),
            "--mode",
            "leaf",
            "--skip-threshold",
            "1",
            "--hash-algo",
            "sha256",
        ],
    )
    assert result.exit_code == 0, result.output
    assert (base / "manifest-sha256.txt").is_file()
    assert (base / f"{base.name}.packmap.json").is_file()
