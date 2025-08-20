import random
import string

import keyring
from pydantic import TypeAdapter

from sciop_cli.clients import ClientConfigs
from sciop_cli.config import get_config, set_config


def test_client_login_keychain(fresh_config):
    """
    We can add multiple clients with same username and use keychain
    """
    cfg_1 = {
        "client": "qbittorrent",
        "username": "admin",
        "password": "".join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(16)]
        ),
        "host": "localhost",
        "port": 8080,
    }
    cfg_2 = {
        "client": "qbittorrent",
        "username": "admin",
        "password": "".join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(16)]
        ),
        "host": "localhost",
        "port": 8081,
    }
    adapter = TypeAdapter(ClientConfigs)
    cfg_1_model = adapter.validate_python(cfg_1)
    cfg_2_model = adapter.validate_python(cfg_2)
    cfg = get_config()
    cfg.clients.append(cfg_1_model)
    cfg.clients.append(cfg_2_model)
    set_config(cfg)

    pw_1 = keyring.get_password(
        f"__testing__.sciop_cli.{cfg_1['client']}.{cfg_1['host']}.{cfg_1['port']}", "admin"
    )
    pw_2 = keyring.get_password(
        f"__testing__.sciop_cli.{cfg_2['client']}.{cfg_2['host']}.{cfg_2['port']}", "admin"
    )
    assert pw_1 == cfg_1["password"]
    assert pw_2 == cfg_2["password"]

    cfg = get_config(reload=True)
    assert cfg.clients[0].password.get_secret_value() == cfg_1["password"]
    assert cfg.clients[1].password.get_secret_value() == cfg_2["password"]
