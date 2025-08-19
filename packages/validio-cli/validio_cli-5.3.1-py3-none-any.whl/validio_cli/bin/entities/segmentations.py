import typer
from validio_sdk._api.api import APIClient
from validio_sdk.config import ValidioConfig
from validio_sdk.exception import ValidioError

import validio_cli
from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Identifier,
    Identifiers,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    get_client,
    output_json,
    output_ok_or_error,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Grouping of data for validation")


@app.async_command(help="List all Segmentations")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
    source: str = typer.Option(
        None, help="List Segmentations for this Source (ID or name)"
    ),
) -> None:
    if identifier and source:
        raise ValidioError("--identifier and --source can't be used together")

    vc, cfg = get_client(config_dir)

    segmentations = await vc.get_segmentations(
        segmentation_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    if source:
        if not isinstance(segmentations, list):
            raise ValidioError("failed to get segmentations")

        segmentations = [
            segmentation
            for segmentation in segmentations
            if segmentation is not None
            and validio_cli._resource_filter(segmentation, ["source"], source)
        ]

    if output_format == OutputFormat.JSON:
        return output_json(segmentations, identifier)

    return output_text(
        segmentations,
        fields={
            "name": OutputSettings(attribute_name="resourceName"),
            "source": OutputSettings(reformat=lambda source: source["resourceName"]),
            "age": OutputSettings.string_as_datetime(attribute_name="createdAt"),
        },
    )


@app.async_command(help="Delete segmentation")
async def delete(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    if not identifiers:
        raise ValidioError("no identifiers are provided")

    vc, cfg = get_client(config_dir)

    segmentation_ids = [
        segmentation_id
        for segmentation_id in [
            await get_segmentation_id(vc, cfg, identifier, namespace)
            for identifier in identifiers
        ]
        if segmentation_id
    ]

    result = await vc.delete_segmentations(segmentation_ids)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return output_ok_or_error(result)


async def get_segmentation_id(
    vc: APIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "segmentation"
    prefix = "SGM_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_segmentations(
        segmentation_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    if not isinstance(resource, dict):
        raise ValidioError("failed to get segmentation id")

    return resource["id"]


if __name__ == "__main__":
    typer.run(app())
