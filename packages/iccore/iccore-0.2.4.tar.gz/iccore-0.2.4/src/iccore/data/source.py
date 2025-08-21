"""
A data source, such as a feed or sensor
"""

import logging
from pathlib import Path
import json

from pydantic import BaseModel

from iccore.filesystem import get_json_files

from .units import Unit

logger = logging.getLogger(__name__)


def load_model(path: Path, model_type):
    with open(path, "r", encoding="utf8") as f:
        data = json.load(f)
    return model_type(**data)


class Source(BaseModel, frozen=True):
    """
    A sensor has one or more datasources, it may be a piece of measurement equipment
    """

    name: str


def load(path: Path, units: list[Unit]) -> Source:
    """
    Load a source description from a json file.

    :param path: Path to the loading python source file.
    """
    logger.info("Loading %s", path)
    model = load_model(path.parent / (path.stem + ".json"), Source)
    return model


def load_all(path: Path, units: list[Unit]) -> list[Source]:
    """
    Load all sensor definition json files found in the provided
    directory.
    """
    return [load(f, units) for f in get_json_files(path)]
