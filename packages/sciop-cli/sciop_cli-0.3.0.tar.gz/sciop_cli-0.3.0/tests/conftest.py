from pathlib import Path

import pytest
from sciop.testing.fixtures.config import set_config as sciop_set_config  # noqa: F401
from sciop.testing.fixtures.db import *  # noqa: F401
from sciop.testing.fixtures.server import *  # noqa: F401

from sciop_cli.config import Config

from .fixtures import *

DATA_DIR = Path(__file__).parent / "data"

pytest_plugins = ("sciop.testing.plugin",)


@pytest.fixture(autouse=True, scope="session")
def session_monkeypatch_config(
    monkeypatch_session: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """sessionwide baseline for our config..."""
    from sciop_cli import config, types
    from sciop_cli.config import Config, set_config

    session_dir = tmp_path_factory.mktemp("sciop_cli_session")
    monkeypatch_session.setattr(config, "_global_config", session_dir / "sciop_cli_test.yaml")
    monkeypatch_session.setattr(types, "_password_prefix", "__testing__.sciop_cli")

    new_config = Config(
        username=None,
        password=None,
        token=None,
        instance_url="http://127.0.0.1:8080",
        request_timeout=10,
    )
    set_config(new_config)


@pytest.fixture(autouse=True, scope="session")
def monkeypatch_sciop_config(
    monkeypatch_session: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> None:
    from sciop.config import main as scfg_main

    new_config = scfg_main.Config(
        env="test",
        secret_key="1" * 64,
        enable_versions=True,
        paths={
            "torrents": tmp_path_factory.mktemp("torrents"),
            "db": "memory",
            "docs": tmp_path_factory.mktemp("docs"),
            "logs": tmp_path_factory.mktemp("logs"),
        },
        logs={"request_timing": False},
        server={"base_url": "http://localhost:8080"},
        services={
            "clear_jobs": True,
            "site_stats": {"enabled": False},
            "tracker_scraping": {"enabled": False},
        },
    )
    monkeypatch_session.setattr(scfg_main, "_config", new_config)


@pytest.fixture()
def fresh_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    from sciop_cli import config
    from sciop_cli.config import Config, set_config

    monkeypatch.setattr(config, "_global_config", tmp_path / "sciop_cli_test.yaml")

    new_config = Config(
        username=None, password=None, token=None, instance_url="http://127.0.0.1:8080"
    )
    set_config(new_config)
    return new_config
