from logging import getLogger
from pathlib import Path
from typing import Optional

import yaml
from platformdirs import PlatformDirs
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from sciop_cli.clients import ClientConfigs
from sciop_cli.types import KeychainSecretStr, TokenSecretStr

_dirs = PlatformDirs("sciop_cli", "sciop", ensure_exists=True)
_global_config = Path(_dirs.user_config_dir) / "sciop_cli.yaml"
_config: Optional["Config"] = None


def get_config(reload: bool = False) -> "Config":
    global _config
    if _config is None or reload:
        _config = Config()
    return _config


def set_config(cfg: "Config") -> "Config":
    """
    Set config, dumping to the global config yaml file.

    If a password is present, first try to save it in the keychain
    and exclude it from the dump.

    if we can't for some reason, dump it with a warning
    """
    global _config
    _config = cfg

    logger = getLogger("sciop_cli.config")
    dumped = cfg.model_dump(context={"update_keyring": True, "data": cfg.model_dump()})

    with open(_global_config, "w") as f:
        yaml.safe_dump(dumped, f)
    logger.debug(f"Dumped config to {_global_config}")
    return cfg


class Config(BaseSettings):
    """
    Environmental config for cli commands.

    Keep this light - just what we need to run cli commands,
    don't want this to be a major point of interaction.

    Values can be set in a .env file with a SCIOP_CLI_ prefix,
    a `sciop_cli.yaml` file in cwd,
    or the `sciop_cli` user config dir provided by
    [platformdirs](https://github.com/tox-dev/platformdirs)
    (e.g. `~/.config/sciop_cli/sciop_cli.yaml`)
    """

    instance_url: str = "https://sciop.net"
    username: str | None = None
    password: KeychainSecretStr() = None  # type: ignore[valid-type]
    request_timeout: float = 5
    """Default timeout to use in API requests."""
    upload_timeout: float = 300
    """Default timeout for file uploads in seconds"""
    token: TokenSecretStr = None
    """Expiring jwt, stored in config to reuse between cli calls"""
    clients: list[ClientConfigs] = Field(default_factory=list)
    """Configured bittorent clients"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="sciop_cli_",
        env_nested_delimiter="__",
        extra="ignore",
        nested_model_default_partial_update=True,
        yaml_file="sciop_cli.yaml",
        validate_assignment=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Read from the following sources,
        in order such that later sources in the list override earlier sources

        - `{config_dir}/sciop_cli.yaml`
        - `sciop_cli.yaml` (in cwd)
        - `.env` (in cwd)
        - environment variables prefixed with `SCIOP_`
        - arguments passed on config object initialization

        See [pydantic settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#customise-settings-sources)
        """
        global_source = YamlConfigSettingsSource(settings_cls, yaml_file=_global_config)
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            global_source,
        )
