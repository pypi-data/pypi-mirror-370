from pathlib import Path
from typing import Any

from pydantic import BaseModel


class BaseComputationalModel(BaseModel, frozen=True):

    name: str
    type: str | None = None
    framework: str | None = None
    location: Path | None = None


class ComputationalModelCreate(BaseComputationalModel, frozen=True):

    parameters: dict[str, Any]
