"""Metadata information about the package."""

import importlib.metadata


def version() -> str:
    """Get the version of the CLI from the metadata."""
    return importlib.metadata.version(
        "validio-cli"
    )  # This needs to match the distribution package name
