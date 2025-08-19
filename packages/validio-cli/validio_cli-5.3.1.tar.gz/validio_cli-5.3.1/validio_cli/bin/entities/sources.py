import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Optional, cast

import click
import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from validio_sdk import ValidioError
from validio_sdk._api.api import (
    APIClient,
    SourceAction,
    apply_source_action,
    get_sources,
    split_to_chunks,
)
from validio_sdk.client import Session
from validio_sdk.config import ValidioConfig

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
    components,
    format_text,
    get_client,
    output_json,
    output_ok_or_error,
    output_text,
)
from validio_cli.bin.entities import credentials
from validio_cli.components import proceed_with_operation
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Data sources to ingest data from")

infer_schema_app = AsyncTyper(help="Infer schema")
app.add_typer(infer_schema_app, no_args_is_help=True, name="infer-schema")


def schema_filename_option(schema_type: str) -> Any:  # typer returns Any here
    return typer.Option(
        Path(Path.cwd(), f"{schema_type}_{uuid.uuid4()}.json"),
        "--filename",
        "-f",
        help="Filename including path for where to write inferred schema",
    )


@app.async_command(help="List all sources")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifier: str = Identifier,
    credential_id: str = typer.Option(None, help="List sources for this credential id"),
    credential_name: str = typer.Option(
        None, help="List sources for this credential name"
    ),
) -> None:
    if identifier and (credential_id or credential_name):
        raise ValidioError(
            "--credential-id or --credential-name can't be used together "
            "with an identifier"
        )

    vc, cfg = get_client(config_dir)

    sources = await vc.get_sources(
        source_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    if credential_id or credential_name:
        if not isinstance(sources, list):
            raise ValidioError("failed to get sources")

        sources = [
            source
            for source in sources
            if _resource_filter(source, credential_id, credential_name)
        ]

    if output_format == OutputFormat.JSON:
        return output_json(sources, identifier)

    return output_text(
        sources,
        fields={
            "name": OutputSettings(attribute_name="resourceName"),
            "type": OutputSettings.trimmed_upper_snake(
                attribute_name="__typename", trim="Source"
            ),
            "state": None,
            "age": OutputSettings.string_as_datetime(attribute_name="createdAt"),
        },
    )


@app.async_command(help="Delete source")
async def delete(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    if not identifiers:
        raise ValidioError("no identifiers are provided")

    vc, cfg = get_client(config_dir)

    source_ids = [
        source_id
        for source_id in [
            await get_source_id(vc, cfg, identifier, namespace)
            for identifier in identifiers
        ]
        if source_id
    ]

    result = await vc.delete_sources(source_ids)

    if output_format == OutputFormat.JSON:
        return output_json(result)

    return output_ok_or_error(result)


async def prompt_for_start_all_sources(
    client: APIClient,
    cfg: ValidioConfig,
    namespace: str,
    auto_approve: bool,
) -> list[str] | None:
    if not namespace:
        raise typer.BadParameter("Namespace must be supplied when using --all")

    sources = await client.get_sources(
        namespace_id=get_namespace(namespace, cfg),
    )

    if not isinstance(sources, list):
        raise ValidioError("failed to get sources")

    if len(sources) == 0:
        print("No sources exist in namespace to start")
        return None

    sources_to_start = [
        source for source in sources if source.get("state") in ["IDLE", "INIT"]
    ]

    if len(sources_to_start) == 0:
        print("No sources in namespace that need starting")
        return None

    prompt = "The following sources will be started:\n"
    prompt += format_text(
        sources_to_start,
        fields={
            "id": OutputSettings(attribute_name="id"),
            "resource_name": OutputSettings(attribute_name="resourceName"),
            "type": OutputSettings.trimmed_upper_snake(
                attribute_name="__typename", trim="Source"
            ),
            "state": None,
        },
    )

    print(prompt)

    if not await proceed_with_operation(auto_approve):
        return None
    print()

    return [source["id"] for source in sources_to_start]


@app.async_command(help="Start sources")
async def start(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    # ruff: noqa: ARG001
    namespace: str = Namespace(),
    all: bool = typer.Option(False, "--all", help="Start all unstarted sources"),
    auto_approve: bool = typer.Option(
        False,
        help="When used with --all, automatically approve starting of all sources",
    ),
    identifiers: Optional[list[str]] = Identifiers,
) -> None:
    client, cfg = get_client(config_dir)

    if all and identifiers and len(identifiers) > 0:
        raise typer.BadParameter(
            "Cannot use both --all and supplying source "
            "identifiers. You must only use one of them"
        )

    if all:
        identifiers = await prompt_for_start_all_sources(
            client=client,
            cfg=cfg,
            namespace=namespace,
            auto_approve=auto_approve,
        )

    if identifiers:
        async with client.client as session:
            await apply_source_action_on_chunks(
                session,
                cfg,
                SourceAction.START,
                split_to_chunks(identifiers),
                namespace,
                output_format,
            )


@app.async_command(help="Stop source")
async def stop(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    # ruff: noqa: ARG001
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    client, cfg = get_client(config_dir)
    async with client.client as session:
        await apply_source_action_on_chunks(
            session,
            cfg,
            SourceAction.STOP,
            split_to_chunks(identifiers),
            namespace,
            output_format,
        )


@app.async_command(help="Backfill source")
async def backfill(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    # ruff: noqa: ARG001
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    client, cfg = get_client(config_dir)
    async with client.client as session:
        await apply_source_action_on_chunks(
            session,
            cfg,
            SourceAction.BACKFILL,
            split_to_chunks(identifiers),
            namespace,
            output_format,
        )


@app.async_command(help="Reset source")
async def reset(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    # ruff: noqa: ARG001
    namespace: str = Namespace(),
    identifiers: list[str] = Identifiers,
) -> None:
    client, cfg = get_client(config_dir)
    async with client.client as session:
        await apply_source_action_on_chunks(
            session,
            cfg,
            SourceAction.RESET,
            split_to_chunks(identifiers),
            namespace,
            output_format,
        )


@infer_schema_app.callback(invoke_without_command=True)
def main(
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Infer schema with an interactive prompt"
    ),
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("schema"),
    namespace: str = Namespace(),
) -> None:
    ctx = click.get_current_context()

    # A subcommand was run prior to this, nothing todo
    if ctx.invoked_subcommand is not None:
        return None

    # The interactive flag was used, run the interactive version
    if interactive:
        return asyncio.run(_interactive(config_dir, filename, namespace))

    # A flag for this command was used but not interactive, print the help as if
    # no command was given
    click.echo(ctx.get_help())

    return None


# Not much to do with this complexity
# ruff: noqa: PLR0915,PLR0912
async def _interactive(config_dir: str, filename: Path, namespace: str) -> None:
    vc, cfg = get_client(config_dir)

    credentials = await vc.get_credentials(namespace_id=get_namespace(namespace, cfg))

    if not isinstance(credentials, list):
        raise ValidioError("failed to get credentials")

    if len(credentials) == 0:
        raise ValidioError(f"No credentials found in namespace {namespace}")

    credential_name_to_id = [(c["id"], c["name"]) for c in credentials]

    credential_id = await components.radiolist_dialog(
        title="Credentials to use",
        values=credential_name_to_id,
        navigation_help=True,
    )

    if credential_id is None:
        return

    credential_type = next(
        (c["__typename"] for c in credentials if c["id"] == credential_id), None
    )
    if credential_type is None:
        return

    credential_type_to_source_type = {
        "AwsCredential": [
            ("kinesis", "Amazon Kinesis"),
        ],
        "DatabricksCredential": [("databricks", "Databricks")],
        "DemoCredential": [("demo", "Demo")],
        "GcpCredential": [
            ("bigquery", "Google BigQuery"),
            ("pubsub", "Google Pub/Sub"),
        ],
        "PostgreSqlCredential": [("postgresql", "PostgreSQL")],
        "RedshiftCredential": [("redshift", "Amazon Redshift")],
        "SnowflakeCredential": [("snowflake", "Snowflake")],
        "KafkaCredential": [("kafka", "Kafka")],
    }

    if credential_type not in credential_type_to_source_type:
        print(f"Unsupported credential type {credential_type} for inferring schema")
        return

    if len(credential_type_to_source_type[credential_type]) > 1:
        print()
        inference_type = await components.radiolist_dialog(
            title="Source type",
            values=credential_type_to_source_type[credential_type],
        )
    else:
        inference_type = credential_type_to_source_type[credential_type][0][0]

    if inference_type is None:
        return

    match inference_type:
        case "databricks":
            info = await _multip_prompt(
                [
                    ("Catalog", [], ""),
                    ("Schema", [], ""),
                    ("Table", [], ""),
                ]
            )
            await _infer_schema_databricks(
                vc,
                filename,
                credential_id,
                info.get("catalog", ""),
                info.get("schema", ""),
                info.get("table", ""),
            )
        case "demo":
            await _infer_schema_demo(vc, filename)
        case "kinesis":
            info = await _multip_prompt(
                [
                    (
                        "Region",
                        # https://docs.aws.amazon.com/general/latest/gr/ak.html
                        [
                            "us-east-2",
                            "us-east-1",
                            "us-west-1",
                            "us-west-2",
                            "af-south-1",
                            "ap-east-1",
                            "ap-south-2",
                            "ap-southeast-3",
                            "ap-southeast-4",
                            "ap-south-1",
                            "ap-northeast-3",
                            "ap-northeast-2",
                            "ap-southeast-1",
                            "ap-southeast-2",
                            "ap-northeast-1",
                            "ca-central-1",
                            "eu-central-1",
                            "eu-west-1",
                            "eu-west-2",
                            "eu-south-1",
                            "eu-west-3",
                            "eu-south-2",
                            "eu-north-1",
                            "eu-central-2",
                            "me-south-1",
                            "me-central-1",
                            "sa-east-1",
                            "us-gov-east-1",
                            "us-gov-west-1",
                        ],
                        "",
                    ),
                    ("Stream name", [], ""),
                    _interactive_message_format_input(),
                    ("Message schema", [], ""),
                ]
            )

            await _infer_schema_kinesis(
                vc,
                filename,
                credential_id,
                info.get("region", ""),
                info.get("stream_name", ""),
                info.get("message_format", ""),
                info.get("message_schema", ""),
            )
        case "pubsub":
            info = await _multip_prompt(
                [
                    ("Project", [], ""),
                    ("Subscription ID", [], ""),
                    _interactive_message_format_input(),
                    ("Message schema", [], ""),
                ]
            )

            await _infer_schema_pubsub(
                vc,
                filename,
                credential_id,
                info.get("project", ""),
                info.get("subscription_id", ""),
                info.get("message_format", ""),
                info.get("message_schema", ""),
            )
        case "pubsublite":
            info = await _multip_prompt(
                [
                    ("Project", [], ""),
                    ("Subscription ID", [], ""),
                    # https://cloud.google.com/pubsub/lite/docs/locations
                    (
                        "Location",
                        [
                            "asia-east1",
                            "asia-east2",
                            "asia-northeast1",
                            "asia-northeast2",
                            "asia-northeast3",
                            "asia-south1",
                            "asia-southeast1",
                            "asia-southeast2",
                            "australia-southeast1",
                            "australia-southeast2",
                            "europe-central2",
                            "europe-north1",
                            "europe-west1",
                            "europe-west2",
                            "europe-west3",
                            "europe-west4",
                            "europe-west6",
                            "europe-west8",
                            "europe-west9",
                            "me-central1",
                            "northamerica-northeast1",
                            "me-west1",
                            "northamerica-northeast2",
                            "southamerica-east1",
                            "us-central1",
                            "us-east1",
                            "us-east4",
                            "us-east5",
                            "us-west1",
                            "us-west2",
                            "us-west3",
                            "us-west4",
                        ],
                        "",
                    ),
                    _interactive_message_format_input(),
                    ("Message schema", [], ""),
                ]
            )
        case "kafka":
            info = await _multip_prompt(
                [
                    ("topic", [], ""),
                    _interactive_message_format_input(),
                    ("Message schema", [], ""),
                ]
            )
            await _infer_schema_kafka(
                vc,
                filename,
                credential_id,
                info.get("topic", ""),
                info.get("message_format", ""),
                info.get("message_schema", ""),
            )
        case "postgresql":
            info = await _multip_prompt(
                [
                    ("Schema", [], ""),
                    ("Database", [], ""),
                    ("Table", [], ""),
                ]
            )
            await _infer_schema_postgresql(
                vc,
                filename,
                credential_id,
                info.get("schema", ""),
                info.get("database", ""),
                info.get("table", ""),
            )
        case "redshift":
            info = await _multip_prompt(
                [
                    ("Schema", [], ""),
                    ("Database", [], ""),
                    ("Table", [], ""),
                ]
            )
            await _infer_schema_redshift(
                vc,
                filename,
                credential_id,
                info.get("schema", ""),
                info.get("database", ""),
                info.get("table", ""),
            )
        case "snowflake":
            info = await _multip_prompt(
                [
                    ("Schema", [], ""),
                    ("Database", [], ""),
                    ("Table", [], ""),
                    ("Warehouse", [], ""),
                    ("Role", [], ""),
                ]
            )
            await _infer_schema_snowflake(
                vc,
                filename,
                credential_id,
                info.get("schema", ""),
                info.get("database", ""),
                info.get("table", ""),
                info.get("role", ""),
                info.get("warehouse", ""),
            )
        case "bigquery":
            info = await _multip_prompt(
                [
                    ("Project", [], ""),
                    ("Dataset", [], ""),
                    ("Table", [], ""),
                ]
            )
            await _infer_schema_bigquery(
                vc,
                filename,
                credential_id,
                info.get("project", ""),
                info.get("dataset", ""),
                info.get("table", ""),
            )
        case _:
            print("Not yet implemented...")
            return


@infer_schema_app.async_command(help="Infer Demo schema")
async def demo(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("demo"),
) -> None:
    vc, _ = get_client(config_dir)
    await _infer_schema_demo(vc, filename)


@infer_schema_app.async_command(help="Infer Amazon Kinesis schema")
async def kinesis(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("kinesis"),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    region: str = typer.Option(..., help="AWS region"),
    stream_name: str = typer.Option(..., help="AWS Kinesis stream name"),
    message_format: str = typer.Option(default=None, help="Message format"),
    message_schema: str = typer.Option(default=None, help="Message schema"),
    namespace: str = Namespace(),
) -> None:
    vc, cfg = get_client(config_dir)

    resolved_credential_id = await _resolve_credential(
        vc, cfg, credential_id, namespace
    )

    await _infer_schema_kinesis(
        vc,
        filename,
        resolved_credential_id,
        region,
        stream_name,
        message_format,
        message_schema,
    )


@infer_schema_app.async_command(help="Infer GCP Pub/Sub schema")
async def pubsub(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("pubsub"),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    project: str = typer.Option(..., help="GCP project"),
    subscription_id: str = typer.Option(..., help="GCP Pub/Sub subscription ID"),
    message_format: str = typer.Option(default=None, help="Message format"),
    message_schema: str = typer.Option(default=None, help="Message schema"),
    namespace: str = Namespace(),
) -> None:
    vc, cfg = get_client(config_dir)

    resolved_credential_id = await _resolve_credential(
        vc, cfg, credential_id, namespace
    )

    await _infer_schema_pubsub(
        vc,
        filename,
        resolved_credential_id,
        project,
        subscription_id,
        message_format,
        message_schema,
    )


@infer_schema_app.async_command(help="Infer Kafka schema")
async def kafka(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("kafka"),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    topic: str = typer.Option(..., help="Kafka topic"),
    message_format: str = typer.Option(default=None, help="Message format"),
    message_schema: str = typer.Option(default=None, help="Message schema"),
    namespace: str = Namespace(),
) -> None:
    vc, cfg = get_client(config_dir)

    resolved_credential_id = await _resolve_credential(
        vc, cfg, credential_id, namespace
    )
    await _infer_schema_kafka(
        vc, filename, resolved_credential_id, topic, message_format, message_schema
    )


@infer_schema_app.async_command(help="Infer PostgreSQL schema")
async def postgresql(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("postgresql"),
    namespace: str = Namespace(),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    schema: str = typer.Option(..., help="Schema name"),
    database: str = typer.Option(..., help="Database name"),
    table: str = typer.Option(..., help="Table name"),
) -> None:
    vc, cfg = get_client(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_postgresql(
        vc, filename, resolved_credential_id, schema, database, table
    )


@infer_schema_app.async_command(help="Infer Amazon Redshift schema")
async def redshift(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("redshift"),
    namespace: str = Namespace(),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    schema: str = typer.Option(..., help="Schema name"),
    database: str = typer.Option(..., help="Database name"),
    table: str = typer.Option(..., help="Table name"),
) -> None:
    vc, cfg = get_client(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_redshift(
        vc, filename, resolved_credential_id, schema, database, table
    )


@infer_schema_app.async_command(help="Infer Snowflake schema")
async def snowflake(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("snowflake"),
    namespace: str = Namespace(),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    schema: str = typer.Option(..., help="Schema name"),
    database: str = typer.Option(..., help="Database name"),
    table: str = typer.Option(..., help="Table name"),
    role: str = typer.Option(..., help="Role name"),
    warehouse: str = typer.Option(..., help="Warehouse name"),
) -> None:
    vc, cfg = get_client(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_snowflake(
        vc, filename, resolved_credential_id, schema, database, table, role, warehouse
    )


@infer_schema_app.async_command(help="Infer Google BigQuery schema")
async def bigquery(
    config_dir: str = ConfigDir,
    filename: Path = schema_filename_option("bigquery"),
    namespace: str = Namespace(),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    project: str = typer.Option(..., help="Google project name"),
    dataset: str = typer.Option(..., help="Dataset name"),
    table: str = typer.Option(..., help="Table name"),
) -> None:
    vc, cfg = get_client(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        return

    await _infer_schema_bigquery(
        vc, filename, resolved_credential_id, project, dataset, table
    )


async def _infer_schema_databricks(
    vc: APIClient,
    filename: Path,
    credential_id: str,
    catalog: str,
    db_schema: str,
    table: str,
) -> None:
    schema = await vc.infer_schema(
        class_name="Databricks",
        variable_values={
            "credentialId": credential_id,
            "httpPath": "",
            "catalog": catalog,
            "schema": db_schema,
            "table": table,
        },
    )
    _write_schema(filename, schema)


async def _infer_schema_demo(
    vc: APIClient,
    filename: Path,
) -> None:
    schema = await vc.infer_schema(class_name="Demo", variable_values={}, no_args=True)
    _write_schema(filename, schema)


async def _infer_schema_kinesis(
    vc: APIClient,
    filename: Path,
    credential_id: str,
    region: str,
    stream_name: str,
    message_format: str | None = None,
    message_schema: str | None = None,
) -> None:
    message_format_input = _get_message_format_input(message_format, message_schema)
    schema = await vc.infer_schema(
        class_name="AwsKinesis",
        variable_values={
            "credentialId": credential_id,
            "region": region,
            "streamName": stream_name,
            "messageFormat": message_format_input,
        },
    )
    _write_schema(filename, schema)


async def _infer_schema_pubsub(
    vc: APIClient,
    filename: Path,
    credential_id: str,
    project: str,
    subscription_id: str,
    message_format: str | None = None,
    message_schema: str | None = None,
) -> None:
    message_format_input = _get_message_format_input(message_format, message_schema)
    schema = await vc.infer_schema(
        class_name="GcpPubSub",
        variable_values={
            "credentialId": credential_id,
            "project": project,
            "subscription_id": subscription_id,
            "messageFormat": message_format_input,
        },
    )
    _write_schema(filename, schema)


async def _infer_schema_kafka(
    vc: APIClient,
    filename: Path,
    credential_id: str,
    topic: str,
    message_format: str | None = None,
    message_schema: str | None = None,
) -> None:
    message_format_input = _get_message_format_input(message_format, message_schema)
    schema = await vc.infer_schema(
        class_name="Kafka",
        variable_values={
            "credentialId": credential_id,
            "topic": topic,
            "messageFormat": message_format_input,
        },
    )
    _write_schema(filename, schema)


async def _infer_schema_postgresql(
    vc: APIClient,
    filename: Path,
    credential_id: str,
    db_schema: str,
    database: str,
    table: str,
) -> None:
    schema = await vc.infer_schema(
        class_name="PostgreSql",
        variable_values={
            "credentialId": credential_id,
            "schema": db_schema,
            "database": database,
            "table": table,
        },
    )
    _write_schema(filename, schema)


async def _infer_schema_redshift(
    vc: APIClient,
    filename: Path,
    credential_id: str,
    db_schema: str,
    database: str,
    table: str,
) -> None:
    schema = await vc.infer_schema(
        class_name="AwsRedshift",
        variable_values={
            "credentialId": credential_id,
            "schema": db_schema,
            "database": database,
            "table": table,
        },
    )
    _write_schema(filename, schema)


async def _infer_schema_snowflake(
    vc: APIClient,
    filename: Path,
    credential_id: str,
    db_schema: str,
    database: str,
    table: str,
    role: str,
    warehouse: str,
) -> None:
    schema = await vc.infer_schema(
        class_name="Snowflake",
        variable_values={
            "credentialId": credential_id,
            "schema": db_schema,
            "database": database,
            "table": table,
            "role": role,
            "warehouse": warehouse,
        },
    )
    _write_schema(filename, schema)


async def _infer_schema_bigquery(
    vc: APIClient,
    filename: Path,
    credential_id: str,
    project: str,
    dataset: str,
    table: str,
) -> None:
    schema = await vc.infer_schema(
        class_name="GcpBigQuery",
        variable_values={
            "credentialId": credential_id,
            "project": project,
            "dataset": dataset,
            "table": table,
        },
    )
    _write_schema(filename, schema)


def _write_schema(filename: Path, schema: Any) -> None:
    filename.write_text(json.dumps(schema, indent=2))

    print(f"Schema written to {filename}")


async def _multip_prompt(questions: list[tuple[str, list[str], str]]) -> dict[str, str]:
    answers = {}
    session: PromptSession = PromptSession()
    for f in questions:
        title, values, default = f
        answer_key = title.replace(" ", "_").lower()
        completer = WordCompleter(values)

        answers[answer_key] = await session.prompt_async(
            validio_cli._fixed_width(title),
            completer=completer,
            default=default,
            complete_in_thread=True,
        )

    return answers


async def _get_source_id(
    session: Session,
    cfg: ValidioConfig,
    identifier: str,
    namespace: str,
) -> str | None:
    """
    Ensure the identifier is a resource id.

    If it doesn't have the expected prefix, do a resource lookup by name.
    """
    identifier_type = "source"
    prefix = "SRC_"

    if identifier is None:
        print(f"Missing {identifier_type} id or name")
        return None

    if identifier.startswith(prefix):
        return identifier

    resource = await get_sources(
        session,
        source_id=identifier,
        namespace_id=get_namespace(namespace, cfg),
    )

    if resource is None:
        print(f"No {identifier_type} with name or id {identifier} found")
        return None

    if not isinstance(resource, dict):
        raise ValidioError("failed to get source id")

    return resource["id"]


async def get_source_id(
    client: APIClient,
    cfg: ValidioConfig,
    identifier: str,
    namespace: str,
) -> str | None:
    async with client.client as session:
        return await _get_source_id(session, cfg, identifier, namespace)


def _resource_filter(
    source: Any, credential_id: str | None, credential_name: str | None
) -> bool:
    if credential_id is not None and source["credential"]["id"] != credential_id:
        return False

    return (
        credential_name is not None
        and source["credential"]["resourceName"] == credential_name
    )


async def _resolve_credential(
    vc: APIClient, cfg: ValidioConfig, credential_id: str, namespace: str
) -> str:
    resolved_credential_id = await credentials.get_credential_id(
        vc, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        raise ValidioError("Credential not found")

    return resolved_credential_id


def _get_message_format_input(
    message_format: str | None, message_schema: str | None
) -> dict[str, Any] | None:
    if any([message_format, message_schema]) and not all(
        [message_format, message_schema]
    ):
        raise ValidioError(
            "Both message_format and message_schema must be supplied, or neither them"
        )
    if all([message_format, message_schema]):
        return {
            "format": cast(str, message_format).upper(),
            "schema": message_schema,
        }

    return None


def _interactive_message_format_input() -> tuple[str, list[str], str]:
    available_formats = ["JSON", "PROTOBUF", "AVRO"]

    return (
        "Message format",
        available_formats,
        "",
    )


async def apply_source_action_on_chunks(
    session: Session,
    cfg: ValidioConfig,
    action: SourceAction,
    chunks: list[list[str]],
    namespace: str,
    output_format: OutputFormat = OutputFormatOption,
) -> None:
    results = await asyncio.gather(
        *[
            apply_batch_source_action(session, cfg, action, chunk, namespace)
            for chunk in chunks
        ]
    )

    return await handle_source_action_response(
        results,
        action,
        output_format,
    )


async def apply_batch_source_action(
    session: Session,
    cfg: ValidioConfig,
    action: SourceAction,
    identifiers: list[str],
    namespace: str,
) -> list[dict[str, Any]]:
    return [
        await apply_single_source_action(session, action, cfg, id, namespace)
        for id in identifiers
    ]


async def apply_single_source_action(
    session: Session,
    action: SourceAction,
    cfg: ValidioConfig,
    identifier: str,
    namespace: str,
) -> dict[str, Any]:
    source_id = await _get_source_id(session, cfg, identifier, namespace)
    if source_id is None:
        return {
            "errors": [{"message": f"No source with id or name {identifier} found"}]
        }

    result = await apply_source_action(session, action, source_id)
    return {
        "id": source_id,
        **result,
    }


async def handle_source_action_response(
    results: list[list[dict[str, Any]]],
    action: SourceAction,
    output_format: OutputFormat,
) -> None:
    results_flattened = [item for sublist in results for item in sublist]
    error_responses = [resp for resp in results_flattened if len(resp["errors"]) > 0]

    match action:
        case SourceAction.START:
            field_name = "started"
        case SourceAction.STOP:
            field_name = "stopped"
        case SourceAction.BACKFILL:
            field_name = "initiated_backfill"
        case SourceAction.RESET:
            field_name = "reset"
        case _:
            raise ValidioError(f"Invalid source action: {action}")

    result = {
        field_name: len(results_flattened) - len(error_responses),
        "failed": len(error_responses),
        "errors": error_responses,
    }

    if output_format == OutputFormat.JSON:
        return output_json(result)

    output_action_word = ""
    match action:
        case SourceAction.START:
            output_action_word = "starting"
        case SourceAction.STOP:
            output_action_word = "stopping"
        case SourceAction.BACKFILL:
            output_action_word = "initiating backfilling"
        case SourceAction.RESET:
            output_action_word = "resetting"

    print(f"Summary of results when {output_action_word} sources:")
    output_text(
        result,
        fields={
            field_name: None,
            "failed": None,
        },
    )

    if len(error_responses) > 0:
        print()
        print(f"Failures details when {output_action_word} sources:")
        output_text(
            error_responses,
            fields={
                "source": OutputSettings(
                    attribute_name="id",
                ),
                "error": OutputSettings(
                    attribute_name="errors",
                    reformat=lambda errors: ",".join(
                        [error["message"] for error in errors]
                    ),
                ),
            },
        )

    return None


if __name__ == "__main__":
    typer.run(app())
