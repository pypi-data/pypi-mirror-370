"""
This module handles conversion of objects to and from
string representations.
"""

from pathlib import Path
import logging
import json
import os

from pydantic import BaseModel

from iccore.filesystem import write_file
from iccore.runtime import ctx

logger = logging.getLogger(__name__)


def read_json(path: Path):
    """
    Read a json file from the provided path. Supports a runtime ctx,
    meaning it will no-op if the context doesn't support filesystem
    access.

    :param path: Path to the json file
    :type path: Path
    :return: The json content of the file.
    :rtype: Native Pyton json
    """

    if not ctx.can_read():
        ctx.add_cmd(f"read_json {path}")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(payload: dict, path: Path, indent: int = 4, make_parents: bool = True):
    """
    Write a dictionary to file in json format.

    :param payload: The payload to write to file
    :type payload: dict
    :param path: Path to the file to write to
    "type path: Path
    :param indent: Number of spaces to indent json entries with
    :param make_parents: Whether to create parent directories for the file
    """

    if not ctx.can_modify():
        ctx.add_cmd(f"write_json {path}")
        return

    if make_parents:
        os.makedirs(path.parent, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=indent)


def write_model(
    model: BaseModel, path: Path, indent: int = 4, make_parents: bool = True
):
    """
    Write a pydantic model to file in json format
    :param model: The model to write
    :param path: The path to write the model to
    :param indent: The number of spaces to indent the json by
    :param make_parents: Whether to automatically create parent directories
    """

    write_file(path, model.model_dump_json(indent=indent), make_parents)
