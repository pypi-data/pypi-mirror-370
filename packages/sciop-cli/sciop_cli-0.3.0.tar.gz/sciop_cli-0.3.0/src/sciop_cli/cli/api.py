import json as json_
from pathlib import Path

import click
from rich import print as pprint
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from sciop_cli.api import claim_next as claim_next_api
from sciop_cli.api import create_upload
from sciop_cli.api import login as api_login


@click.command("login")
@click.option("-u", "--username", prompt=True, help="Username", required=True)
@click.option("-p", "--password", prompt=True, hide_input=True, help="Password", required=True)
@click.option("-i", "--instance-url", help="Instance to log in to, if None, sciop.net")
def login(username: str, password: str, instance_url: str | None = None) -> None:
    """
    Login to sciop.net (or another instance), storing the password in a keyring
    and getting a token
    """
    api_login(username, password, instance_url=instance_url)
    click.echo(f"Logged in as {username} ;)")


@click.command("upload")
@click.option("-d", "--dataset", help="Slug of the target dataset", required=True)
@click.option(
    "-p",
    "--part",
    help="Slug of the part, or parts for the upload (optional)."
    "Can be used multiple times to upload to multiple dataset parts",
    multiple=True,
)
@click.option(
    "-t",
    "--torrent",
    help="Path to the torrent file to upload",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
)
@click.option(
    "-i",
    "--infohash",
    help="If no path is passed, an infohash of an already-uploaded torrent",
    required=False,
    default=None,
)
@click.option(
    "--method",
    help="A description of how this upload was created. Supports markdown as a path or string.",
)
@click.option(
    "--description",
    help="Any description of the contents of the upload that are not contained within "
    "the dataset description, "
    "e.g. additional structure, if this is some sub-component of a dataset, and so on. "
    "Supports markdown as a path or string.",
)
def upload(
    dataset: str,
    part: list[str] | None = None,
    torrent: Path | None = None,
    infohash: str | None = None,
    method: str | None = None,
    description: str | None = None,
) -> None:
    """
    Create an upload for a dataset or dataset parts.

    Must pass either a path to an existing .torrent file, or an infohash of a torrent
    that has already been uploaded to the configured sciop instance.
    """
    progress = Progress(SpinnerColumn(), TimeElapsedColumn(), TextColumn("{task.description}"))
    with progress:
        progress.add_task(description="Uploading torrent...", total=None)
        upload = create_upload(
            dataset=dataset,
            dataset_parts=part,
            torrent_path=torrent,
            infohash=infohash,
            method=method,
            description=description,
        )
    pprint(upload)


@click.group("claims")
def claims() -> None:
    """Claims that we are scraping some data as part of a Quest :)"""
    pass


@claims.command("next")
@click.option("-d", "--dataset", required=True, help="Dataset to claim (as its slug)")
@click.option("-j", "--json", is_flag=True, default=False, help="Print response as json to stdout")
def next_claim(dataset: str, json: bool = False) -> None:
    """
    Get the next unclaimed, un-uploaded dataset part for a dataset, printing it
    """
    res = claim_next_api(dataset)
    if json:
        click.echo(json_.dumps(res))
    else:
        click.echo(res)
