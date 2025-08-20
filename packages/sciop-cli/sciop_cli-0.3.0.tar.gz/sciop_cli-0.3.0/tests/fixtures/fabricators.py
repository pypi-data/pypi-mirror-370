from typing import TYPE_CHECKING

import httpx
import pytest

from sciop_cli.config import Config, set_config

if TYPE_CHECKING:
    from sciop.models import Account, Dataset
    from sciop.testing.server import UvicornSyncServer
    from sqlmodel import Session


@pytest.fixture
async def account(run_server_sync: "UvicornSyncServer") -> tuple[str, str]:
    # say we have set our login info through the cli...
    username = "testuser"
    password = "testuser12345"
    async with httpx.AsyncClient() as client:
        account = await client.post(
            "http://localhost:8080/api/v1/register",
            data={"username": username, "password": password},
        )
    assert account.status_code == 200
    return username, password


@pytest.fixture()
async def config_logged_in(account: tuple[str, str], fresh_config: Config) -> Config:
    # say we have set our login info through the cli...
    username, password = account
    fresh_config.username = username
    fresh_config.password = password
    set_config(fresh_config)
    return fresh_config


@pytest.fixture()
async def as_admin(
    fresh_config: Config, session: "Session", run_server_sync: "UvicornSyncServer"
) -> "Account":
    from sciop.api.auth import get_password_hash
    from sciop.models import Account, Scope

    username = "admin"
    password = "adminadmin12"
    hashed_pw = get_password_hash(password)
    admin = Scope.get_item("admin", session=session)
    account = Account(username=username, hashed_password=hashed_pw, scopes=[admin])
    session.add(account)
    session.commit()
    session.refresh(account)
    fresh_config.username = username
    fresh_config.password = password
    set_config(fresh_config)
    return account


@pytest.fixture()
def claims_setup(as_admin: "Account", session: "Session") -> "Dataset":
    """
    Crappy in-place data setup pending exporting sciop fixtures in a testing module
    """
    from sciop.models import Dataset, DatasetPart, Tag

    tag = Tag(tag="default")
    ds = Dataset(
        title="default",
        slug="default",
        publisher="example",
        tags=[tag],
        account=as_admin,
        is_approved=True,
    )
    parts = [
        DatasetPart(part_slug=letter, is_approved=True, dataset=ds) for letter in ("a", "b", "c")
    ]
    ds.parts = parts
    session.add(ds)
    session.commit()
    session.refresh(ds)
    return ds
