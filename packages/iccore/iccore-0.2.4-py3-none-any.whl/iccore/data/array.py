from typing import Any

import numpy as np
from pydantic import BaseModel

from .units import UnitPublic, convert_unit


class Array(BaseModel, frozen=True):
    """
    An ordered collection of data all with the same quantity.
    """

    name: str
    data: Any

    def get_bounds(self):
        return self.data[0], self.data[-1]


def append_array(source: Array, new: Array) -> Array:
    return source.model_copy(update={"data": np.append(source.data, new.data, axis=0)})


def insert_array(source: Array, new: Array, idx: int) -> Array:
    return source.model_copy(
        update={"data": np.insert(source.data, idx, new.data, axis=0)}
    )


def convert(source: Array, source_unit: UnitPublic, target_unit: UnitPublic) -> Array:
    return source.model_copy(
        update={
            "data": [
                convert_unit(item, source_unit, target_unit) for item in source.data
            ]
        }
    )
