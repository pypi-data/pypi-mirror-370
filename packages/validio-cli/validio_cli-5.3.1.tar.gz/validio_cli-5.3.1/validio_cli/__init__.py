import asyncio
import contextlib
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from pathlib import Path
from types import EllipsisType
from typing import Any, TypeVar

import typer
from camel_converter import to_snake
from tabulate import tabulate
from validio_sdk import config
from validio_sdk._api.api import APIClient
from validio_sdk.config import Config, ValidioConfig
from validio_sdk.util import ClassJSONEncoder

F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T", bound="OutputSettings")

DEFAULT_NAMESPACE: str = "default"


class Role(str, Enum):
    """User roles."""

    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


class OutputFormat(str, Enum):
    """Available output formats for the CLI"""

    JSON = "json"
    TEXT = "text"


# Shared command line argument and flag types.
ConfigDir = typer.Option(
    config.default_config_dir,
    "--config-dir",
    "-c",
    help="Path to where config is stored",
)
OutputFormatOption = typer.Option(
    OutputFormat.TEXT.value, "--output", "-o", help="Output format"
)
Identifier = typer.Argument(
    default=None, help="Name or ID of the resource to get of this type"
)
RequiredIdentifier = typer.Argument(
    default=..., help="Name or ID of the resource to get of this type"
)
Identifiers = typer.Argument(
    default=None, help="Names or IDs of the sources to apply the command on"
)


# ruff: noqa: N802
# Let's use capital name to be consistent.
def Namespace(
    default: str | EllipsisType | None = None, help: str = "Namespace to target"
) -> Any:  # typer returns Any here
    """
    Create a namespace flag that defaults to optional with a short help
    text. Accepts a string, ellipsis or None and a help text.

    :param default: The default value (or ellipsis for required)
    :param help: Help text for the flag
    """
    return typer.Option(default, "--namespace", "-n", help=help)


class AsyncTyper(typer.Typer):
    """
    Async version of typer.

    Decorator to support running async functions with typer, will basically just
    wrap your function in `asyncio.run`
    """

    def async_command(self, *args: Any, **kwargs: Any) -> Callable:
        def decorator(async_func: F) -> F:
            @wraps(async_func)
            def sync_func(*_args: Any, **_kwargs: Any) -> None:
                return asyncio.run(async_func(*_args, **_kwargs))

            self.command(*args, **kwargs)(sync_func)
            return async_func

        return decorator


def get_client(
    config_dir: str = ConfigDir,
) -> tuple[APIClient, ValidioConfig]:
    cfg = Config(Path(config_dir)).read()
    return APIClient(config=cfg), cfg


@dataclass
class OutputSettings:
    attribute_name: str | None = None
    reformat: Callable[[Any], Any] | None = None
    pass_full_object: bool = False

    @classmethod
    def trimmed_upper_snake(cls: type[T], attribute_name: str | None, trim: str) -> T:
        return cls(
            attribute_name=attribute_name,
            reformat=lambda x: to_snake(x.removesuffix(trim)).upper(),
        )

    @classmethod
    def string_as_datetime(cls: type[T], attribute_name: str | None) -> T:
        format = "%Y-%m-%dT%H:%M:%S.%fZ"
        return cls(
            attribute_name=attribute_name,
            reformat=lambda x: datetime.strptime(x, format).replace(
                tzinfo=timezone.utc
            ),
        )


def output_json(obj: Any, identifier: str | None = None) -> None:
    # If we have an identifier we only want to display a single object so grab
    # the first index if object is not empty and is a list.
    if obj is not None and isinstance(obj, list) and identifier is not None:
        with contextlib.suppress(IndexError):
            obj = obj[0]

    j = json.dumps(obj, sort_keys=True, indent=2, cls=ClassJSONEncoder)
    print(j)


def format_text(items: Any, fields: dict[str, OutputSettings | None]) -> str:
    if items is None:
        items = []
    elif not isinstance(items, list):
        items = [items]

    table: list[list[str]] = [[k.upper().replace("_", " ") for k in fields]]

    for item in items:
        row = []
        for field_name, settings in fields.items():
            attribute_name = field_name
            if settings is not None and settings.attribute_name is not None:
                attribute_name = settings.attribute_name

            if settings and settings.pass_full_object and settings.reformat:
                row.append(settings.reformat(item))
                continue

            if isinstance(item, dict):
                value = item.get(attribute_name)
            elif hasattr(item, attribute_name):
                value = getattr(item, attribute_name)
            else:
                row.append("UNKNOWN")
                continue

            if settings is not None and settings.reformat is not None:
                value = settings.reformat(value)

            if isinstance(value, datetime):
                value = _format_relative_time(value)

            row.append(value)

        table.append(row)

    return tabulate(table, tablefmt="plain")


def output_text(items: Any, fields: dict[str, OutputSettings | None]) -> None:
    print(format_text(items=items, fields=fields))

    # We flush stdout here so we can avoid an unhandled broken pipe error.
    # Catching the exception according to the documentation at
    # https://docs.python.org/3/library/signal.html#note-on-sigpipe does not
    # work in this context. Generating a table with the same amount of data but
    # without iterating over the object (i.e. adding a static string) does not
    # cause this issue so it must be related to the content.
    #
    # This is important to allow piping to commands like `head` without getting
    # a message on stderr about unhandled exceptions for the broken pipe.
    # Internal ref: VR-2146
    sys.stdout.flush()


def output_ok_or_error(result: Any) -> None:
    status = "OK" if not result.get("errors") else "ERROR"

    return output_text(
        {"status": status},
        fields={
            "status": OutputSettings(pass_full_object=True, reformat=lambda _: status),
        },
    )


# ruff: noqa: PLR2004, PLR0911
def _format_relative_time(d: datetime) -> str:
    diff = datetime.now(timezone.utc) - d
    seconds = diff.seconds

    if diff.days < 0:
        return "0s"
    if diff.days >= 1:
        return f"{diff.days}d"
    if seconds <= 1:
        return "1s"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 120:
        return "1m"
    if seconds < 3600:
        return f"{int(seconds / 60)}m"
    if seconds < 7200:
        return "1h"

    return f"{int(seconds / 3600)}h"


def _single_resource_if_specified(items: list[Any], identifier: str | None) -> Any:
    if identifier is None:
        return items

    return next(
        (
            item
            for item in items
            if (hasattr(item, "resource_name") and item.resource_name == identifier)
            or (hasattr(item, "name") and item.name == identifier)
            or (hasattr(item, "id") and item.id == identifier)
            or (isinstance(item, dict) and item.get("resourceName") == identifier)
            or (isinstance(item, dict) and item.get("name") == identifier)
            or (isinstance(item, dict) and item.get("id") == identifier)
        ),
        None,
    )


def _resource_filter(
    resource: Any | None,
    field_path: list[str],
    value: str | None,
) -> bool:
    # If we don't have an object we don't want to filter it in.
    if resource is None:
        return False

    # If we don't have a value to filter for we don't want to filter it out.
    if value is None:
        return True

    # Traverse the object til the resource we need for filtering.
    for field in field_path:
        resource = resource.get(field)

        # If the object field value we need for filtering out is none we filter
        # it out.
        if resource is None:
            return False

    return value in [resource["id"], resource["resourceName"]]


def _fixed_width(message: str, width: int = 25) -> str:
    message = f"{message}: "
    return f"{message:<{width}} "
