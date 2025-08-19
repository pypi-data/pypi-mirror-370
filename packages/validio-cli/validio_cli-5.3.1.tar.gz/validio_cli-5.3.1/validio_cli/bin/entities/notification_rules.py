import typer
from camel_converter import to_snake
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

app = AsyncTyper(help="Notification rules for incidents")


@app.async_command(help="Get notification rules")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
) -> None:
    vc, cfg = get_client(config_dir)

    notification_rules = await vc.get_notification_rules(
        notification_rule_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    # TODO(UI-2311): Fully support list/get/get_by_resource_name
    if isinstance(notification_rules, list):
        notification_rules = _single_resource_if_specified(
            notification_rules, identifier
        )

    if output_format == OutputFormat.JSON:
        return output_json(notification_rules, identifier)

    return output_text(
        notification_rules,
        fields={
            "name": OutputSettings(attribute_name="resourceName"),
            "channel": OutputSettings(reformat=lambda x: x["resourceName"]),
            "type": OutputSettings(
                attribute_name="channel",
                reformat=lambda x: to_snake(
                    x["__typename"].removesuffix("Channel")
                ).upper(),
            ),
            "age": OutputSettings.string_as_datetime(attribute_name="createdAt"),
        },
    )


@app.async_command(help="Delete notification rule")
async def delete(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    if not identifiers:
        raise ValidioError("no identifiers are provided")

    vc, cfg = get_client(config_dir)

    notification_rule_ids = [
        notification_rule_id
        for notification_rule_id in [
            await get_notification_rule_id(vc, cfg, identifier, namespace)
            for identifier in identifiers
        ]
        if notification_rule_id
    ]

    result = await vc.delete_notification_rules(notification_rule_ids)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return output_ok_or_error(result)


async def get_notification_rule_id(
    vc: APIClient, cfg: ValidioConfig, identifier: str, namespace: str
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "notification rule"
    prefix = "NRL_"

    if not identifier:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await vc.get_notification_rules(
        notification_rule_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    if not isinstance(resource, dict):
        raise ValidioError("failed to get notification rule id")

    return resource["id"]


if __name__ == "__main__":
    typer.run(app())
