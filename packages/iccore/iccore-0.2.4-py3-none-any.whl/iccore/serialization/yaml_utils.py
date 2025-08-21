"""
This module is for handling yaml reading and writing from file
"""

from pathlib import Path
import os
import logging
from typing import Type

import yaml
from pydantic import BaseModel

from iccore.runtime import ctx

logger = logging.getLogger(__name__)


def read_yaml(path: Path) -> dict:
    """
    Read yaml from the provided path
    """

    if not ctx.can_read():
        ctx.add_cmd(f"read_yaml {path}")
        return {}

    with open(path, "r", encoding="utf-8") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            logging.error("Yaml exception: %s", e)
            raise e


def write_yaml(path: Path, content: dict):
    """
    Write yaml to the specified path
    """
    os.makedirs(path.parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(content, f)


def write_model_yaml(path: Path, model: BaseModel):
    write_yaml(path, model.model_dump())


def read_model_yaml(path: Path, model_type: Type) -> BaseModel:
    return model_type(**read_yaml(path))
