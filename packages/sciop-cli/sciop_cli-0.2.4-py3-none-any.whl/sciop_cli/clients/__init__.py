from typing import Annotated, TypeAlias, Union

from pydantic import Field

from sciop_cli.clients.base import BittorrentClientAdapter, ClientConfig
from sciop_cli.clients.qbt import QBittorrentAdapter, QBittorrentConfig

ClientConfigs: TypeAlias = Annotated[Union[QBittorrentConfig,], Field(discriminator="client")]

__all__ = [
    "BittorrentClientAdapter",
    "ClientConfig",
    "ClientConfigs",
    "QBittorrentAdapter",
    "QBittorrentConfig",
]
