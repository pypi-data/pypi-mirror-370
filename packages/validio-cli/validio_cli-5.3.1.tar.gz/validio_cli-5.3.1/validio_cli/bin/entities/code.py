import os
import pathlib
import sys
from collections.abc import Mapping
from enum import Enum
from typing import Any

import classdiff  # type: ignore
import typer
from validio_sdk._api.api import APIClient
from validio_sdk.code import _import as code_import
from validio_sdk.code import apply as code_apply
from validio_sdk.code import plan as code_plan
from validio_sdk.code import scaffold
from validio_sdk.resource._diff import GraphDiff, ResourceUpdate
from validio_sdk.resource._resource import DiffContext, Resource, ResourceDeprecation
from validio_sdk.resource._util import SourceSchemaReinference
from validio_sdk.resource.replacement import (
    ImmutableFieldReplacementReason,
    ReplacementReason,
)

from validio_cli import AsyncTyper, ConfigDir, Namespace, get_client
from validio_cli.bin.entities.resources import ResourceNamesToMove, do_move
from validio_cli.components import BETA_BANNER, proceed_with_operation

"""Maximum number of deprecation warnings to show."""
MAX_DEPRECATIONS_TO_SHOW = 20

app = AsyncTyper(help="Plan or apply your configuration")


class DiffOutput(str, Enum):
    """Available output formats for the CLI"""

    FULL = "full"
    CHANGES = "changes"
    NONE = "none"


directory_option = typer.Option(
    "",
    help=(
        "The location to place the generated project; "
        "Defaults to the current directory if not specified"
    ),
)

no_capture_option = typer.Option(
    False,
    help=(
        "By default, the code program's stdout output is hidden; "
        "enable this parameter to recover the output"
    ),
)

show_schema_option = typer.Option(
    False, help="Show the JTD schema in the plan output for Sources"
)

diff_option = typer.Option(
    DiffOutput.CHANGES.value,
    "--diff",
    help="Show only the changed lines (added, removed, or modified)",
)

color_option = typer.Option(
    not os.environ.get("NO_COLOR", False) and sys.stdout.isatty(),
    help="Enable colored output",
)

destroy_option = typer.Option(
    False, help="Deletes all resources associated with the project"
)

show_secrets_option = typer.Option(
    False,
    help=(
        "By default, secret values within credentials are not shown; "
        "enable this parameter to show the values"
    ),
)

update_schema_option = typer.Option(
    [],
    help=(
        "Specify a Source name to update its schema. This checks the upstream data"
        " source for any schema changes before planning. You can use"
        " --update-schema src1 --update-schema src2 to specify multiple Sources."
    ),
)

update_all_schemas_option = typer.Option(
    False,
    help=(
        "Similar to --update-schema. Checks for schema "
        "updates for all Sources before planning"
    ),
)

show_progress_option = typer.Option(
    sys.stdout.isatty(),
    help=(
        f"{BETA_BANNER} "
        "If enabled, progress updates will be displayed during "
        "execution of this command"
    ),
)


def target_option(resource_type: str) -> Any:
    return typer.Option(
        [],
        help=(
            f"{BETA_BANNER} "
            f"Only target selected {resource_type.replace('-', ' ')}(s) and ignore "
            f"changes for others. E.g. `--{resource_type} resource-a"
        ),
    )


@app.command(help="Initialize a new IaC project")
def init(
    directory: str = directory_option,
    force: bool = typer.Option(
        False, help="Forces project files to be generated in a non-empty directory"
    ),
    namespace: str = Namespace(
        "dev", help="A unique name to associate resources managed by the project"
    ),
) -> None:
    dir_path = directory_or_default(directory)

    scaffold._new_project(namespace, dir_path, force)


