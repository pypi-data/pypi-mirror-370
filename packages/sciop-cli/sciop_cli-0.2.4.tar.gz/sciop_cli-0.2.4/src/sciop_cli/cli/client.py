from pathlib import Path
from typing import Any, Callable

import click
from pydantic import TypeAdapter
from rich import print as rprint

from sciop_cli.clients import BittorrentClientAdapter, ClientConfigs
from sciop_cli.config import get_config, set_config


def client_idx(f: Callable) -> Callable:
    f = click.option(
        "-c",
        "--client",
        type=int,
        help="Index of client config to use.",
        default=0,
        show_default=True,
    )(f)
    return f


@click.group("client")
def client() -> None:
    """
    Interact with a bittorrent client
    """


_available_clients = list(BittorrentClientAdapter.get_adapters().keys())


@client.command("login")
@click.option(
    "--client",
    type=click.Choice(_available_clients),
    prompt="Which type of client?",
    required=True,
)
@click.option("-u", "--username", prompt=True, help="Username", required=True)
@click.option("-p", "--password", prompt=True, hide_input=True, help="Password", required=True)
@click.option(
    "-h", "--host", prompt=True, help="Host (without protocol, like `localhost`)", required=True
)
@click.option("--port", prompt=True, help="Port", type=int, required=True)
def login(**kwargs: Any) -> None:
    adapter = TypeAdapter(ClientConfigs)
    client_config = adapter.validate_python(kwargs)
    cfg = get_config()
    cfg.clients.append(client_config)
    set_config(cfg)
    click.echo("Added new client configuration")
    rprint(client_config.model_dump())


@client.command("remove")
@click.option(
    "-c",
    "--client",
    type=int,
    help="Index of client config to remove.",
    default=0,
    show_default=True,
    confirmation_prompt=True,
)
def remove(client: int = 0) -> None:
    """Remove a client configuration by index"""
    cfg = get_config()
    client_cfg = cfg.clients.pop(client)
    set_config(cfg)
    click.echo("Removed client configuration")
    rprint(client_cfg.model_dump())


@client.command("list")
def list_configs() -> None:
    """List client configurations"""
    cfg = get_config()
    if len(cfg.clients) == 0:
        click.echo("No clients configured - use sciop-cli client login")
    else:
        rprint({i: client for i, client in enumerate(cfg.clients)})


@client.command("list-clients")
def list_clients() -> None:
    """List available bittorrent client adapters"""
    rprint(BittorrentClientAdapter.get_adapters())


@client.command("add")
@client_idx
@click.option(
    "-t",
    "--torrent",
    type=click.Path(exists=True),
    required=True,
    help="Path of a local torrent file to upload",
)
@click.option(
    "-p",
    "--path",
    type=click.Path(),
    required=True,
    help="Path to save downloaded data/check existing data",
)
def add_torrent(torrent: Path, path: Path, client: int = 0) -> None:
    """Add a new torrent to the client"""
    adapter = _get_adapter(client)
    torrent = Path(torrent)
    data_path = Path(path)
    adapter.add_torrent_file(torrent_path=torrent, data_path=data_path)


def _get_adapter(idx: int = 0) -> BittorrentClientAdapter:
    cfg = get_config()
    client_config = cfg.clients[idx]
    adapter = client_config.make_adapter()
    adapter.login()
    return adapter
