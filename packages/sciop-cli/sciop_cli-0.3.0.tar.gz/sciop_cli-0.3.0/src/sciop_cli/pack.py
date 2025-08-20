from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Sequence
from logging import getLogger
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal, overload

import humanize
import zstandard as zstd
from annotated_types import Gt
from pydantic import BaseModel, DirectoryPath, Field, TypeAdapter
from tqdm import tqdm

from sciop_cli.const import EXCLUDE_FILES
from sciop_cli.models.pack import HASH_ALGOS, FileHash, HashManifest, PackedDirectory, PackMap

HashCtor = Callable[[], Any]
ALGO_MAP: dict[str, HashCtor] = {
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
    # any new hash functions we like
}

COMPRESSED_EXTS = (".zip", ".tar", ".gz", ".tgz", ".bz2", ".rar", ".xz", ".7z", ".tar.zst")
SELECTED_COMP_FILETYPE = ".tar.zst"
PACKED_BY = "sciop-cli"
PACK_MODES = Literal["heuristic", "depth", "leaf"]


class PackArgs(BaseModel):
    mode: str
    base_dir: DirectoryPath
    hash_algo: HASH_ALGOS = "sha512"

    @overload
    @classmethod
    def from_kwargs(cls, mode: Literal["heuristic"], **kwargs: Any) -> HeuristicArgs: ...
    @overload
    @classmethod
    def from_kwargs(cls, mode: Literal["depth"], **kwargs: Any) -> DepthArgs: ...
    @overload
    @classmethod
    def from_kwargs(cls, mode: Literal["leaf"], **kwargs: Any) -> LeafArgs: ...
    @overload
    @classmethod
    def from_kwargs(
        cls, mode: PACK_MODES, **kwargs: Any
    ) -> HeuristicArgs | DepthArgs | LeafArgs: ...
    @classmethod
    def from_kwargs(cls, mode, **kwargs):
        adapter = TypeAdapter(
            Annotated[HeuristicArgs | DepthArgs | LeafArgs, Field(discriminator="mode")]
        )
        return adapter.validate_python({"mode": mode, **kwargs})


class HeuristicWeights(BaseModel):
    file_count: float = 1
    mean_size: float = 1
    total_size: float = 1


class HeuristicArgs(PackArgs):
    mode: Literal["heuristic"]
    min_filecount: int = 0
    max_mean_kib: int = 0
    min_total_mib: int = 0
    weights: HeuristicWeights = Field(default_factory=HeuristicWeights)
    top_n: Annotated[int, Gt(0)] | None = None


class DepthArgs(PackArgs):
    mode: Literal["depth"]
    depth: int


class LeafArgs(PackArgs):
    mode: Literal["leaf"]
    skip_threshold: float


def _dir_stats(path: Path) -> tuple[int, int]:
    """Return (total_bytes, file_count) under *path* recursively."""
    total = count = 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
            count += 1
    return total, count


def _walk_bottom_up(root: Path) -> Iterable[tuple[str, list[str], list[str]]]:
    return os.walk(root, topdown=False)


def generate_checksums(base_dir: str | Path, algorithm: HASH_ALGOS = "sha512") -> Path:
    base = Path(base_dir).expanduser().resolve()
    if not base.is_dir():
        raise ValueError(f"{base!r} is not a directory")

    # discover files
    files, total = [], 0
    for p in base.rglob("*"):
        if (
            p.is_file()
            and not re.match(r"^manifest-\w+\.txt$", p.name)
            and p.name not in EXCLUDE_FILES
        ):
            files.append(p)
            total += p.stat().st_size

    bar = tqdm(
        total=total, unit="B", unit_scale=True, desc=f"Hashing {algorithm.upper()}", file=sys.stdout
    )
    try:
        hashes = []
        for path in files:
            hashes.append(FileHash.from_path(path=path, relative_to=base, algo=algorithm, pbar=bar))

        manifest = HashManifest(hashes=hashes, algo=algorithm)
        return manifest.write(base)
    finally:
        bar.close()


