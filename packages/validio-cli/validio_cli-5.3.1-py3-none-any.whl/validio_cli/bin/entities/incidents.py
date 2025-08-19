from datetime import datetime, timedelta
from typing import Any

import typer

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    get_client,
    output_json,
    output_text,
)
from validio_cli.bin.entities import validators

app = AsyncTyper(help="Incidents from validators")


@app.async_command(
    help="""List all incidents.

By default you will get incidents from the last hour. You can specify a time
range for when the incident occurred by specifying when the incident ended.

You can list incidents in different ways:

* Listing all incidents

* Listing all incidents for a specific validator with --validator

* Listing all incidents for a specific segment with --segment

* Listing all incidents for a specific validator and segment with --validator
and --segment together
"""
)
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    ended_before: datetime = typer.Option(
        datetime.utcnow(),
        help="The incident ended before this timestamp",
    ),
    ended_after: datetime = typer.Option(
        (datetime.utcnow() - timedelta(hours=1)),
        help="The incident ended after this timestamp",
    ),
    validator: str = typer.Option(..., help="Validator to fetch incidents for"),
    segment: str = typer.Option(None, help="Segment to fetch incidents for"),
) -> None:
    vc, cfg = get_client(config_dir)

    validator_id = await validators.get_validator_id(vc, cfg, validator, namespace)
    if validator_id is None:
        return None

    incidents = await vc.get_incidents(
        validator_id=validator_id,
        segment_id=segment,
        start_time=ended_after,
        end_time=ended_before,
    )

    if not incidents:
        return output_text(None, {})

    if output_format == OutputFormat.JSON:
        return output_json(incidents)

    return output_text(
        incidents["incidents"],
        fields={
            "validator": OutputSettings(
                pass_full_object=True, reformat=lambda _: incidents["__typename"]
            ),
            "bound": OutputSettings(
                pass_full_object=True,
                reformat=lambda x: (
                    f"{format_number(x['lowerBound'])} - "
                    f"{format_number(x['upperBound'])}"
                ),
            ),
            "value": OutputSettings(reformat=format_number),
            "deviation": OutputSettings(reformat=format_number),
            "severity": None,
            "status": None,
            "age": OutputSettings.string_as_datetime(attribute_name="endTime"),
        },
    )


def calculate_operator(item: Any) -> str:
    type_ = item["__typename"][len("ValidatorMetricWith") :]
    if type_ == "DynamicThreshold":
        return f"{type_}/{item['decisionBoundsType']}"

    if type_ == "FixedThreshold":
        return f"{type_}/{item['operator']}"

    return type_


def calculate_bound(item: Any) -> str:
    type_ = item["__typename"][len("ValidatorMetricWith") :]
    if type_ == "DynamicThreshold":
        bound = f"{item['lowerBound']:.2f} - {item['upperBound']:.2f}"
    elif type_ == "DifferenceThreshold":
        lower = f"{item['lowerBound']:.2f}" if item["lowerBound"] is not None else "-"
        upper = f"{item['upperBound']:.2f}" if item["upperBound"] is not None else "-"

        bound = f"{lower} - {upper}"
    elif type_ == "FixedThreshold":
        bound = item["bound"]
    else:
        bound = "-"

    return bound


def format_number(item: Any) -> str:
    if item % 1 == 0:
        return str(item)
    if (item * 10) % 1 == 0:
        return f"{item:.1f}"
    if (item * 100) % 1 == 0:
        return f"{item:.2f}"
    if (item * 1000) % 1 == 0:
        return f"{item:.3f}"

    return f"{item:.3f}..."


if __name__ == "__main__":
    typer.run(app())
