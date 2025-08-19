import typer

from validio_cli import (
    AsyncTyper,
    ConfigDir,
    Identifier,
    OutputFormat,
    OutputFormatOption,
    OutputSettings,
    get_client,
    output_json,
    output_text,
)

app = AsyncTyper(help="Users in the Validio platform")


@app.async_command(help="Get users")
async def get(
    config_dir: str = ConfigDir,
    output_format: OutputFormat = OutputFormatOption,
    identifier: str = Identifier,
) -> None:
    vc, _ = get_client(config_dir)

    users = await vc.get_users(user_id=identifier)

    if output_format == OutputFormat.JSON:
        return output_json(users, identifier)

    return output_text(
        users,
        fields={
            "name": OutputSettings(attribute_name="resourceName"),
            "global_role": OutputSettings(attribute_name="globalRole"),
            "status": None,
            "identities": OutputSettings(reformat=lambda x: len(x)),
            "age": OutputSettings.string_as_datetime(attribute_name="createdAt"),
        },
    )


if __name__ == "__main__":
    typer.run(app())