def compress_folder(folder_path: str) -> str | None:

    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError(f"{folder!r} is not a directory")

    # free-space sanity check
    total_bytes, _ = _dir_stats(folder)
    try:
        usage = shutil.disk_usage(folder.parent)
    except Exception:
        pass
    else:
        if usage.free < total_bytes:
            raise OSError(
                f"Out of disk space, directory is {humanize.naturalsize(total_bytes)}, "
                f"{humanize.naturalsize(usage.free)} available."
            )

    archive_path = folder.with_suffix(".tar.zst")
    temp_path = folder.with_suffix(".tar.zst.part")

    try:
        with temp_path.open("wb") as fout:
            cctx = zstd.ZstdCompressor(level=3)
            with (
                cctx.stream_writer(fout, closefd=False) as zfh,
                tarfile.open(fileobj=zfh, mode="w|") as tar,
            ):
                for root, _dirs, files in os.walk(folder_path):
                    for fname in files:
                        if fname in EXCLUDE_FILES:
                            continue
                        src = os.path.join(root, fname)
                        rel = os.path.relpath(src, folder_path)
                        tar.add(src, arcname=rel, recursive=False)

            # ensure all buffers are flushed to disk
            fout.flush()
            os.fsync(fout.fileno())

        # atomic rename
        temp_path.replace(archive_path)
        return str(archive_path)

    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _decompress_tar_zst(archive: Path) -> bool:
    """
    Extract <name>.tar.zst into a sibling directory <name>/.
    Deletes the archive on success; returns True if extracted.
    """
    if archive.suffixes[-2:] != [".tar", ".zst"]:
        return False

    out_dir = archive.with_suffix("").with_suffix("")  # strip .zst then .tar
    if out_dir.exists():
        return False

    try:
        with (
            archive.open("rb") as fin,
            zstd.ZstdDecompressor().stream_reader(fin) as zr,
            tarfile.open(fileobj=zr, mode="r|") as tar,
        ):
            tar.extractall(out_dir)

        archive.unlink()
        return True

    except Exception:
        return False


### Compressor classes


class Compressor(ABC):
    """Abstract compressor – subclasses supply `select_targets()`."""

    args_cls: ClassVar[type[PackArgs]]

    def __init__(self, args: PackArgs):
        self.base_dir = Path(args.base_dir)

    @overload
    @classmethod
    def from_args(cls, args: HeuristicArgs) -> HeuristicCompressor: ...
    @overload
    @classmethod
    def from_args(cls, args: DepthArgs) -> DepthCompressor: ...
    @overload
    @classmethod
    def from_args(cls, args: LeafArgs) -> LeafCompressor: ...
    @overload
    @classmethod
    def from_args(cls, args: PackArgs) -> Compressor: ...
    @classmethod
    def from_args(cls, args):
        for subcls in Compressor.__subclasses__():
            if isinstance(args, subcls.args_cls):
                return subcls(args=args)
        raise ValueError(f"No compressor found for args type: {args}")

    @abstractmethod
    def select_targets(self) -> list[str]: ...

    def run(self) -> list[str]:
        processed: list[str] = []
        for rel in tqdm(self.select_targets(), desc="compress", unit="dir"):
            if compress_folder(str(self.base_dir / rel)):
                processed.append(rel)
        return processed


