"""
A product is a 'dataset type'. Its specification allows loading a
dataset in a standard format.
"""

# from __future__ import annotations

from sqlmodel import SQLModel, Relationship, Field

from iccore.auth import User, UserPublic  # NOQA
from iccore.database.models import Timestamped, TimestampedModelMixin

from .measurement import (
    Measurement,
    MeasurementCreate,
    MeasurementPublicWithUnits,
)  # NOQA


class ProductBase(SQLModel):
    """
    A 'dataset type' to allow dataset content loading into a standard format.

    :cvar name: A concise name or label
    :cvar description: A longer description
    :cvar measurements: Readings taken from a sensor
    :cvar x: Description of the x or index values
    :cvar y: Optional 'y' values for 2d datasets
    """

    name: str = Field(primary_key=True)
    description: str = ""
    license: str = ""


class ProductCreateNoMeasurements(ProductBase):

    x: str | None = None
    y: str | None = None


class ProductCreate(ProductCreateNoMeasurements):

    measurements: list[MeasurementCreate]


class Product(ProductBase, TimestampedModelMixin, table=True):

    added_by: str | None = Field(default=None, foreign_key="user.name")
    x: str | None = None
    y: str | None = None
    measurements: list["Measurement"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"foreign_keys": "Measurement.product_name"},
    )

    @staticmethod
    def from_create(create_model: ProductCreate):

        model_base = ProductCreateNoMeasurements.model_validate(create_model)
        db_model = Product.model_validate(model_base)

        m_dumps = [m.model_dump() for m in create_model.measurements]
        for m in m_dumps:
            m["product_name"] = create_model.name

        db_model.measurements = [Measurement.model_validate(m) for m in m_dumps]
        return db_model


class ProductPublic(ProductBase, Timestamped):

    added_by: str
    x: str | None
    y: str | None


class ProductPublicWithMeasurements(ProductBase):
    added_by: str
    measurements: list[MeasurementPublicWithUnits]

    x: MeasurementPublicWithUnits | None
    y: MeasurementPublicWithUnits | None

    @classmethod
    def from_model(cls, model: Product) -> "ProductPublicWithMeasurements":
        model_dump = model.model_dump()

        if model_dump["x"] or model_dump["y"]:
            for m in model.measurements:
                if model_dump["x"] and m.name == model_dump["x"]:
                    model_dump["x"] = MeasurementPublicWithUnits.from_model(m)
                if model_dump["y"] and m.name == model_dump["y"]:
                    model_dump["y"] = MeasurementPublicWithUnits.from_model(m)

        model_dump["measurements"] = [
            MeasurementPublicWithUnits.from_model(m) for m in model.measurements
        ]

        return cls.model_validate(model_dump)

    def get_measurement(self, name: str) -> MeasurementPublicWithUnits:
        for m in self.measurements:
            if m.name == name:
                return m
        raise ValueError("Requested measurement not found in product")
