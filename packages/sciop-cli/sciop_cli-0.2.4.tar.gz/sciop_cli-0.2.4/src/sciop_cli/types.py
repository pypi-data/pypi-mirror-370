from copy import copy
from logging import getLogger
from typing import Annotated, Any, TypeAlias, cast
from typing import Callable as C

import humanize
import keyring
from pydantic import (
    AfterValidator,
    SecretStr,
    SerializationInfo,
    ValidationInfo,
    WrapSerializer,
)


def _divisible_by_16kib(size: int) -> bool:
    if size < 0:
        return False
    return size % (16 * (2**10)) == 0


def _validate_size(size: int) -> int:
    assert _divisible_by_16kib(size), "Piece size must be divisible by 16kib and positive"
    return size


PieceSize = Annotated[int, AfterValidator(_validate_size)]


class Size(int):
    def __str__(self) -> str:
        return humanize.naturalsize(int(self), binary=True)

    def __rmul__(self, factor: int) -> "Size":
        return Size(int(self) * factor)

    def __mul__(self, other: int) -> "Size":
        return Size(int(self) * other)


_password_prefix: str = "sciop_cli"


def KeychainSecretStr(  # noqa: N802
    key_fields: tuple[str, ...] | None = None, user_field: str = "username"
) -> type[SecretStr] | None:
    """
    (functional) type for getting/setting passwords from a keychain.

    Uses other fields in the model to provide unique keys in the keychain.

    Each key is stored in a service name like

    ```
    "sciop_cli.{data[key_fields[0]}}.{data[key_fields[1]]}..."
    ```

    so, e.g. if one were to want to store multiple of the same username field for
    e.g. a bittorrent client,
    you could save the passwords with a key that included the uri of the client like

    ```
    KeychainSecretStr(("client", "uri"))
    ```

    to get something like

    ```
    "sciop_cli.qbittorrent.localhost:8080"
    ```

    The `user_field` key works similarly -
    by default expecting some username to be stored in the `username` field.

    When serializing, treated like a normal SecretStr,
    except if `"update_keyring"` is provided in the serialization context,
    then we attempt to save the password to the keyring.
    Since serialization doesn't have access to the model info,
    we do this by storing the keys, usernames, and passwords in the function closure
    and updating any that need to be.

    !!! note

        This is a sorta busted type, this should be fixed, but we need to be able to
        access the model data during serialization to do so.
        for now we are just telling mypy to ignore this type, but that's a pretty bad solution.

        See: https://github.com/pydantic/pydantic/issues/12017


    Args:
        key_fields (tuple[str] | None): fields to fetch from the rest of the model
            to make passwords unique. See docstring for usage.
        user_field (str): the field that has the username, (usually just "username").

    Returns:
        type[SecretStr | None]
    """
    _keychain_trips: set[tuple[str, str, str]] = set()

    def service_key(data: dict[str, Any]) -> str:
        key = copy(_password_prefix)
        if not key_fields:
            return key

        for field in key_fields:
            if field in data:
                key = ".".join([key, str(data[field])])
        return key

    def password_from_keychain(value: SecretStr | None, info: ValidationInfo) -> SecretStr | None:
        """Try to get a password from keychain, if not provided"""
        nonlocal _keychain_trips
        username = str(info.data[user_field])
        key = service_key(info.data)

        try:
            if not value and username:
                maybe_password = keyring.get_password(key, username)
                if maybe_password:
                    value = SecretStr(maybe_password)
        except Exception:
            # e.g. no supported keyring backends available
            pass

        if value:
            _keychain_trips.add((key, username, value.get_secret_value()))
        return value

    def password_to_keychain(
        value: SecretStr | None, handler: C[[SecretStr | None], str | None], info: SerializationInfo
    ) -> str | SecretStr | None:
        if not value:
            return handler(value)
        if info.context and info.context.get("update_keyring"):
            nonlocal _keychain_trips
            logger = getLogger("sciop_cli.config")
            # use the triples stored during validation to update

            try:
                for key, username, password in _keychain_trips:
                    existing = keyring.get_password(key, username)
                    if existing is None or existing != password:
                        keyring.set_password(key, username, password)
                return None
            except Exception as e:
                logger.warning(
                    "Password present, but could not save in keyring. "
                    "Dumping in plaintext, which is insecure!\n"
                    f"Got exception: {e}"
                )
                return value.get_secret_value()
        else:
            return handler(value)

    type_ = Annotated[
        SecretStr | None,
        AfterValidator(password_from_keychain),
        WrapSerializer(password_to_keychain),
    ]
    # mypy fuckery because Annotated types are a special form
    cast_type_ = cast(type[SecretStr] | None, type_)
    return cast_type_


def _unsecret_when_configuring(
    value: SecretStr | None, handler: C[[SecretStr | None], str | None], info: SerializationInfo
) -> str | SecretStr | None:
    if not value:
        return handler(value)
    elif info.context and info.context.get("update_keyring"):
        return value.get_secret_value()
    else:
        return handler(value)


TokenSecretStr: TypeAlias = Annotated[SecretStr | None, WrapSerializer(_unsecret_when_configuring)]
"""
Type for an authorization token to be stored along with a password.
When `update_keyring` is provided in the serialization context, return as a plain string,
as when we are called from set_config
"""
