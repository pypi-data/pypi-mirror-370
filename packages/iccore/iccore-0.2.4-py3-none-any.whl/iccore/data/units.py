"""
Module for handling units and quantities
"""

# from __future__ import annotations

from pathlib import Path
import json
from datetime import date, datetime, timedelta

import numpy as np
from pydantic import BaseModel
from sqlmodel import SQLModel, Relationship, Field

from iccore.database.models import BaseModelMixin


class UnitBase(SQLModel):
    """
    A unit of measurement.

    The base field is the definition of the unit relative to SI base units.
    This is used for automatic unit conversion. The order is
    [s, m, kg, A, K, mol, cd].

    There are a number of special dimensionless units also:
     - dimensionless
     - percent

    :cvar name: A short name for the unit
    :cvar long_name: A longer name for the unit, as might be shown in a plot
    :cvar symbol: A symbol for the unit
    """

    name: str = Field(primary_key=True)
    long_name: str = ""
    symbol: str = ""


class Unit(UnitBase, BaseModelMixin, table=True):  # type: ignore

    base_powers: str
    base_factors: str
    base_offsets: str

    measurements: list["Measurement"] = Relationship(back_populates="unit")  # type: ignore # NOQA


class UnitCreate(UnitBase):

    base_powers: tuple[int, ...] = (0, 0, 0, 0, 0, 0, 0)
    base_factors: tuple[float, ...] = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    base_offsets: tuple[float, ...] = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def to_model(self) -> Unit:
        dumped = self.model_dump()
        dumped["base_powers"] = ",".join(str(p) for p in self.base_powers)
        dumped["base_factors"] = ",".join(str(f) for f in self.base_factors)
        dumped["base_offsets"] = ",".join(str(f) for f in self.base_offsets)
        return Unit.model_validate(dumped)


class UnitPublic(UnitBase):

    base_powers: tuple[int, ...]
    base_factors: tuple[float, ...]
    base_offsets: tuple[float, ...]

    @staticmethod
    def from_model(model: Unit) -> "UnitPublic":
        dumped = model.model_dump()
        dumped["base_powers"] = tuple(dumped["base_powers"].split(","))
        dumped["base_factors"] = tuple(dumped["base_factors"].split(","))
        dumped["base_offsets"] = tuple(dumped["base_offsets"].split(","))
        return UnitPublic.model_validate(dumped)

    def get_long_name(self) -> str:
        if self.long_name:
            return self.long_name
        return self.name


def convert_unit(item, source: UnitPublic, target: UnitPublic):

    if source == target:
        return item

    if source.base_powers != target.base_powers:
        raise RuntimeError("Incompatible unit base powers - can't convert")

    # Convert to base units
    for f, p in zip(source.base_factors, source.base_powers):
        if p == 0:
            continue
        if p >= 1:
            item = item * f
        if p <= -1:
            item = item * (1.0 / f)

    for offset in source.base_offsets:
        item += offset

    # Convert to target units
    for f, p in zip(target.base_factors, target.base_powers):
        if p == 0:
            continue
        if p >= 1:
            item = item * f
        if p <= -1:
            item = item * (1.0 / f)

    for offset in target.base_offsets:
        item += offset

    return item


def load_default_units() -> list[UnitCreate]:
    return load_units(Path(__file__).parent / "units.json")


def load_units(path: Path) -> list[UnitCreate]:
    """
    Load a unit definition file from the provided path
    """
    with open(path, "r", encoding="utf8") as f:
        data = json.load(f)

    return [UnitCreate(**u) for u in data["items"]]


class DateRange(BaseModel, frozen=True):
    """
    A date range, useful for defining the extents of a time series
    """

    start: date | None
    end: date | None

    def as_tuple(self) -> tuple[date | None, ...]:
        return self.start, self.end


def to_python_datetime(np_datetime):
    unix_epoch = np.datetime64(0, "s")
    one_second = np.timedelta64(1, "s")
    seconds_since_epoch = (np_datetime - unix_epoch) / one_second
    return datetime.utcfromtimestamp(seconds_since_epoch)


def timestamp_from_seconds_since(count, relative_to: str):
    reference = datetime.fromisoformat(relative_to)
    reference += timedelta(seconds=count)
    return reference


def to_date_str(date_item: date):
    return f"{date_item.year}-{date_item.month}-{date_item.day}"


def to_timestamps(times, since: str):
    return [timestamp_from_seconds_since(int(t), since) for t in times]
