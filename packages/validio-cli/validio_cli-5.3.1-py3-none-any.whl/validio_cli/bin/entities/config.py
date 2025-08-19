from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import confirm
from tabulate import tabulate
from validio_sdk._api.api import APIClient
from validio_sdk.config import (
    Config,
    ConfigInvalidError,
    ConfigNotFoundError,
    ValidioConfig,
)
from validio_sdk.exception import _show_trace

import validio_cli
from validio_cli import (
    AsyncTyper,
    ConfigDir,
    OutputFormat,
    OutputFormatOption,
    output_json,
)

app = AsyncTyper(help="Configuration for the Validio CLI and SDK")


@app.async_command(help="Create or edit current credentials")
async def init(config_dir: str = ConfigDir) -> None:
    config_path = Path(config_dir) if config_dir is not None else None

    cfg = Config(config_path)
    create_type = "updated" if cfg.config_path.is_file() else "created"

    current_config = cfg.read() if cfg.config_path.is_file() else None

    print("Address to Validio, should start with 'https://' and usually have no path")
    print("Example: https://my-company.validio.io\n")

    while True:
        print("-" * 50)
        current_config = await _prompt_for_config(current_config)

        print()
        session: PromptSession = PromptSession()
        should_test_config = (
            await session.prompt_async(
                validio_cli._fixed_width("Test configuration? [Y/n]")
            )
        ).strip()

        if should_test_config and should_test_config.lower() != "y":
            break

        failure_reason = await _test_configuration(current_config)
        if failure_reason is None:
            break

        print(f"\n{failure_reason}\n")

    cfg.write(current_config)

    print(f"\n🎉 Configuration {create_type} successfully!")


@app.command(help="Set default namespace to target")
def ns(
    config_dir: str = ConfigDir,
    namespace: str = typer.Argument(
        "default",
        help="Set default namespace to target from CLI",
    ),
) -> None:
    set_default_namespace(namespace or "default", config_dir)


@app.command(help="List current configuration")
def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    show_secrets: bool = False,
) -> None:
    config_path = Path(config_dir) if config_dir is not None else None

    cfg = Config(config_path)
    try:
        validio_config = cfg.read()
    except ConfigNotFoundError:
        if confirm("🚫 No configuration found - do you want to create one?"):
            return init(config_dir)

        raise typer.Exit(code=1)
    except ConfigInvalidError:
        if confirm(
            "🚨 Configuration found, but is not valid - do you want to delete it and"
            " create a new one?"
        ):
            cfg.remove()
            return init(config_dir)

        raise typer.Exit(code=1)

    def _highlight_if_missing(value: Any) -> str:
        if not value:
            return "⚠️  \033[91m{}\033[0m".format("MISSING")

        return value

    settings = {
        "config_path": cfg.config_path,
        "default_namespace": validio_config.default_namespace,
        "endpoint": validio_config.endpoint,
        "access_key": validio_config.access_key,
        "access_secret": (
            validio_config._access_secret
            if show_secrets
            else validio_config.access_secret
        ),
    }

    if output_format == OutputFormat.JSON:
        return output_json(settings)

    table = [["KEY", "VALUE"]]

    for k, v in settings.items():
        table.append([k.capitalize().replace("_", " "), _highlight_if_missing(v)])

    print(tabulate(table, tablefmt="plain"))

    return None


def set_default_namespace(
    namespace: str, default_config_path: str | None = None
) -> None:
    config_path = Path(default_config_path) if default_config_path is not None else None
    cfg = Config(config_path)

    validio_config = cfg.read()
    validio_config.default_namespace = namespace

    cfg.write(validio_config)

    print(f"Default namespace set to '{namespace}'")


async def _prompt_for_config(current_config: ValidioConfig | None) -> ValidioConfig:
    if current_config is None:
        current_config = ValidioConfig()

    endpoint_completer = WordCompleter(["http://localhost:8889"])

    session: PromptSession = PromptSession()

    while True:
        validio_endpoint = (
            (
                await session.prompt_async(
                    validio_cli._fixed_width("Validio URL"),
                    completer=endpoint_completer,
                    default=current_config.endpoint,
                )
            )
            .strip()
            .strip("/")
        )

        current_config.endpoint = validio_endpoint

        try:
            result = urlparse(validio_endpoint)
            assert all([result.scheme, result.netloc])

            break
        except Exception:
            print("\nValidio URL must be a valid URL")

    while True:
        api_key = (
            await session.prompt_async(
                validio_cli._fixed_width("API access key ID"),
                default=current_config.access_key,
            )
        ).strip()

        current_config.access_key = api_key

        if api_key.startswith("APK_"):
            break

        print("\nAPI access key ID should start with 'APK_'")

    current_config.access_secret = (
        await session.prompt_async(
            validio_cli._fixed_width("API secret access key"),
            is_password=True,
            default=current_config._access_secret,
        )
    ).strip()

    return current_config


async def _test_configuration(config: ValidioConfig) -> str | None:
    vc = APIClient(config=config)

    try:
        await vc.test_connection()
    except Exception as e:
        if _show_trace():
            raise e

        return str(e)

    return None