class HeuristicCompressor(Compressor):
    """
    Heuristic directory selector based directly on the fields in `PackArgs`.
    """

    args_cls = HeuristicArgs

    def __init__(self, args: HeuristicArgs):
        super().__init__(args)
        self.args = args

    def _by_filecount(self) -> list[str]:
        limit: int = self.args.min_filecount or 0
        counts: dict[str, int] = {}
        chosen: set[str] = set()
        for d, ds, fs in _walk_bottom_up(self.base_dir):
            tot = len(fs) + sum(counts.get(os.path.join(d, x), 0) for x in ds)
            counts[d] = tot
            if tot >= limit and not any(os.path.join(d, x) in chosen for x in ds):
                chosen.add(d)
        return sorted(chosen, key=lambda p: counts[p], reverse=True)

    def _by_mean(self) -> list[str]:
        byte_limit = (self.args.max_mean_kib or 0) * 1024
        stats: dict[str, tuple[int, int]] = {}
        chosen: set[str] = set()
        for d, ds, fs in _walk_bottom_up(self.base_dir):
            total = sum(Path(d, f).stat().st_size for f in fs)
            cnt = len(fs)
            for x in ds:
                b, c = stats.get(os.path.join(d, x), (0, 0))
                total += b
                cnt += c
            stats[d] = (total, cnt)
            if (
                cnt
                and total / cnt <= byte_limit
                and not any(os.path.join(d, x) in chosen for x in ds)
            ):
                chosen.add(d)
        return sorted(chosen, key=lambda p: stats[p][0] / stats[p][1])

    def _by_total(self) -> list[str]:
        byte_limit = (self.args.min_total_mib or 0) * 1_048_576
        stats: dict[str, int] = {}
        chosen: set[str] = set()
        for d, ds, fs in _walk_bottom_up(self.base_dir):
            total = sum(Path(d, f).stat().st_size for f in fs)
            for x in ds:
                total += stats.get(os.path.join(d, x), 0)
            stats[d] = total
            if total >= byte_limit and not any(os.path.join(d, x) in chosen for x in ds):
                chosen.add(d)
        return sorted(chosen, key=lambda p: stats[p], reverse=True)

    def _rank_sum(self, cand: dict[str, Sequence[str]]) -> list[str]:
        scores: dict[str, int] = {}
        for name, dirs in cand.items():
            w = getattr(self.args.weights, name)
            for r, p in enumerate(dirs):
                scores[p] = scores.get(p, 0) + w * (len(dirs) - r)
        ranked = sorted(scores, key=lambda p: (-scores[p], p))
        if self.args.top_n:
            ranked = ranked[: self.args.top_n]
        return [
            os.path.relpath(p, self.base_dir)
            for p in ranked
            if not any(o != p and o.startswith(p.rstrip(os.sep) + os.sep) for o in ranked)
        ]

    def select_targets(self) -> list[str]:
        return self._rank_sum(
            {
                "file_count": self._by_filecount(),
                "mean_size": self._by_mean(),
                "total_size": self._by_total(),
            }
        )


class LeafCompressor(Compressor):
    args_cls = LeafArgs

    def __init__(self, args: LeafArgs):
        super().__init__(args)
        self.args = args
        self.skip = self.args.skip_threshold

    def select_targets(self) -> list[str]:
        leaves: list[str] = []
        for d, ds, fs in os.walk(self.base_dir, topdown=False):
            if ds or not fs:
                continue
            tot = len(fs)
            comp = sum(1 for f in fs if f.lower().endswith(COMPRESSED_EXTS))
            skip = self.skip or 0.0
            if comp / tot >= skip:
                continue
            leaves.append(os.path.relpath(d, self.base_dir))
        return leaves


class DepthCompressor(Compressor):
    """
    Selects every directory that lies exactly *depth* levels beneath base_dir.

      depth = 1  → immediate sub-directories
      depth = 2  → grandchildren, etc.
    """

    args_cls = DepthArgs

    def __init__(self, args: DepthArgs):
        super().__init__(args)
        self.args = args
        self.depth = args.depth

    def select_targets(self) -> list[str]:

        targets: list[str] = []
        for p in self.base_dir.rglob("*"):
            if p.is_dir():
                rel = p.relative_to(self.base_dir)
                if len(rel.parts) == self.depth:
                    targets.append(rel.as_posix())
        return targets


