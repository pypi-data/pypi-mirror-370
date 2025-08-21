"""
A reference to some data that all has the same 'dataset type'.
"""

from __future__ import annotations

import json
from datetime import datetime

from sqlmodel import Field, SQLModel, Session, select, col

from iccore.database import get_db_engine
from iccore.database.models import Timestamped, TimestampedModelMixin


class DatasetBase(SQLModel):
    """
    An instance of a dataset, includes references to data and metadata

    :cvar id: A unique identifier
    :cvar product: A reference to a product or 'dataset type'
    :cvar format: The format such as an extension for a file source
    :cvar type_specs: Type hints for csv loader performance
    """

    file_format: str
    name: str = ""
    original_path: str = ""
    group_prefix: str = ""
    checksum: str = ""
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None


class DatasetCreate(DatasetBase):
    """
    An instance of a dataset, includes references to data and metadata

    :cvar type_specs: Type hints for csv loader performance
    """

    product: str

    type_specs: dict[str, str] = {}
    path_excludes: list[str] = []
    extension_includes: list[str] = []
    fields: dict[str, str] = {}


class DatasetPublic(DatasetBase, Timestamped):
    """
    An instance of a dataset, includes references to data and metadata

    :cvar type_specs: Type hints for csv loader performance
    """

    id: int
    product: str
    added_by: str

    type_specs: dict[str, str] = {}
    path_excludes: list[str] = []
    extension_includes: list[str] = []
    fields: dict[str, str]


class Dataset(TimestampedModelMixin, DatasetBase, table=True):

    id: int | None = Field(default=None, primary_key=True)
    product: str = Field(foreign_key="product.name", index=True)
    added_by: str | None = Field(default=None, foreign_key="user.name")

    type_specs: str = ""
    path_excludes: str = ""
    extension_includes: str = ""
    fields: str = ""

    @staticmethod
    def from_create(create_model: DatasetCreate):
        dumped_model = create_model.model_dump()
        dumped_model["fields"] = json.dumps(create_model.fields)
        dumped_model["type_specs"] = json.dumps(create_model.type_specs)
        dumped_model["path_excludes"] = ",".join(p for p in create_model.path_excludes)
        dumped_model["extension_includes"] = ",".join(
            p for p in create_model.extension_includes
        )
        return Dataset.model_validate(dumped_model)

    def to_public(self) -> DatasetPublic:
        model_dump = self.model_dump()
        model_dump["type_specs"] = json.loads(model_dump["type_specs"])
        model_dump["fields"] = json.loads(model_dump["fields"])
        model_dump["path_excludes"] = model_dump["path_excludes"].split(",")
        model_dump["extension_includes"] = model_dump["extension_includes"].split(",")
        return DatasetPublic.model_validate(model_dump)

    @staticmethod
    def select_by_product(
        product_name: str,
        start_datetime: datetime | None,
        end_datetime: datetime | None,
    ) -> list[DatasetPublic]:

        stmt = select(Dataset).where(Dataset.product == product_name)
        if start_datetime:
            stmt = stmt.where(col(Dataset.end_datetime) >= start_datetime)
        if end_datetime:
            stmt = stmt.where(col(Dataset.start_datetime) <= end_datetime)
        stmt = stmt.order_by(col(Dataset.start_datetime))

        with Session(get_db_engine()) as session:
            db_instances = session.exec(stmt)
            instances = [d.to_public() for d in db_instances]
        return instances
