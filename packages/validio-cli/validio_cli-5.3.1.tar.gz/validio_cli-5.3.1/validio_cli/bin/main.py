import os
import shutil
import sys
from typing import Optional

import typer
import validio_sdk.metadata
from tabulate import tabulate
from validio_sdk import ValidioError
from validio_sdk.config import Config

import validio_cli.metadata
from validio_cli.bin.entities import (
    channels,
    code,
    config,
    credentials,
    dbt,
    filters,
    incidents,
    metrics,
    namespaces,
    notification_rules,
    resources,
    segmentations,
    segments,
    sources,
    users,
    validators,
    windows,
)

app = typer.Typer(
    help="Validio CLI tool",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    rich_markup_mode="rich",
)

app.add_typer(channels.app, no_args_is_help=True, name="channels")
app.add_typer(code.app, no_args_is_help=True, name="code")
app.add_typer(config.app, no_args_is_help=True, name="config")
app.add_typer(credentials.app, no_args_is_help=True, name="credentials")
app.add_typer(dbt.app, no_args_is_help=True, name="dbt")
app.add_typer(filters.app, no_args_is_help=True, name="filters")
app.add_typer(incidents.app, no_args_is_help=True, name="incidents")
app.add_typer(metrics.app, no_args_is_help=True, name="metrics")
app.add_typer(namespaces.app, no_args_is_help=True, name="namespaces")
app.add_typer(resources.app, no_args_is_help=True, name="resources")
app.add_typer(notification_rules.app, no_args_is_help=True, name="notification-rules")
app.add_typer(segmentations.app, no_args_is_help=True, name="segmentations")
app.add_typer(segments.app, no_args_is_help=True, name="segments")
app.add_typer(sources.app, no_args_is_help=True, name="sources")
app.add_typer(users.app, no_args_is_help=True, name="users")
app.add_typer(validators.app, no_args_is_help=True, name="validators")
app.add_typer(windows.app, no_args_is_help=True, name="windows")


@app.command(help="Show current version")
def version() -> None:
    print(
        tabulate(
            [
                ["SDK version", validio_sdk.metadata.version()],
                ["CLI version", validio_cli.metadata.version()],
            ],
            tablefmt="plain",
        )
    )


@app.command(
    add_help_option=False,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def plugins(
    ctx: typer.Context,
    # We need to keep this for typer
    # ruff: noqa: UP007
    plugin: Optional[str] = typer.Argument(
        None,
        help="Plugin to run. Leave empty to list available plugins.",
    ),
) -> None:
    """
    Run plugin.

    This works similar to `git` in that any executable prefixed with `validio-`
    will be executed through this CLI without the prefix. That means that if you
    have an executable somewhere in your `PATH` named `validio-my-app` you can
    invoke that by running `validio plugin my-app`.

    Any additional arguments will be passed to your plugin so you can run
    `validio plugin my-app --arg1 --arg2`.
    """
    # We allow plugin as None since we want to show all available plugins when
    # this part is
    if plugin is None:
        _list_executables()
        return

    # Since we want to allow passing any argument to plugins we accept extra
    # unknown arguments and remove the `--help` flag so it can be passed to the
    # plugin. However, if the _only_ argument passed (i.e. the `plugin`) is help
    # we assume that the user wants help about the `plugin` subcommand.
    if plugin in ["-h", "--help"]:
        typer.echo(ctx.get_help())
        return

    plugin_path = shutil.which(f"validio-{plugin}")
    if not plugin_path:
        raise ValidioError(f"Unknown plugin {plugin}")

    cfg = Config(None)
    validio_cfg = cfg.read()

    os.execve(
        plugin_path,
        [plugin_path] + sys.argv[3:],
        # If someone wants to write a plugin with tooling that doesn't have an
        # SDK we kindly pass the credentials to the environment so you can
        # easily call Validio anyway.
        {
            **os.environ.copy(),
            "VALIDIO_CONFIG_PATH": str(cfg.config_path.parent),
            "VALIDIO_ENDPOINT": validio_cfg.endpoint,
            "VALIDIO_ACCESS_KEY_ENV": validio_cfg.access_key,
            "VALIDIO_SECRET_ACCESS_KEY_ENV": validio_cfg._access_secret,
        },
    )


def _list_executables() -> None:
    paths = os.environ.get("PATH", "").split(":")

    executables = set()
    for path in paths:
        try:
            executables.update(
                {
                    filename.lstrip("validio-")
                    for filename in os.listdir(path)
                    if filename.startswith("validio-")
                }
            )
        except FileNotFoundError:
            continue

    if not executables:
        print("No plugins found")
        return

    print(
        tabulate(
            [[executable] for executable in sorted(executables)],
            tablefmt="plain",
            headers=["PLUGIN NAME"],
        )
    )


def main() -> None:
    exit_code = 1

    try:
        app()
        exit_code = 0

    # If the pipe is broken we can't print more so just return asap.
    except BrokenPipeError:
        return

    # ValidioErrors are thrown by us and should not require the stack trace
    # to tell what went wrong.
    # GraphQL errors doesn't contain any valuable information in the trace, we
    # only want to print the error message.
    except ValidioError as e:
        print(f"Something went wrong: {e}")

    # For the other errors check if they're known children.
    except Exception as e:
        if issubclass(type(e), ValidioError):
            print(f"Something went wrong: {e}")
        else:
            raise e

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
