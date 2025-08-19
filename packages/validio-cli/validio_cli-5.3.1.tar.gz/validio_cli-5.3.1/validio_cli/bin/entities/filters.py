import typer
from validio_sdk.exception import ValidioError

import validio_cli
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
    get_client,
    output_json,
    output_ok_or_error,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Filters on sources")


@app.async_command(help="List filters")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
    source: str = typer.Option(None, help="List filters for this source (ID or name)"),
) -> None:
    if identifier and source:
        raise ValidioError("--source can't be used together with an identifier")

    vc, cfg = get_client(config_dir)

    filters = await vc.get_filters(
        filter_id=identifier, namespace_id=get_namespace(namespace, cfg)
    )

    if source:
        if not isinstance(filters, list):
            raise ValidioError("failed to get filters")

        filters = [
            f
            for f in filters
            if f is not None and validio_cli._resource_filter(f, ["source"], source)
        ]

    if output_format == OutputFormat.JSON:
        return output_json(filters, identifier)

    return output_text(
        filters,
        fields={
            "name": OutputSettings(attribute_name="resourceName"),
            "source": OutputSettings(reformat=lambda source: source["resourceName"]),
            "type": OutputSettings(
                attribute_name="__typename",
            ),
            "age": OutputSettings.string_as_datetime(attribute_name="createdAt"),
        },
    )


@app.async_command(help="Delete filter")
async def delete(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    if not identifiers:
        raise ValidioError("no identifiers are provided")

    vc, cfg = get_client(config_dir)

    filter_ids = [
        filter_id
        for filter_id in [
            await get_filter_id(vc, cfg, identifier, namespace)
            for identifier in identifiers
        ]
        if filter_id
    ]

    result = await vc.delete_filters(filter_ids)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return output_ok_or_error(result)


async def get_filter_id(
    vc: APIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "filter"
    prefix = "FTR_"

    if not identifier:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_filters(
        filter_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    if not isinstance(resource, dict):
        raise ValidioError("failed to get filter id")

    return resource["id"]


if __name__ == "__main__":
    typer.run(app())
