"""
A collection of values of type described by an associated quantity.
"""

from pydantic import BaseModel

from .array import Array, append_array, convert


class Series(BaseModel):
    """
    A collection of arrays, each with the same quantity.

    :cvar x: The x axis values correspond to the values
    :cvar y: Optional extra values for 2d series (e.g. height)
    """

    values: list[Array] = []
    x: str | None = None
    y: str | None = None
    name: str = ""

    def get_array(self, name: str) -> Array:
        for v in self.values:
            if v.name == name:
                return v
        raise ValueError("No array with name found")

    def get_x_array(self) -> Array:
        if not self.x:
            raise RuntimeError("Series has no x dimension")
        return self.get_array(self.x)

    def get_y_array(self) -> Array:
        if not self.y:
            raise RuntimeError("Series has no y dimension")
        return self.get_array(self.y)

    def get_x_bounds(self):
        return self.get_x_array().get_bounds()


def insert_series(source: Series, new: Series) -> Series:

    values = []
    for s, n in zip(source.values, new.values):
        if s.name != source.y:
            values.append(append_array(s, n))
        else:
            values.append(s)

    return source.model_copy(update={"values": values})


def filter_on_names(source: Series, names: list[str]) -> Series:

    retained = []
    if source.x:
        retained.append(source.get_array(source.x))
    if source.y:
        retained.append(source.get_array(source.y))
    retained.extend([source.get_array(n) for n in names])
    return source.model_copy(update={"values": retained})


def convert_units(source: Series, conversions: tuple) -> Series:

    values = []
    for v in source.values:
        found = False
        for name, unit_from, unit_to in conversions:
            if v.name == name:
                values.append(convert(v, unit_from, unit_to))
                found = True
                break
        if not found:
            values.append(v)
    return source.model_copy(update={"values": values})


def filter_on_range():
    pass
