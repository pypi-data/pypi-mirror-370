import typing
from pathlib import Path
from typing import Any, Optional

import typer
from validio_sdk import ValidioError, dbt, util

from validio_cli import AsyncTyper, ConfigDir, Namespace, get_client
from validio_cli.bin.entities import credentials

app = AsyncTyper(help="dbt related commands")

"""
Well-known file name for the manifest artifact.

https://docs.getdbt.com/reference/artifacts/dbt-artifacts
"""
MANIFEST_FILE_NAME = "manifest.json"

"""
Well-known file name for the run-results artifact.

https://docs.getdbt.com/reference/artifacts/dbt-artifacts
"""
RUN_RESULTS_FILE_NAME = "run_results.json"


def _resolve_file_paths(
    target_path: Path,
) -> tuple[Path, Optional[Path]]:
    if not target_path:
        raise ValidioError("Missing --target-path argument")

    manifest_path = target_path / MANIFEST_FILE_NAME
    run_results_path = target_path / RUN_RESULTS_FILE_NAME
    if not manifest_path.is_file():
        raise ValidioError(f"manifest file not found at {manifest_path}")

    if not run_results_path.is_file():
        print(
            "Warning: run_results file not found at {run_results_path}. "
            "Uploading only manifest file"
        )
        return manifest_path, None

    return manifest_path, run_results_path


@app.async_command(help="Upload dbt artifact")
async def upload(
    config_dir: str = ConfigDir,
    namespace: str = Namespace(),
    credential_id: str = typer.Option(..., help="Credential name or ID"),
    job_name: str = typer.Option(
        ..., help="The job that the dbt execution belongs to, e.g. `staging-pipeline`"
    ),
    target_path: Path = typer.Option(
        ..., help="Path to the dbt artifacts target directory. "
    ),
) -> None:
    client, cfg = get_client(config_dir)

    resolved_credential_id = await credentials.get_credential_id(
        client, cfg, credential_id, namespace
    )
    if resolved_credential_id is None:
        raise ValidioError(f"Credential '{credential_id}' not found")

    manifest, run_results = _resolve_file_paths(target_path)

    run_results_content = None
    try:
        manifest_content = typing.cast(dict[str, Any], util.read_json_file(manifest))
        if run_results is not None:
            run_results_content = typing.cast(
                dict[str, Any],
                util.read_json_file(run_results),
            )
    except Exception as e:
        raise ValidioError(f"Failed to process artifacts file: {e}")

    await dbt.upload_artifacts(
        client=client,
        credential_id=resolved_credential_id,
        job_name=job_name,
        manifest=manifest_content,
        run_results=run_results_content,
    )
    return print("dbt artifact uploaded successfully")


if __name__ == "__main__":
    typer.run(app())
