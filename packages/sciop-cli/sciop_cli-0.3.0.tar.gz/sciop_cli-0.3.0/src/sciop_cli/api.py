"""
Code to work with the sciop API :)
"""

from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal, TypedDict, cast
from urllib.parse import urljoin

import requests
from pydantic import SecretStr

from sciop_cli.config import Config, get_config, set_config
from sciop_cli.models import DatasetClaim, Token, TorrentFile, Upload

HTTP_METHOD = Literal["GET", "POST", "PUT", "DELETE"]
USER_AGENT = f"sciop-cli ({version('sciop-cli')})"

DefaultHeaders = TypedDict("DefaultHeaders", {"Authorization": str, "User-Agent": str}, total=False)


def path_or_str(value: Path | str) -> str:
    """
    handle args that can either be contained in a path or passed as a string
    """
    if isinstance(value, Path):
        return value.read_text()
    try:
        path = Path(value)
    except Exception:
        return value

    if path.exists():
        return path.read_text()
    else:
        return str(value)


def api_call(
    path: str,
    data: dict | None = None,
    method: HTTP_METHOD = "POST",
    data_encoding: Literal["form", "json"] = "json",
    headers: dict | None = None,
    files: dict | None = None,
    instance_url: str | None = None,
    api_prefix: Literal["/api/v1", False] = "/api/v1",
    autorefresh_token: bool = True,
    timeout: float | None = None,
    do_raise: bool = True,
) -> requests.Response:
    """
    Generic request wrapper around sciop API requests.

    Args:
        path (str): The path beneath the instance url to call.
            Includes the `api_prefix` by default,
            and handles leading `/`'s with [urljoin][urllib.parse.urljoin]
            so e.g. one can just use `"login"` to call `{instance_url}/api/v1/login`.
        data (dict | None): The data to send in a POST request.
        method (HTTP_METHOD): The HTTP method to use.
        headers (dict | None): Extra headers to add to a request.
            These override and are merged with the default headers from
            [default_headers][sciop_cli.api.default_headers].
        files (dict | None): Extra files to send in a POST request.
        data_encoding (Literal["form", "json"]): If `json`, use request's `json=` parameter,
            which sets `Content-Type`. If `form`, use `data=`, which defaults to formencoded data.
        instance_url (str): Instance url to call to. Default is https://sciop.net
        api_prefix (str): API prefix after the `instance_url`,
            either `/api/v1` or `False` to access paths at the base url.
        autorefresh_token (bool): If `True` (default), try and get a token if we have credentials.
            Made `False` e.g. to avoid infinite recursion while logging in,
            or if it is otherwise desirable to use only the preconfigured token.
        timeout (float): Explicit request timeout. If `None`, use config.request_timeout
        do_raise (bool): If `True` (default), raise on status codes >=400
    """
    config = get_config()
    request_kwargs = _api_call_kwargs(
        path=path,
        config=config,
        data=data,
        method=method,
        data_encoding=data_encoding,
        headers=headers,
        files=files,
        instance_url=instance_url,
        api_prefix=api_prefix,
        autorefresh_token=autorefresh_token,
        timeout=timeout,
    )

    res = requests.request(**request_kwargs)
    if res.status_code in (401, 403) and config.token and autorefresh_token:
        # try once to get a new token if it just expired
        token = get_token(force=True)
        request_kwargs["headers"]["Authorization"] = f"Bearer {token}"
        res = requests.request(**request_kwargs)

    if do_raise:
        res.raise_for_status()
    return res


def _api_call_kwargs(
    path: str,
    config: Config,
    data: dict | None = None,
    method: HTTP_METHOD = "POST",
    data_encoding: Literal["form", "json"] = "json",
    headers: dict | None = None,
    files: dict | None = None,
    instance_url: str | None = None,
    api_prefix: Literal["/api/v1", False] = "/api/v1",
    autorefresh_token: bool = True,
    timeout: float | None = None,
) -> dict:
    default = default_headers(
        instance_url=instance_url, headers=headers, autorefresh_token=autorefresh_token
    )
    merged_headers = default | headers if headers else default

    if instance_url is None:
        instance_url = config.instance_url

    if api_prefix:
        path = "/".join([segment.strip("/") for segment in [api_prefix, path]])

    url = urljoin(instance_url, path)
    request_kwargs = {
        "method": method,
        "url": url,
        "headers": merged_headers,
        "timeout": timeout if timeout else config.request_timeout,
        "files": files,
    }
    if data:
        if data_encoding == "form":
            request_kwargs["data"] = data
        elif data_encoding == "json":
            request_kwargs["json"] = data
        else:
            raise ValueError(f"data_encoding must be form or json, got {data_encoding}")
    return request_kwargs