@app.async_command(help="Show changes to resources from an IaC configuration")
async def plan(
    directory: str = directory_option,
    no_capture: bool = no_capture_option,
    config_dir: str = ConfigDir,
    update_schema: list[str] = update_schema_option,
    update_all_schemas: bool = update_all_schemas_option,
    show_schema: bool = show_schema_option,
    diff_output: DiffOutput = diff_option,
    destroy: bool = destroy_option,
    show_secrets: bool = show_secrets_option,
    color: bool = color_option,
    channel: list[str] = target_option("channel"),
    credential: list[str] = target_option("credential"),
    notification_rule: list[str] = target_option("notification-rule"),
    segmentation: list[str] = target_option("segmentation"),
    source: list[str] = target_option("source"),
    validator: list[str] = target_option("validator"),
    window: list[str] = target_option("window"),
    progress: bool = show_progress_option,
) -> None:
    dir_path = directory_or_default(directory)
    client, _ = get_client(config_dir)

    schema_reinference = create_source_schema_reinference(
        update_schema, update_all_schemas
    )

    namespace = get_namespace(dir_path)
    await _plan(
        namespace=namespace,
        client=client,
        directory=dir_path,
        schema_reinference=schema_reinference,
        destroy=destroy,
        no_capture=no_capture,
        color=color,
        show_schema=show_schema,
        diff_output=diff_output,
        show_secrets=show_secrets,
        targets=code_plan.ResourceNames(
            channels=set(channel),
            credentials=set(credential),
            notification_rules=set(notification_rule),
            segmentations=set(segmentation),
            sources=set(source),
            validators=set(validator),
            windows=set(window),
        ),
        show_progress=progress,
    )


@app.async_command(help="Create or update resources from an IaC configuration")
async def apply(
    directory: str = directory_option,
    no_capture: bool = no_capture_option,
    auto_approve: bool = typer.Option(
        False, help="Automatically approve and perform plan operations"
    ),
    config_dir: str = ConfigDir,
    update_schema: list[str] = update_schema_option,
    update_all_schemas: bool = update_all_schemas_option,
    show_schema: bool = show_schema_option,
    diff_output: DiffOutput = diff_option,
    destroy: bool = destroy_option,
    show_secrets: bool = show_secrets_option,
    color: bool = color_option,
    channel: list[str] = target_option("channel"),
    credential: list[str] = target_option("credential"),
    notification_rule: list[str] = target_option("notification-rule"),
    segmentation: list[str] = target_option("segmentation"),
    source: list[str] = target_option("source"),
    validator: list[str] = target_option("validator"),
    window: list[str] = target_option("window"),
    progress: bool = show_progress_option,
    test_credentials: bool = typer.Option(
        True,
        help=(
            f"{BETA_BANNER} Test that credentials are valid before creating or updating"
        ),
    ),
    dry_run_sql: bool = typer.Option(
        False,
        help=f"""
            {BETA_BANNER} Dry run SQL queries before creating/updating SQL Filters,
            SQL Sources or SQL Validators.
            Note: this feature is unsupported on Azure based warehouses.
        """,
    ),
) -> None:
    dir_path = directory_or_default(directory)
    client, _ = get_client(config_dir)

    schema_reinference = create_source_schema_reinference(
        update_schema, update_all_schemas
    )

    namespace = get_namespace(dir_path)
    plan_result = await _plan(
        namespace=namespace,
        client=client,
        directory=dir_path,
        schema_reinference=schema_reinference,
        destroy=destroy,
        no_capture=no_capture,
        color=color,
        show_schema=show_schema,
        diff_output=diff_output,
        show_secrets=show_secrets,
        targets=code_plan.ResourceNames(
            channels=set(channel),
            credentials=set(credential),
            notification_rules=set(notification_rule),
            segmentations=set(segmentation),
            sources=set(source),
            validators=set(validator),
            windows=set(window),
        ),
        show_progress=progress,
    )

    diff = plan_result.graph_diff
    if diff.num_operations() == 0:
        return

    if not await proceed_with_operation(auto_approve):
        return

    print()
    print("Applying...")

    await code_apply.apply(
        namespace=namespace,
        client=client,
        ctx=plan_result.diff_context,
        diff=diff,
        show_secrets=show_secrets,
        show_progress=progress,
        dry_run_sql=dry_run_sql,
        test_credentials=test_credentials,
    )

    print(
        f"Apply complete! Resources: {diff.num_creates()} created, "
        f"{diff.num_updates()} updated, {diff.num_deletes()} deleted"
    )


