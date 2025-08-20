from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import qbittorrentapi

from sciop_cli.clients.base import BittorrentClientAdapter, ClientConfig
from sciop_cli.types import KeychainSecretStr

_client_secret = KeychainSecretStr(("client", "host", "port"))


class QBittorrentConfig(ClientConfig):
    """
    Client configuration for qbittorrent to be stored in the global config yaml
    """

    client: Literal["qbittorrent"] = "qbittorrent"
    username: str
    password: KeychainSecretStr(("client", "host", "port"))  # type: ignore[valid-type]

    def make_adapter(self) -> "QBittorrentAdapter":
        return QBittorrentAdapter(config=self)


@dataclass
class QBittorrentAdapter(BittorrentClientAdapter):
    name = "qbittorrent"
    config: QBittorrentConfig
    _client: qbittorrentapi.Client | None = None

    @property
    def client(self) -> qbittorrentapi.Client:
        if self._client is None:
            self._client = qbittorrentapi.Client(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password.get_secret_value(),
            )
        return self._client

    def login(self) -> None:
        self.client.auth_log_in()

    def add_torrent_file(self, torrent_path: Path, data_path: Path, **kwargs: Any) -> str:
        return self.client.torrents_add(
            torrent_files=[str(torrent_path)], save_path=str(data_path), **kwargs
        )

    def get_config(self) -> qbittorrentapi.ApplicationPreferencesDictionary:
        return self.client.app_preferences()

    def set_config(self, config: qbittorrentapi.ApplicationPreferencesDictionary) -> None:  # type: ignore[override]
        return self.client.app_set_preferences(prefs=config)

    def get_torrents(self, **kwargs: Any) -> qbittorrentapi.TorrentInfoList:
        return self.client.torrents_info(**kwargs)

    def get_torrent_info(self, infohash: str, **kwargs: Any) -> qbittorrentapi.TorrentDictionary:
        return self.client.torrents_info(torrent_hashes=[infohash], **kwargs)[0]

    def start_torrent(self, infohash: str, **kwargs: Any) -> None:
        return self.client.torrents_resume(torrent_hashes=[infohash], **kwargs)

    def stop_torrent(self, infohash: str, **kwargs: Any) -> None:
        return self.client.torrents_pause(torrent_hashes=[infohash], **kwargs)

    def add_webseeds(self, infohash: str, urls: list[str], **kwargs: Any) -> Any:
        self.client.torrents_add_webseeds(torrent_hashes=[infohash], urls=urls, **kwargs)
