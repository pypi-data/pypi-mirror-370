"""Namepsace management."""

from validio_sdk.config import ValidioConfig

import validio_cli


def get_namespace(ns: str | None, cfg: ValidioConfig) -> str:
    """
    Get default namespace.

    If a namespace is passed, use that one. If not, pick the one from the config
    file. If there is none in the config file, use the default one.

    :param ns: Optional namespace, probably from the prompt
    :param cfg: ValidioConfig
    :returns: A string with the default namespace
    """
    if ns:
        return ns

    if cfg.default_namespace:
        return cfg.default_namespace

    return validio_cli.DEFAULT_NAMESPACE
