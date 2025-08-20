from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Sequence

from pydantic import BaseModel


class ClientConfig(BaseModel):
    """Base class for client configurations"""

    client: str
    """Set as a `Literal` in subclasses for union discrimination"""
    host: str
    port: int

    @abstractmethod
    def make_adapter(self) -> "BittorrentClientAdapter": ...


@dataclass
class BittorrentClientAdapter:
    """
    ABC for adapters
    """

    name: ClassVar[str]
    config: ClientConfig

    @classmethod
    def get_adapters(cls) -> dict[str, type["BittorrentClientAdapter"]]:
        """Get available client adapters"""
        return {subc.name: subc for subc in cls.__subclasses__()}

    def login(self) -> Any:
        """
        Login to the API, storing any token in the config
        """
        raise NotImplementedError()

    def add_torrent_file(self, torrent_path: Path, data_path: Path, **kwargs: Any) -> Any:
        """
        Add a torrent file to the client
        """
        raise NotImplementedError()

    def get_config(self) -> dict:
        """
        Get the client configuration
        """
        raise NotImplementedError()

    def set_config(self, config: dict) -> Any:
        """
        Set some new configuration
        """
        raise NotImplementedError()

    def get_torrents(self, **kwargs: Any) -> Sequence[dict]:
        """Get information about all torrents"""
        raise NotImplementedError()

    def get_torrent_info(self, infohash: str, **kwargs: Any) -> dict:
        """Get information about a single torrent"""
        raise NotImplementedError()

    def start_torrent(self, infohash: str, **kwargs: Any) -> Any:
        """Start downloading/seeding a torrent"""
        raise NotImplementedError()

    def stop_torrent(self, infohash: str, **kwargs: Any) -> Any:
        """Stop downloading/seeding a torrent"""
        raise NotImplementedError()

    def add_webseeds(self, infohash: str, urls: list[str], **kwargs: Any) -> Any:
        raise NotImplementedError()
