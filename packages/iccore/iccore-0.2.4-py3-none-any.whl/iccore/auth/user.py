from sqlmodel import SQLModel, Field

from iccore.database.models import BaseModelMixin


class UserBase(SQLModel):

    first_name: str | None = None
    surname: str | None = None
    email: str | None = None


class UserCreate(UserBase):
    name: str


class UserPublic(UserBase):
    name: str


class User(UserBase, BaseModelMixin, table=True):  # type: ignore

    name: str | None = Field(default=None, primary_key=True)