@app.async_command(name="import", help="Import resources into the current project")
async def _import(
    directory: str = directory_option,
    no_capture: bool = no_capture_option,
    config_dir: str = ConfigDir,
    output: pathlib.Path = typer.Option(
        ...,
        "--output",
        "-o",
        help=(
            "The path to the file that will contain the generated resource declarations"
        ),
    ),
    import_namespace: str = typer.Option(
        None,
        "--import-namespace",
        help=(
            "Shorthand to first 'move' resources into the current "
            "project's namespace before performing the import. "
        ),
    ),
    credential: list[str] = typer.Option(
        [],
        help=(
            f"{BETA_BANNER} Target credential resources to move into "
            f"the current project's namespace. "
            f"This moves any specified credentials together with their "
            f"attached sources, windows, filters, segmentations and validators. "
            f"Only applicable with '--import-namespace'"
        ),
    ),
    channel: list[str] = typer.Option(
        [],
        help=(
            f"{BETA_BANNER} Target channel resources to move into "
            f"the current project's namespace. "
            f"This moves any specified channels together with their "
            f"attached notification rules. "
            f"Only applicable with '--import-namespace'"
        ),
    ),
    auto_approve: bool = typer.Option(
        False, help="Automatically approve and perform the import operation"
    ),
) -> None:
    resource_names = ResourceNamesToMove(
        credentials=set(credential), channels=set(channel)
    )

    dir_path = directory_or_default(directory)
    client, _ = get_client(config_dir)
    namespace = get_namespace(dir_path)

    if import_namespace:
        num_moved_resources = await do_move(
            client=client,
            namespace=import_namespace,
            target_namespace=namespace,
            resource_names=resource_names,
            auto_approve=auto_approve,
        )
        if num_moved_resources is None:
            return

        if num_moved_resources > 0:
            print(f"Moved {num_moved_resources} resources")

    plan_result = await _plan(
        namespace=namespace,
        client=client,
        directory=dir_path,
        schema_reinference=create_source_schema_reinference([], False),
        destroy=False,
        color=False,
        no_capture=no_capture,
        show_schema=False,
        show_secrets=False,
        show_diff=False,
        import_mode=True,
    )

    if plan_result.graph_diff.num_deletes() == 0:
        _print_no_changes()
        return

    s = await code_import._import(
        ctx=plan_result.graph_diff.to_delete,
        tags_ctx=plan_result.tags_context,
    )
    output.write_text(s)
    print(f"Generated file {output.absolute()}")


def get_namespace(directory: pathlib.Path) -> str:
    settings = scaffold._read_project_settings(directory)
    return settings.namespace


def directory_or_default(directory: str) -> pathlib.Path:
    return (pathlib.Path(directory) if directory else pathlib.Path.cwd()).absolute()


async def _plan(
    namespace: str,
    client: APIClient,
    directory: pathlib.Path,
    schema_reinference: SourceSchemaReinference,
    destroy: bool,
    no_capture: bool,
    color: bool,
    show_schema: bool = False,
    diff_output: DiffOutput = DiffOutput.FULL,
    show_secrets: bool = False,
    show_diff: bool = True,
    targets: code_plan.ResourceNames = code_plan.ResourceNames(),
    import_mode: bool = False,
    show_progress: bool = True,
) -> code_plan.PlanResult:
    plan_result = await code_plan.plan(
        namespace=namespace,
        client=client,
        directory=directory,
        schema_reinference=schema_reinference,
        destroy=destroy,
        no_capture=no_capture,
        show_secrets=show_secrets,
        targets=targets,
        import_mode=import_mode,
        show_progress=show_progress,
    )

    if show_diff:
        if plan_result.graph_diff.num_operations() == 0:
            _print_no_changes()
        else:
            _show_resources_diff(
                diff=plan_result.graph_diff,
                show_schema=show_schema,
                show_secrets=show_secrets,
                escape=color,
                diff_output=diff_output,
            )

    _show_deprecations(plan_result.deprecations)

    return plan_result


