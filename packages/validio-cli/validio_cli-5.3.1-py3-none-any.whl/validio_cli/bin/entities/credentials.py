import typer
from validio_sdk._api.api import APIClient
from validio_sdk.config import ValidioConfig
from validio_sdk.exception import ValidioError

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Identifier,
    Identifiers,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    _single_resource_if_specified,
    get_client,
    output_json,
    output_ok_or_error,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Credentials used for Sources")


@app.async_command(help="Get credentials")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
) -> None:
    client, cfg = get_client(config_dir)

    credentials = await client.get_credentials(
        credential_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    # TODO(UI-2311): Fully support list/get/get_by_resource_name
    if isinstance(credentials, list):
        credentials = _single_resource_if_specified(credentials, identifier)

    if output_format == OutputFormat.JSON:
        return output_json(credentials, identifier)

    return output_text(
        credentials,
        fields={
            "name": OutputSettings(attribute_name="resourceName"),
            "type": OutputSettings.trimmed_upper_snake("__typename", "Credential"),
            "age": OutputSettings.string_as_datetime("createdAt"),
        },
    )


@app.async_command(help="Delete credential")
async def delete(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    if not identifiers:
        raise ValidioError("no identifiers are provided")

    vc, cfg = get_client(config_dir)

    credential_ids = [
        credential_id
        for credential_id in [
            await get_credential_id(vc, cfg, identifier, namespace)
            for identifier in identifiers
        ]
        if credential_id
    ]

    sources = await vc.get_sources(namespace_id=namespace)
    if not isinstance(sources, list):
        raise ValidioError("failed to get sources")

    credentials_with_sources = {
        s["credential"]["resourceName"]
        for s in sources
        if s["credential"]["id"] in credential_ids
    }
    if len(credentials_with_sources) > 0:
        raise ValidioError(
            "Following credentials are connected to sources:\n"
            + "\n".join(credentials_with_sources)
        )

    result = await vc.delete_credentials(credential_ids)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return output_ok_or_error(result)


async def get_credential_id(
    vc: APIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "credential"
    prefix = "CRD_"

    if not identifier:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    # TODO: UI-1957 - Get a single resource by name
    all_credentials = await vc.get_credentials(
        namespace_id=get_namespace(namespace, cfg)
    )

    if not isinstance(all_credentials, list):
        raise ValidioError("failed to get credentials")

    resolved_id = next(
        (
            credential["id"]
            for credential in all_credentials
            if credential["resourceName"] == identifier
        ),
        None,
    )

    if resolved_id is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    return resolved_id


if __name__ == "__main__":
    typer.run(app())
