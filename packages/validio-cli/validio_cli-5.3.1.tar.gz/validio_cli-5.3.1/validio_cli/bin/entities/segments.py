from dataclasses import dataclass

import typer

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Namespace,
    OutputFormat,
    OutputFormatOption,
    RequiredIdentifier,
    get_client,
    output_json,
    output_text,
)
from validio_cli.namespace import get_namespace

app = AsyncTyper(help="Segments for a segmentation")


@app.async_command(help="Get segment")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    namespace: str = Namespace(),
    segmentation: str = RequiredIdentifier,
    max_fields: int = typer.Option(3, help="Maximum number of fields to show"),
) -> None:
    vc, cfg = get_client(config_dir)

    segments = await vc.get_segments(
        segmentation_id=segmentation,
        namespace_id=get_namespace(namespace, cfg),
    )

    if output_format == OutputFormat.JSON:
        return output_json(segments)

    @dataclass
    class SegmentOutput:
        id: str
        field_and_value: str

    resources = []
    for segment in segments:
        field_and_value = []
        for f in segment["fields"]:
            field_and_value.append(f"{f['field']}={f['value']}")

        additional = ""
        if len(field_and_value) > max_fields:
            additional = f" and {len(field_and_value) - max_fields} more"
            field_and_value = field_and_value[:max_fields]

        resources.append(
            SegmentOutput(
                id=segment["id"],
                field_and_value=", ".join(field_and_value) + additional,
            )
        )

    return output_text(
        resources,
        fields={
            "id": None,
            "field_and_value": None,
        },
    )


if __name__ == "__main__":
    typer.run(app())
