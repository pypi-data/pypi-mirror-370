import json
import pathlib
from typing import cast

import typer
from validio_sdk import ValidioError
from validio_sdk._api.api import APIClient
from validio_sdk.resource._resource import DiffContext, Resource
from validio_sdk.resource._update_namespace import (
    ResourceNamesToMove,
    apply_move,
    get_resources_to_move,
)

from validio_cli import AsyncTyper, ConfigDir, Namespace, get_client
from validio_cli.components import BETA_BANNER, proceed_with_operation

app = AsyncTyper(help="Manage resources")


@app.async_command(help=f"{BETA_BANNER} Move resources from one namespace to another")
# ruff: noqa:  PLR0912
async def move(
    config_dir: str = ConfigDir,
    auto_approve: bool = typer.Option(
        False, help="Automatically approve and perform the move operation"
    ),
    namespace: str = Namespace(
        ..., help="Namespace where the resources currently reside"
    ),
    target_namespace: str = typer.Option(
        ..., "--target-namespace", help="Namespace to move the resources to"
    ),
    credential: list[str] = typer.Option(
        [], help="Credential resources to move to the target namespace"
    ),
    channel: list[str] = typer.Option(
        [], help="Channel resources to move to the target namespace"
    ),
) -> None:
    resource_names = ResourceNamesToMove(
        credentials=set(credential), channels=set(channel)
    )

    client, _ = get_client(config_dir)

    num_resources = await do_move(
        client=client,
        namespace=namespace,
        target_namespace=target_namespace,
        resource_names=resource_names,
        auto_approve=auto_approve,
    )

    if num_resources is not None and num_resources > 0:
        print(f"Apply complete! Resources: {num_resources} moved")


async def do_move(
    client: APIClient,
    namespace: str,
    target_namespace: str,
    resource_names: ResourceNamesToMove,
    auto_approve: bool,
) -> int | None:
    if namespace == target_namespace:
        raise ValidioError("target namespace should be different from source namespace")

    resources_to_move = await get_resources_to_move(
        namespace=namespace,
        client=client,
        resource_names=resource_names,
    )

    if resources_to_move.is_empty():
        print("No resources found to move")
        return 0

    print()
    num_resources = 0
    entries = [
        ("Credential", cast(dict[str, Resource], resources_to_move.credentials)),
        ("Channel", cast(dict[str, Resource], resources_to_move.channels)),
    ]
    for resource_type, rs in entries:
        for name, r in rs.items():
            num_resources += 1
            print(f"{r.__class__.__name__} {name} will be moved")

    print(
        "\n",
        f"Plan: {num_resources} resources will be moved "
        f"(together with their child resources) "
        f"from namespace '{namespace}' to namespace '{target_namespace}'",
    )

    if not await proceed_with_operation(auto_approve):
        return None

    print()
    print("Applying..")

    await apply_move(
        namespace=namespace,
        client=client,
        new_namespace=target_namespace,
        resources_to_move=resources_to_move,
    )

    return num_resources


def _read_resource_file(file: pathlib.Path) -> dict:
    if not file.is_file():
        raise ValidioError(f"'{file.absolute()}' is not a file")

    obj = json.loads(file.read_text())
    if not isinstance(obj, dict):
        raise ValidioError(f"expected json object in resource file: got {type(obj)}")

    if "resources" not in obj:
        raise ValidioError("json object in file should contain a 'resources' key")

    resources_obj_raw = obj["resources"]
    if not isinstance(resources_obj_raw, dict):
        raise ValidioError(
            "'resources' key should contain a json object: got"
            f" {type(resources_obj_raw)}"
        )

    # Sanity check that we have the correct file format
    for resource_type in DiffContext.fields():
        if resource_type not in resources_obj_raw:
            continue
        resource_names = resources_obj_raw[resource_type]
        if not isinstance(resource_names, list):
            raise ValidioError(
                f"'{resource_type}' should contain a list of resource names: got"
                f" {resource_names}"
            )

    return resources_obj_raw
