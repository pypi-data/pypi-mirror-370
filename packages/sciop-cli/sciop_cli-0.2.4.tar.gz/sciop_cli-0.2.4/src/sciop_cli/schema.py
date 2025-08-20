from __future__ import annotations

import fnmatch
import io
import logging
import re
from collections import OrderedDict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from textwrap import dedent
from typing import Annotated, Any, BinaryIO, Iterable, Iterator, Literal, Mapping, Self

from pydantic import BaseModel, BeforeValidator, Field, RootModel

from sciop_cli.types import PieceSize

logger = logging.getLogger(__name__)


FileLength = Annotated[int, Field(ge=0)]
SHA_256_DIGEST_LEN = 64
HEX_PATTERN = re.compile(r"^[0-9a-f]+$")
Sha256Hash = Annotated[
    str, Field(min_length=SHA_256_DIGEST_LEN, max_length=SHA_256_DIGEST_LEN, pattern=HEX_PATTERN)
]


class Sha256Checksum(BaseModel):
    algorithm: Literal["sha256"] = "sha256"
    value: Sha256Hash


def chunk_file(file: BinaryIO, chunk_size: int) -> Iterator[bytes]:
    assert chunk_size > 0, chunk_size
    while chunk := file.read(chunk_size):
        yield chunk


class Digest(BaseModel):
    length: FileLength
    checksum: Sha256Checksum = Field(discriminator="algorithm")

    @classmethod
    def chunks(cls, chunks: Iterable[bytes]) -> Self:
        count = 0
        hasher = sha256()

        for chunk in chunks:
            count += len(chunk)
            hasher.update(chunk)

        return cls(length=count, checksum=Sha256Checksum(value=hasher.hexdigest()))

    @classmethod
    def en_masse(cls, chunk: bytes) -> Self:
        return cls.chunks([chunk])

    @classmethod
    def file(cls, file: BinaryIO, *, chunk_size: int = io.DEFAULT_BUFFER_SIZE) -> Self:
        return cls.chunks(chunk_file(file, chunk_size))


class VerificationFailed(Exception):
    pass


class FileVerificationFailed(VerificationFailed):
    def __init__(self, prev: SingleFileManifest, cur: SingleFileManifest) -> None:
        self.prev = prev
        self.cur = cur
        super().__init__(
            dedent(
                """\
                file manifest failed to match file input:
                manifest:
                {prev}

                input:
                {cur}
                """
            ).format(prev=prev.model_dump_json(indent=2), cur=cur.model_dump_json(indent=2))
        )


class SingleFileManifest(BaseModel):
    manifest_kind: Literal["file"] = "file"
    digest: Digest

    @classmethod
    def generate_from_file(cls, file: BinaryIO) -> Self:
        return cls(digest=Digest.file(file))

    def verify(self, file: BinaryIO) -> None:
        cmp = type(self).generate_from_file(file)
        if cmp != self:
            raise FileVerificationFailed(self, cmp)


def _validate_file_tree_node_name(component: Any) -> Any:
    if isinstance(component, str):
        component_str = component
    elif isinstance(component, (bytes, bytearray)):
        try:
            component_str = component.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(
                f"file entry path component {component!r} is not a UTF-8 encoded string"
            ) from e
    else:
        raise ValueError(f"file entry path component {component!r} is not a string or bytes")

    for banned in ["\\", "/"]:
        if banned in component_str:
            raise ValueError(f"component {component_str} contained the banned character '{banned}'")
    for banned_component in [".", ".."]:
        if banned_component == component_str:
            raise ValueError(
                f"component {component_str} was equal to the banned string '{banned_component}'"
            )

    return component_str


FileEntryPathComponent = Annotated[str, BeforeValidator(_validate_file_tree_node_name)]


class FileEntry(BaseModel):
    entry_kind: Literal["file"] = "file"
    digest: Digest

    @classmethod
    def generate_from_file(cls, file: BinaryIO) -> Self:
        return cls(digest=Digest.file(file))


DirEntry = Annotated["FileEntry | SubdirEntry", Field(discriminator="entry_kind")]


@dataclass(frozen=True)
class IgnorePattern:
    glob: str
    rx: re.Pattern[str]

    @classmethod
    def compile(cls, glob: str) -> Self:
        return cls(glob=glob, rx=re.compile(fnmatch.translate(glob)))


class EmptyDir(Exception):
    pass


