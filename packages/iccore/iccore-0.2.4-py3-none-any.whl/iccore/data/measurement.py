"""
Module for a measureable quantity
"""

from sqlmodel import Field, SQLModel, Relationship

from iccore.database.models import BaseModelMixin

from .units import Unit, UnitPublic


class MeasurementBase(SQLModel):
    """
    A measurable quantity, including physical quantities

    :cvar name: A concise name or label
    :cvar unit: A measurement unit, default to dimensionless
    :cvar description: A description of the measurement
    :cvar long_name: A long name as might appear in a plot axis
    :cvar min_value: The minimal value to cutoff at
    :cvar max_value: The max value to cutoff at
    :cvar dates: Date range to cutoff values
    """

    name: str
    unit_name: str
    description: str = ""
    long_name: str = ""
    min_value: float | None = None
    max_value: float | None = None


class MeasurementCreate(MeasurementBase):
    pass


class Measurement(MeasurementBase, BaseModelMixin, table=True):

    id: int | None = Field(default=None, primary_key=True)
    unit_name: str = Field(foreign_key="unit.name")
    product_name: str = Field(foreign_key="product.name")
    unit: Unit = Relationship(back_populates="measurements")

    product: "Product" = Relationship(  # type: ignore  # NOQA
        back_populates="measurements",
        sa_relationship_kwargs={"foreign_keys": "Measurement.product_name"},
    )


class MeasurementPublic(MeasurementBase):
    id: int
    product_name: str

    @property
    def has_limits(self) -> bool:
        return (self.min_value is not None) and (self.max_value is not None)

    @property
    def limits(self) -> tuple[float | None, ...]:
        if not self.has_limits:
            raise ValueError("Requested limits but none set")
        return self.min_value, self.max_value

    def get_long_name(self) -> str:
        if self.long_name:
            return self.long_name

        spaced = " ".join(self.name.split("_"))
        return spaced.title()


class MeasurementPublicWithUnits(MeasurementPublic):

    unit: UnitPublic

    @classmethod
    def from_model(cls, model: Measurement):
        model_dump = model.model_dump()
        model_dump["unit"] = UnitPublic.from_model(model.unit)
        return cls.model_validate(model_dump)
