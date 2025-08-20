"""
Placeholder models that mimic sciop's models,
until we can split them off into a separate package and single-source them.
"""

import sys
from datetime import datetime
from typing import Literal

if sys.version_info >= (3, 12):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict


class Token(TypedDict):
    access_token: str
    token_type: Literal["bearer"]


class DatasetClaim(TypedDict):
    created_at: datetime
    updated_at: datetime
    dataset: str
    dataset_part: NotRequired[str]
    account: str
    status: Literal["in_progress", "completed"]


class TorrentFile(TypedDict):
    file_name: str
    v1_infohash: NotRequired[str | None]
    v2_infohash: NotRequired[str | None]
    short_hash: str
    version: Literal["v1", "v2", "hybrid"]
    total_size: int
    piece_size: int
    torrent_size: int
    announce_urls: list[str]
    seeders: NotRequired[int | None]
    leechers: NotRequired[int | None]


class Upload(TypedDict):
    created_at: datetime
    updated_at: datetime
    is_approved: bool
    is_removed: bool
    method: str | None
    description: str | None
    dataset: str
    dataset_parts: NotRequired[list[str]]
    seeders: NotRequired[int | None]
    leechers: NotRequired[int | None]
    torrent: TorrentFile