class PackManager:
    def __init__(self, args: PackArgs):
        self.args = args
        self.base = Path(self.args.base_dir).resolve()
        self.packmap_path = self.base / f"{self.base.name}.packmap.json"

    def scan(self, targets: list[str]) -> Path:
        """
        Perform one-pass scan over each target in `targets`, gathering:
          - pre_archive_bytes
          - file_count
          - archive             (relative path to <target>.SELECTED_COMP_FILETYPE, if it exists)
          - post_archive_bytes

        Writes a single .packmap.json with all fields filled in at once.
        Returns {dataset}.packmap.json path.
        """
        total_before = total_after = total_files = 0
        recs = []

        for rel in targets:
            folder = self.base / rel
            # Look for the archive file that would be created for this target
            comp_candidate = folder.with_suffix(SELECTED_COMP_FILETYPE)
            if not comp_candidate.exists():
                continue
            # Compute size_before & file_count
            b, f = _dir_stats(folder)
            total_before += b
            total_files += f

            size_after = comp_candidate.stat().st_size
            total_after += size_after

            recs.append(
                PackedDirectory(
                    src_dir=Path(rel),
                    pre_archive_bytes=b,
                    file_count=f,
                    archive=comp_candidate.relative_to(self.base),
                    post_archive_bytes=size_after,
                )
            )

        packmap = PackMap(
            archives=recs,
            total_size_before=total_before,
            total_size_after=total_after,
            total_file_count=total_files,
        )

        p = self.packmap_path
        p.write_text(packmap.model_dump_json(indent=2), encoding="utf-8")
        return p

    def write_sums(self) -> Path:
        return generate_checksums(self.base, algorithm=self.args.hash_algo)

    def delete_originals(self) -> list[str]:
        """
        Remove each original directory listed in .packmap.json, but only if its
        corresponding archive exists. Returns a list of src_dir paths that were deleted.
        """
        deleted: list[str] = []
        packmap_path = self.packmap_path
        if not packmap_path.exists():
            return deleted

        data = json.loads(packmap_path.read_text(encoding="utf-8"))
        for rec in data.get("archives", []):
            rel_dir = rec.get("src_dir")
            if not rel_dir:
                continue

            folder_path = self.base / rel_dir
            comp_path = folder_path.with_suffix(SELECTED_COMP_FILETYPE)

            # Only delete the original if the archive is present
            if comp_path.exists() and folder_path.exists() and folder_path.is_dir():
                try:
                    shutil.rmtree(folder_path)
                    deleted.append(rel_dir)
                except Exception:
                    # If deletion fails (permissions, in-use, etc.), skip it
                    continue

        return deleted

    def restore_directory(self) -> list[str]:
        """
        Extract each <dir>.tar.zst listed in .packmap.json, then delete the archive.
        Returns a list of archive paths that were successfully restored.
        """
        restored: list[str] = []

        packmap_path = self.packmap_path
        if not packmap_path.exists():
            return restored

        data = json.loads(packmap_path.read_text(encoding="utf-8"))

        # Collect only the archives that actually exist and need restoring
        archives: list[str] = [
            rec["archive"]
            for rec in data.get("archives", [])
            if rec.get("archive") and (self.base / rec["archive"]).exists()
        ]
        if not archives:
            return restored

        # Progress bar: one tick per archive restored
        for rel_archive in tqdm(
            archives,
            desc="restore",
            unit="archive",
            file=sys.stdout,
        ):
            comp_path = self.base / rel_archive
            if _decompress_tar_zst(comp_path):
                restored.append(rel_archive)

        return restored


def run_packing_pipeline(args: PackArgs) -> None:
    """
    Drive the entire packing workflow for *args.base_dir*:

      1.   Write SHA512.sums to base_dir
      2.   Run compressor to select target folders
      3.   Compress each selected directory into an archive file
      4.   Scan base_dir to produce .packmap.json
      5.   Delete original folders
      6.   Print summary

    """
    logger = getLogger("sciop_cli.pack")
    manager = PackManager(args)
    base = manager.base

    # create manifest
    manifest_path = manager.write_sums()
    logger.info(f"Wrote checksum manifest → {manifest_path.relative_to(base)}")

    # build compressor and choose targets
    compressor = Compressor.from_args(args)
    targets = compressor.select_targets()
    if not targets:
        logger.info("No directories matched the selection criteria – nothing to do.")
        return

    # compress targets
    processed = compressor.run()

    # build manifest
    packmap_path = manager.scan(targets)

    # delete original folders
    manager.delete_originals()

    data = json.loads(packmap_path.read_text(encoding="utf-8"))
    before = data.get("total_size_before", 0)
    after = data.get("total_size_after", 0)
    saved = 0.0 if before == 0 else (1 - after / before) * 100

    logger.info(
        f"Packing complete: compressed {len(processed)} folder(s), "
        f"reducing size from {humanize.naturalsize(before, binary=True)} "
        f"to {humanize.naturalsize(after, binary=True)} "
        f"({saved:.1f}% saved)."
    )