def _show_resources_diff(
    diff: GraphDiff,
    show_schema: bool,
    show_secrets: bool,
    escape: bool,
    diff_output: DiffOutput,
) -> None:
    resource_types = DiffContext.fields()
    if diff.num_creates() > 0:
        for t in resource_types:
            _show_create_resource_diff(
                getattr(diff.to_create, t),
                getattr(diff.replacement_ctx, t),
                show_schema,
                show_secrets,
                escape,
                diff_output,
            )

    if diff.num_deletes() > 0:
        for t in resource_types:
            _show_delete_resource_diff(
                getattr(diff.to_delete, t),
                getattr(diff.replacement_ctx, t),
                show_schema,
                show_secrets,
                escape,
                diff_output,
            )

    if diff.num_updates() > 0:
        for t in resource_types:
            _show_update_resource_diff(
                resources=getattr(diff.to_update, t),
                show_schema=show_schema,
                show_secrets=show_secrets,
                color=escape,
                diff_output=diff_output,
            )

    for t in resource_types:
        _show_replace_resource_diff(
            getattr(diff.to_create, t),
            getattr(diff.replacement_ctx, t),
            show_schema,
            show_secrets,
            escape,
            diff_output,
        )

    print(
        "\n"
        f"Plan: {diff.num_creates()} to create, {diff.num_updates()} to update, "
        f"{diff.num_deletes()} to delete."
    )


def _show_create_resource_diff(
    resources: Mapping[str, Resource],
    replaced_resources: Mapping[str, ReplacementReason],
    show_schema: bool,
    show_secrets: bool,
    color: bool,
    diff_output: DiffOutput,
) -> None:
    for r in resources.values():
        if r.name in replaced_resources:
            continue

        class_key = r.__class__.__name__

        print(f"{class_key} '{r.name}' will be created")

        rewrites = _diff_field_rewrites(show_schema)
        value = code_plan._create_resource_diff_object(
            r, rewrites=rewrites, show_secrets=show_secrets
        )

        _show_diff(None, value, color, diff_output, class_key)


def _show_delete_resource_diff(
    resources: Mapping[str, Resource],
    replaced_resources: Mapping[str, ReplacementReason],
    show_schema: bool,
    show_secrets: bool,
    color: bool,
    diff_output: DiffOutput,
) -> None:
    for r in resources.values():
        if r.name in replaced_resources:
            continue

        class_key = r.__class__.__name__

        print(f"{class_key} '{r.name}' will be deleted")

        rewrites = _diff_field_rewrites(show_schema)
        value = code_plan._create_resource_diff_object(
            r, rewrites=rewrites, show_secrets=show_secrets
        )

        _show_diff(value, None, color, diff_output, class_key)


