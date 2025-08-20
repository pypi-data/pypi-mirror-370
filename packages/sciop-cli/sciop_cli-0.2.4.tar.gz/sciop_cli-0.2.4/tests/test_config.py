import random
import string
from pathlib import Path

import keyring
import pytest
import yaml
from keyring.backends.fail import Keyring as FailBackend
from pydantic import SecretStr

from sciop_cli import config
from sciop_cli.config import Config, set_config


def test_instantiation_defaults(monkeypatch, tmp_path):
    """We should be able to instantiate config without setting any values"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(config, "_global_config", Path(tmp_path) / "sciop_cli_test.yaml")
    _ = Config()


def test_password_from_keychain(request: pytest.FixtureRequest):
    """We can get a password from the keychain automatically"""
    username = f"__test__{request.node.name}"
    expected = "__testpassword__"
    keyring.set_password("__testing__.sciop_cli", username, expected)

    cfg = Config(username=username)
    assert cfg.password
    assert cfg.password.get_secret_value() == expected


def test_set_config_no_password(monkeypatch, tmp_path: Path, request: pytest.FixtureRequest):
    """
    When we dump the config, and we have a password, and we can access a keyring,
    we should remove the password from the dump, save it in the keyring.
    """
    username = f"__test__{request.node.name}"
    expected = (
        f"__testpassword{''.join([random.choice(string.ascii_letters) for _ in range(10)])}__"
    )
    cfg_path = Path(tmp_path) / "sciop_cli_test.yaml"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(config, "_global_config", cfg_path)
    if keyring.get_password("__testing__.sciop_cli", username):
        keyring.delete_password("__testing__.sciop_cli", username)

    assert not keyring.get_password("__testing__.sciop_cli", username)
    cfg = Config(username=username, password=expected)
    cfg = set_config(cfg)

    with open(cfg_path) as f:
        dumped = yaml.safe_load(f)
    assert dumped["username"] == username
    assert dumped["password"] is None
    assert keyring.get_password("__testing__.sciop_cli", username) == expected

    # and we should get it again when we instantiate
    loaded = Config()
    assert loaded.username == username
    assert loaded.password.get_secret_value() == expected


def test_set_config_no_keyring(
    monkeypatch: pytest.MonkeyPatch, caplog, request: pytest.FixtureRequest
):
    """
    When no keyring is available, we should dump the password with a warning
    """
    monkeypatch.setattr(keyring.core, "_keyring_backend", FailBackend())

    username = f"__test__{request.node.name}"
    password = (
        f"__testpassword{''.join([random.choice(string.ascii_letters) for _ in range(10)])}__"
    )
    cfg = Config(username=username, password=password)
    dumped = cfg.model_dump(context={"update_keyring": True})
    assert dumped["password"] == password
    records = [r for r in caplog.records if r.name == "sciop_cli.config"]
    assert len(records) == 1
    assert "Dumping in plaintext" in records[0].message
    assert "No recommended backend was available" in records[0].message


def test_dump_token(request: pytest.FixtureRequest):
    """
    When we dump the config when setting config, we dump tokens in plaintext
    """
    username = f"__test__{request.node.name}"
    token = "".join([random.choice(string.ascii_letters) for _ in range(10)])
    password = "".join([random.choice(string.ascii_letters) for _ in range(10)])
    cfg = Config(username=username, password=password, token=token)
    dumped = cfg.model_dump(context={"update_keyring": True})
    assert dumped["token"] == token
    assert dumped["password"] is None

    dumped_reg = cfg.model_dump()
    assert isinstance(dumped_reg["token"], SecretStr)
