from datetime import datetime, timedelta

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
from validio_cli.bin.entities.incidents import calculate_bound, calculate_operator

app = AsyncTyper(help="Metrics and incidents from validators")


@app.async_command(help="List all metrics")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    ended_before: datetime = typer.Option(
        datetime.utcnow(),
        help="Data seen before this timestamp",
    ),
    ended_after: datetime = typer.Option(
        (datetime.utcnow() - timedelta(hours=1)),
        help="Data seen after this timestamp",
    ),
    validator: str = typer.Option(..., help="Validator to fetch metrics for"),
    segment: str = typer.Option(..., help="Segment to fetch metrics for"),
) -> None:
    vc, cfg = get_client(config_dir)

    validator_id = await validators.get_validator_id(vc, cfg, validator, namespace)
    if validator_id is None:
        return None

    metrics = await vc.validator_segment_metrics(
        validator_id=validator_id,
        segment_id=segment,
        start_time=ended_after,
        end_time=ended_before,
    )

    if output_format == OutputFormat.JSON:
        return output_json(metrics)

    return output_text(
        metrics["values"],
        fields={
            "operator": OutputSettings(
                pass_full_object=True,
                reformat=calculate_operator,
            ),
            "bound": OutputSettings(
                pass_full_object=True,
                reformat=calculate_bound,
            ),
            "value": None,
            "is_incident": OutputSettings(attribute_name="isIncident"),
            "age": OutputSettings.string_as_datetime(
                attribute_name="endTime",
            ),
        },
    )


if __name__ == "__main__":
    typer.run(app())
