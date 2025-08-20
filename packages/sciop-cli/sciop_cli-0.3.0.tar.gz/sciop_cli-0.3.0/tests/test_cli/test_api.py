import json
from typing import TYPE_CHECKING

from click.testing import CliRunner

from sciop_cli.cli.api import login as login_cli
from sciop_cli.cli.api import next_claim as next_claim_cli
from sciop_cli.config import Config, get_config

if TYPE_CHECKING:
    from .sciop import UvicornSyncServer


def test_login(
    run_server_sync: "UvicornSyncServer", fresh_config: Config, account: tuple[str, str]
):
    """
    We can log in through the CLI!
    """
    cfg = get_config()
    assert cfg.username is None
    assert cfg.password is None
    runner = CliRunner()

    res = runner.invoke(login_cli, ["--username", account[0], "--password", account[1]])
    assert res.exit_code == 0
    cfg2: Config = get_config()
    assert cfg2.username == account[0]
    assert cfg2.password.get_secret_value() == account[1]
    assert cfg2.token is not None


def test_get_next_claim(as_admin, claims_setup, run_server_sync):
    """
    After logging in, we can get the next dataset part and print it as json
    """

    runner = CliRunner()

    res = runner.invoke(next_claim_cli, ["--dataset", "default", "--json"])
    assert res.exit_code == 0
    out = json.loads(res.stdout.splitlines()[-1])
    assert out["status"] == "in_progress"
    assert out["dataset"] == "default"
    assert out["dataset_part"] == "a"
    assert out["account"] == "admin"
