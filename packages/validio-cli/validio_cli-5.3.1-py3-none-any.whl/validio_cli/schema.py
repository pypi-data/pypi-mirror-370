"""
Manage JTD schemas.

This module will expose schemas and allow the user to edit them before attaching
to the source.
"""

import json
import os
import tempfile
from subprocess import call
from typing import Any

EDITOR = os.environ.get("EDITOR", "vim")


def edit(original: dict[str, Any]) -> dict[str, Any]:
    """
    Edit a dictionary with your configured EDITOR.

    Serialize the passed dictionary and open it with your configured EDITOR
    (default to `vim`). After saving the file it will be read back with
    potential changes and returned after being deserialized.

    :param original: The original dictionary
    :returns: The modified dictionary after the caller saved the file
    """
    original_as_str = json.dumps(original, indent=2)

    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(str.encode(original_as_str))
        tf.flush()

        command = [EDITOR, tf.name]

        # vim will move the old file aside and write to a new file in some cases
        # which will make the original file handle open not changed. If the
        # editor is of vim flavour we can add the backupcopy flag to prevent
        # this.
        if EDITOR in ["vi", "vim", "nvim"]:
            command.insert(1, "+set backupcopy=yes")

        call(command)

        tf.seek(0)
        edited_value = tf.read()

    return json.loads(edited_value)
