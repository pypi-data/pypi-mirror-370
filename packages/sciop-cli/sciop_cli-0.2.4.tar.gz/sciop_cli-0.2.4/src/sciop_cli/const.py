from importlib.metadata import version

from sciop_cli.types import Size

KiB = Size(2**10)
MiB = Size(2**20)
GiB = Size(2**30)
TiB = Size(2**40)

DEFAULT_TORRENT_CREATOR = f"sciop-cli {version('sciop-cli')}"
EXCLUDE_FILES = (".DS_Store", "Thumbs.db")
BLOCK_SIZE = 16 * KiB
PIECE_SIZES = tuple(BLOCK_SIZE * (2**exp) for exp in range(14))
"""16KiB to 128MiB, powers of two * block size."""