def _show_update_resource_diff(
    resources: Mapping[str, ResourceUpdate],
    show_schema: bool,
    show_secrets: bool,
    color: bool,
    diff_output: DiffOutput,
) -> None:
    for r in resources.values():
        class_key = r.manifest.__class__.__name__

        cascade_update = ""
        if r.replacement_cascaded_update_parent:
            (cls, parent_name) = r.replacement_cascaded_update_parent
            cascade_update = f" (due to replacement of {cls.__name__}({parent_name!r}))"

        print(f"{class_key} '{r.manifest.name}' will be updated{cascade_update}")

        rewrites = _diff_field_rewrites(show_schema)

        a_value = code_plan._create_resource_diff_object(
            r.manifest,
            show_secrets=show_secrets,
            rewrites=rewrites,
            secret_fields_changed=r.secret_fields_changed,
            is_manifest=True,
        )
        b_value = code_plan._create_resource_diff_object(
            r.server,
            show_secrets=show_secrets,
            rewrites=rewrites,
            secret_fields_changed=r.secret_fields_changed,
            is_manifest=False,
        )

        _show_diff(b_value, a_value, color, diff_output, class_key)


def _show_replace_resource_diff(
    resources: Mapping[str, Resource],
    replaced_resources: Mapping[str, ReplacementReason],
    show_schema: bool,
    show_secrets: bool,
    color: bool,
    diff_output: DiffOutput,
) -> None:
    for r in resources.values():
        reason = replaced_resources.get(r.name)
        if not reason:
            continue

        class_key = r.__class__.__name__

        print(f"{class_key} '{r.name}' will be replaced: {reason._reason()}")

        rewrites = _diff_field_rewrites(show_schema)
        a_value, b_value = (None, None)
        if isinstance(reason, ImmutableFieldReplacementReason):
            update = reason.resource_update
            a_value = code_plan._create_resource_diff_object(
                update.manifest,
                show_secrets=show_secrets,
                rewrites=rewrites,
                secret_fields_changed=update.secret_fields_changed,
                is_manifest=True,
            )
            b_value = code_plan._create_resource_diff_object(
                update.server,
                show_secrets=show_secrets,
                rewrites=rewrites,
                secret_fields_changed=update.secret_fields_changed,
                is_manifest=False,
            )
        else:
            b_value = code_plan._create_resource_diff_object(
                r, rewrites=rewrites, show_secrets=show_secrets
            )

        _show_diff(b_value, a_value, color, diff_output, class_key)


def _show_diff(
    current_value: Any,
    new_value: Any,
    color: bool,
    diff_output: DiffOutput,
    class_key: str | None = None,
) -> None:
    if diff_output == DiffOutput.NONE:
        return

    diff = classdiff.diff(
        current_value,
        new_value,
        no_color=not color,
        changes_only=diff_output == DiffOutput.CHANGES,
        object_name=class_key,
    )

    print(diff)

    # We keep track if any lines were printed at all (any changes or full
    # output) and if not we don't add a newline. This is to make it more
    # condensed and consistent with the DiffOutput.NONE output.
    if diff:
        print()


def _diff_field_rewrites(show_schema: bool) -> dict[str, Any]:
    return {} if show_schema else {"jtd_schema": "[NOT SHOWN]"}


def _show_deprecations(deprecations: list[ResourceDeprecation]) -> None:
    if not deprecations:
        return

    title = "⚠️ NOTICE"
    footer = ""

    if len(deprecations) > MAX_DEPRECATIONS_TO_SHOW:
        footer = f"And {len(deprecations) - MAX_DEPRECATIONS_TO_SHOW} more...\n"
        deprecations = deprecations[:MAX_DEPRECATIONS_TO_SHOW]

    print()
    print(f"\033[93m{title}\033[0m")  # Make the text yellow
    for i, message in enumerate(sorted(deprecations)):
        print(f"\033[93m{i + 1:>2}. {message}\033[0m")

    print(footer, end="")


def create_source_schema_reinference(
    schemas_to_update: list[str], update_all_schemas: bool
) -> SourceSchemaReinference:
    source_names = None
    if update_all_schemas:
        source_names = []
    elif len(schemas_to_update) > 0:
        source_names = schemas_to_update

    return SourceSchemaReinference(
        set(source_names) if source_names is not None else None
    )


def _print_no_changes() -> None:
    print("No changes. The configuration is up-to-date!")


if __name__ == "__main__":
    app()