class DirEntries(RootModel[Mapping[FileEntryPathComponent, DirEntry]]):
    # FIXME: formulate this as a coroutine so that ignores can be computed on demand and it can be
    #        computed in parallel across threads.
    @classmethod
    def generate_from_directory(
        cls, directory: Path, root: Path, ignores: Iterable[IgnorePattern]
    ) -> Self:
        assert directory.is_relative_to(root), (directory, root)

        # Iterate through entries, recursing as necessary.
        sub_entries: dict[str, DirEntry] = {}
        for sub_entry in directory.iterdir():
            assert sub_entry.name not in sub_entries, (sub_entry, sub_entries)

            relative_path = sub_entry.relative_to(root)
            matched_ignore = False
            for pat in ignores:
                if pat.rx.search(str(relative_path)):
                    logger.debug("entry %s was ignored by glob pattern '%s'", sub_entry, pat.glob)
                    matched_ignore = True
                    break
            if matched_ignore:
                continue

            # TODO: checking file type will follow symlinks by default. We don't currently support
            #       symlinks within this metadata schema, so we will end up with duplicate copies of
            #       entries available via symlink. This is intentional, as bittorrent also does not
            #       support symlinks, but may be worth expanding in the future, as symlinks can be
            #       stored wholly in the metadata schema separate from the torrent data itself.
            if sub_entry.is_file():
                with sub_entry.open(mode="rb") as file:
                    sub_entries[sub_entry.name] = FileEntry.generate_from_file(file)
            elif sub_entry.is_dir():
                try:
                    sub_entries[sub_entry.name] = SubdirEntry.generate_from_directory(
                        sub_entry, root, ignores
                    )
                except EmptyDir:
                    logger.debug("subdir %s was empty", sub_entry)
                    continue
            else:
                logger.debug(
                    "directory entry is neither file, directory, nor symlink to such: %s", sub_entry
                )

        # If the directory was empty (either for having no valid entries, or having them all
        # filtered out by ignore patterns), raise an internal exception. We can't represent these in
        # bittorrent, so we can't use them in our metadata protocol yet either.
        # TODO: we could very well support empty directories external to the torrent itself, by
        #       re-inserting them upon download like we propose for symlinks above.
        if not sub_entries:
            raise EmptyDir

        # Sort the entries by key. This is almost definitely going to be the case already just by
        # using the filesystem native iteration order and relying on insertion order sorting for
        # dict in python 3.7+, but this ensures that result, allowing us to produce reproducible
        # json serialization which we can checksum.
        sorted_entries = OrderedDict((k, sub_entries[k]) for k in sorted(sub_entries.keys()))
        return cls(sorted_entries)

    def generate_all_entries(self) -> Iterator[tuple[Path, FileEntry]]:
        """Walk the recursive directory contents and produce complete file paths and digests."""
        for component, sub_entry in self.root.items():
            # If this is a file entry, then return just this last component as its path.
            if isinstance(sub_entry, FileEntry):
                yield (Path(component), sub_entry)
            else:
                # Otherwise, prepend this component to the paths generated by this subdirectory.
                for sub_component, file_entry in sub_entry.sub_entries.generate_all_entries():
                    yield (Path(component) / sub_component, file_entry)

    def verify_inexact(self, directory: Path) -> None:
        """Match the contents of this manifest against a specific directory.

        This method allows for other files not specified in the manifest to exist."""
        for relpath, file_entry in self.generate_all_entries():
            cur_path = directory / relpath
            try:
                with cur_path.open("rb") as f:
                    # Create a single-file manifest object, and delegate to its verify method.
                    try:
                        prev_entry = SingleFileManifest(digest=file_entry.digest)
                        prev_entry.verify(f)
                    except FileVerificationFailed as e:
                        raise InexactDirectoryVerificationFailed(
                            prev=DirectoryManifest(entries=self),
                            entry_path=relpath,
                            reason=f"file from input dir {directory} failed to match manifest",
                        ) from e
            except (FileNotFoundError, NotADirectoryError) as e:
                # NB: NotADirectoryError occurs if something that was a directory in the manifest is
                #     a file path in the input directory.
                raise InexactDirectoryVerificationFailed(
                    prev=DirectoryManifest(entries=self),
                    entry_path=relpath,
                    reason=f"file path was not found within input dir {directory}",
                ) from e


class SubdirEntry(BaseModel):
    entry_kind: Literal["subdir"] = "subdir"
    sub_entries: DirEntries

    @classmethod
    def generate_from_directory(
        cls, directory: Path, root: Path, ignores: Iterable[IgnorePattern]
    ) -> Self:
        return cls(sub_entries=DirEntries.generate_from_directory(directory, root, ignores))


class ExactDirectoryVerificationFailed(VerificationFailed):
    def __init__(self, prev: DirectoryManifest, cur: DirectoryManifest):
        self.prev = prev
        self.cur = cur
        super().__init__(
            dedent(
                """\
                directory manifest failed to exactly match directory input:
                manifest:
                {prev}

                input:
                {cur}
                """
            ).format(prev=prev.model_dump_json(indent=2), cur=cur.model_dump_json(indent=2))
        )


class InexactDirectoryVerificationFailed(VerificationFailed):
    def __init__(self, prev: DirectoryManifest, entry_path: Path, reason: str) -> None:
        self.prev = prev
        self.entry_path = entry_path
        self.reason = reason
        super().__init__(
            dedent(
                """\
                directory manifest failed to match directory input:
                manifest:
                {prev}

                failed entry was: {entry_path}
                reason: {reason}
                """
            ).format(prev=prev.model_dump_json(indent=2), entry_path=entry_path, reason=reason)
        )


class DirectoryManifest(BaseModel):
    manifest_kind: Literal["directory"] = "directory"
    entries: DirEntries

    @classmethod
    def generate_from_directory(cls, directory: Path, ignores: Iterable[IgnorePattern]) -> Self:
        return cls(entries=DirEntries.generate_from_directory(directory, directory, ignores))

    def verify_exact(self, directory: Path) -> None:
        cmp = type(self).generate_from_directory(directory, ignores=[])
        if cmp != self:
            raise ExactDirectoryVerificationFailed(self, cmp)

    def verify_inexact(self, directory: Path) -> None:
        self.entries.verify_inexact(directory)


class UnstableManifest(BaseModel):
    schema_version: Literal["unstable"] = "unstable"
    contents: SingleFileManifest | DirectoryManifest = Field(discriminator="manifest_kind")

    @classmethod
    def generate_from_file(cls, file: BinaryIO) -> Self:
        return cls(contents=SingleFileManifest.generate_from_file(file))

    @classmethod
    def generate_from_directory(
        cls, directory: Path, *, ignores: Iterable[IgnorePattern] = []
    ) -> Self:
        return cls(contents=DirectoryManifest.generate_from_directory(directory, ignores))


Manifest = Annotated[UnstableManifest, Field(discriminator="schema_version")]


class PackMap(BaseModel):
    """
    Summary of a directory packing operation,
    contains information for creating a torrent from a packed directory
    """

    piece_size: PieceSize
    files: list[Path]
