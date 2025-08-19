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
from validio_cli.bin.entities.sources import get_source_id
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Validators monitor the data from your sources")


@app.async_command(help="Get Validators")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
    source: str = typer.Option(
        None, help="List Validators for this Source (name or ID)"
    ),
    window: str = typer.Option(
        None, help="List Validators for this Window (name or ID)"
    ),
    segmentation: str = typer.Option(
        None, help="List Validators for this Segmentation (name or ID)"
    ),
) -> None:
    vc, cfg = get_client(config_dir)

    source_id = await get_source_id(vc, cfg, source, namespace) if source else None

    validators = await vc.get_validators(
        validator_id=identifier,
        source_id=source_id,
        namespace_id=get_namespace(namespace, cfg),
    )

    if isinstance(validators, list):
        validators = [
            validator
            for validator in validators
            if validio_cli._resource_filter(
                validator, ["sourceConfig", "source"], source
            )
            and validio_cli._resource_filter(
                validator, ["sourceConfig", "window"], window
            )
            and validio_cli._resource_filter(
                validator, ["sourceConfig", "segmentation"], segmentation
            )
        ]

    if output_format == OutputFormat.JSON:
        return output_json(validators, identifier)

    return output_text(
        validators,
        fields={
            "name": OutputSettings(attribute_name="resourceName"),
            "type": OutputSettings.trimmed_upper_snake("__typename", "Validator"),
            "age": OutputSettings.string_as_datetime(attribute_name="createdAt"),
        },
    )


@app.async_command(help="Delete validator")
async def delete(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    if not identifiers:
        raise ValidioError("no identifiers are provided")

    vc, cfg = get_client(config_dir)

    validator_ids = [
        validator_id
        for validator_id in [
            await get_validator_id(vc, cfg, identifier, namespace)
            for identifier in identifiers
        ]
        if validator_id
    ]

    result = await vc.delete_validators(validator_ids)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return output_ok_or_error(result)


async def get_validator_id(
    vc: APIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "validator"
    prefix = "MTR_"

    if not identifier:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_validators(
        validator_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    if not isinstance(resource, dict):
        raise ValidioError("failed to get validator id")

    return resource["id"]


if __name__ == "__main__":
    app()
