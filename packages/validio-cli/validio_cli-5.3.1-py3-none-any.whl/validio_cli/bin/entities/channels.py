import typer
from camel_converter import to_snake
from validio_sdk.exception import ValidioError

from validio_cli import (
    APIClient,
    AsyncTyper,
    ConfigDir,
    Identifier,
    Identifiers,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    ValidioConfig,
    _single_resource_if_specified,
    get_client,
    output_json,
    output_ok_or_error,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Channels used for notifications")


@app.async_command(help="Get channels")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
) -> None:
    client, cfg = get_client(config_dir)

    channels = await client.get_channels(
        channel_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    # TODO(UI-2311): Fully support list/get/get_by_resource_name
    if isinstance(channels, list):
        channels = _single_resource_if_specified(channels, identifier)

    if output_format == OutputFormat.JSON:
        return output_json(channels, identifier)

    return output_text(
        channels,
        fields={
            "name": OutputSettings(attribute_name="resourceName"),
            "type": OutputSettings(
                attribute_name="__typename",
                reformat=lambda x: to_snake(x.removesuffix("Channel")).upper(),
            ),
            "age": OutputSettings.string_as_datetime("createdAt"),
        },
    )


@app.async_command(help="Delete channel")
async def delete(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    if not identifiers:
        raise ValidioError("no identifiers are provided")

    vc, cfg = get_client(config_dir)

    channel_ids = [
        channel_id
        for channel_id in [
            await get_channel_id(vc, cfg, identifier, namespace)
            for identifier in identifiers
        ]
        if channel_id
    ]

    result = await vc.delete_channels(channel_ids)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return output_ok_or_error(result)


async def get_channel_id(
    vc: APIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "channel"
    prefix = "CNL_"

    if not identifier:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_channels(
        channel_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    if not isinstance(resource, dict):
        raise ValidioError("failed to get channel id")

    return resource["id"]


if __name__ == "__main__":
    typer.run(app())
