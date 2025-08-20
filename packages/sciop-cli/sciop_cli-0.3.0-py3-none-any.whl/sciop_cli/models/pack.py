import hashlib
import uuid
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator
from tqdm import tqdm

from sciop_cli.const import CHECKSUM_CHUNK, DEFAULT_TORRENT_CREATOR
from sciop_cli.types import PosixPath, UTCDateTime

HASH_ALGOS = Literal["sha512", "sha256"]


class PackedDirectory(BaseModel):
    """A single packed directory within a packmap"""

    src_dir: PosixPath
    archive: PosixPath
    pre_archive_bytes: int
    post_archive_bytes: int
    file_count: int


class PackMap(BaseModel):
    """
    Metadata file containing information about files before being compressed/packed,
    as well as the parameterization of the packing.
    """

    packmap_version: int = 1
    sciop_cli_version: str = Field(default_factory=lambda: version("sciop-cli"))
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: UTCDateTime = Field(default_factory=lambda: datetime.now(UTC))
    packed_by: str = DEFAULT_TORRENT_CREATOR
    archives: list[PackedDirectory] = Field(default_factory=list)
    total_size_before: int
    total_size_after: int
    total_file_count: int


class FileHash(BaseModel):
    algo: HASH_ALGOS
    path: PosixPath
    digest: str
    """hexdigest of hash"""

    @classmethod
    def from_path(
        cls,
        path: Path,
        algo: HASH_ALGOS,
        relative_to: Path,
        pbar: tqdm | None = None,
        chunk_size: int = CHECKSUM_CHUNK,
    ) -> "FileHash":
        h = hashlib.new(algo)
        with path.open("rb") as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
                if pbar:
                    pbar.update(len(chunk))
        return FileHash(algo=algo, path=path.relative_to(relative_to), digest=h.hexdigest())


class HashManifest(BaseModel):
    """Manifest of hashes and relative paths"""

    algo: HASH_ALGOS
    hashes: list[FileHash]

    @model_validator(mode="after")
    def matching_algos(self) -> Self:
        """all file hashes have the same algo as the manifest"""
        assert all(
            [hash.algo == self.algo for hash in self.hashes]
        ), "All hashes must be computed with the manifest's hashing algo"
        return self

    def write(self, path: Path) -> Path:
        """Write to a manifest-{algo}.txt file.

        Args:
            path (Path): The *directory* to write the manifest into
                (filename is fixed according to the algo).
        """
        # invoke serialization
        dumped = self.model_dump()
        manifest_lines = [" ".join([h["digest"], h["path"]]) for h in dumped["hashes"]]
        manifest = "\n".join(manifest_lines)
        output = path / f"manifest-{dumped['algo']}.txt"
        output.write_text(manifest)
        return output