def default_headers(autorefresh_token: bool = True, **kwargs: Any) -> DefaultHeaders:
    token = get_token(autorefresh_token=autorefresh_token, **kwargs)
    headers: DefaultHeaders = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def login(username: str, password: str, save: bool = True, **kwargs: Any) -> str:
    """
    Get a token from the API with a username and password and saves all three to the local config.

    Args:
        save (bool): If ``True``, save username, password, and token to the local yaml config.
            ``False`` to just get the token without persisting anything
        **kwargs: passed to [api_call][sciop_cli.api.api_call]
    """
    res = api_call(
        "login", data={"username": username, "password": password}, data_encoding="form", **kwargs
    )
    token_dict: Token = res.json()
    token = token_dict["access_token"]
    if save:
        cfg = get_config()
        cfg.username = username
        cfg.password = SecretStr(password)
        cfg.token = SecretStr(token)
        set_config(cfg)
    return token


def get_token(
    username: str | None = None,
    password: str | None = None,
    force: bool = False,
    autorefresh_token: bool = True,
    **kwargs: Any,
) -> str | None:
    """
    Get a token from passed username/password or from config.

    Reuses the already-existing token if present.
    Sets the username, password (if passed) and received token if we get a new one.

    Args:
        username (str): Username. If None (default),
            use from [get_config][sciop_cli.config.get_config].
            Must be used with `password`
        password (str): Password. If None (default),
            use from [get_config][sciop_cli.config.get_config].
        force (bool): If True, get a new token from the instance,
            even if one is stored in the config.
        **kwargs: passed to [api_call][sciop_cli.api.api_call] if a login request is made

    Returns:
        str: if token present
        None: if no username/password has been given.
    """
    config = get_config()
    if config.token and not force:
        return config.token.get_secret_value()

    if not username and config.username:
        username = config.username
    if not password and config.password:
        password = config.password.get_secret_value()

    if username and password and autorefresh_token:
        token = login(username=username, password=password, autorefresh_token=False, **kwargs)
        return token
    else:
        return None


def claim_next(dataset: str) -> DatasetClaim | None:
    res = api_call(f"claims/datasets/{dataset}/next", do_raise=False)
    if res.status_code == 404 and "no unclaimed" in res.text.lower():
        return None
    res.raise_for_status()
    claim = cast(DatasetClaim, res.json())
    return DatasetClaim(**claim)


def upload_torrent(path: Path, timeout: float | None = None) -> TorrentFile:
    if timeout is None:
        timeout = get_config().upload_timeout
    with open(path, "rb") as f:
        response = api_call("torrents", files={"file": f}, timeout=timeout)
    tf = cast(TorrentFile, response.json())
    return TorrentFile(**tf)


def create_upload(
    dataset: str,
    dataset_parts: list[str] | None = None,
    torrent_path: Path | None = None,
    infohash: str | None = None,
    method: str | Path | None = None,
    description: str | Path | None = None,
    timeout: float | None = None,
) -> Upload:
    """
    Create an upload for a dataset or dataset parts.

    Must pass either a path to an existing .torrent file, or an infohash of a torrent
    that has already been uploaded to the configured sciop instance.

    Args:
        dataset (str): Slug of the dataset to upload to
        torrent_path (Path): Path to the .torrent file to upload - pass either this or `infohash`
        infohash (str): Infohash of a torrent that has already been uploaded -
            pass either this or `torrent_path`
        method (str | Path | None): A description of how this upload was created,
            Supports markdown as a path or string.
        description (str | Path | None): Any description of the contents of the upload
            that are not contained within the dataset description, e.g. additional structure,
            if this is some sub-component of a dataset, and so on
        timeout (float | None): Timeout in seconds to wait for the upload to complete.
            If `None`, use Config.upload_timeout
    """
    if torrent_path and infohash or not (torrent_path or infohash):
        raise ValueError("Must pass torrent path OR infohash")
    elif torrent_path:
        tf = upload_torrent(path=torrent_path, timeout=timeout)
        infohash = tf["v1_infohash"] if tf["version"] == "v1" else tf["v2_infohash"]

    if timeout is None:
        timeout = get_config().upload_timeout

    kwargs: dict[str, str | list[str] | None] = {
        "infohash": infohash,
        "dataset_slug": dataset,
    }

    if method:
        kwargs["method"] = path_or_str(method)
    if description:
        kwargs["description"] = path_or_str(description)
    if dataset_parts:
        kwargs["part_slugs"] = dataset_parts

    res = api_call("uploads", data=kwargs, timeout=timeout)
    ul = cast(Upload, res.json())
    return Upload(**ul)
