from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from sqlmodel import Session, select

from .database import get_db_engine


class BaseModelMixin:

    def save(self, session: Session | None = None):
        if session:
            session.add(self)
        else:
            with Session(get_db_engine()) as session:
                session.add(self)
                session.commit()

    @classmethod
    def delete_item(cls, id: int | str, key: str = "id"):

        with Session(get_db_engine()) as session:
            stmt = select(cls).where(getattr(cls, key) == id)
            item = session.exec(stmt).one()
            session.delete(item)
            session.commit()

    @classmethod
    def _object_exec(
        cls, statement, session: Session, return_t=None, fail_on_none: bool = True
    ):

        instance = session.exec(statement).first()
        if fail_on_none and not instance:
            raise RuntimeError(f"Requested instance not found: {statement}.")

        if return_t:
            to_model_op = getattr(return_t, "from_model", None)
            if to_model_op and callable(to_model_op):
                instance = to_model_op(instance)
            else:
                instance = return_t.model_validate(instance)
        return instance

    @classmethod
    def _object(
        cls,
        key: str,
        attr: str,
        session: Session,
        return_t=None,
        fail_on_none: bool = True,
    ):
        stmt = select(cls).where(getattr(cls, attr) == key)
        return cls._object_exec(stmt, session, return_t, fail_on_none)

    @classmethod
    def object(
        cls,
        key: str,
        attr: str = "id",
        session: Session | None = None,
        return_t=None,
        fail_on_none: bool = True,
    ):
        if session:
            return cls._object(key, attr, session, return_t, fail_on_none)

        with Session(get_db_engine()) as session:
            return cls._object(key, attr, session, return_t, fail_on_none)

    @classmethod
    def _object_multiarg(
        cls, keys: list[str], attrs: list[str], session: Session, return_t=None
    ):
        stmt = select(cls)
        for key, attr in zip(keys, attrs):
            stmt = stmt.where(getattr(cls, attr) == key)

        return cls._object_exec(stmt, session, return_t)

    @classmethod
    def object_multiarg(
        cls,
        keys: list[str],
        attrs: list[str],
        session: Session | None = None,
        return_t=None,
    ):
        if session:
            return cls._object_multiarg(keys, attrs, session, return_t)

        with Session(get_db_engine()) as session:
            return cls._object_multiarg(keys, attrs, session, return_t)

    @classmethod
    def objects(cls, session: Session | None = None):
        stmt = select(cls)
        with Session(get_db_engine()) as session:
            instances = list(session.exec(stmt))
        return instances


class Timestamped(BaseModel):

    created_at: datetime | None = None
    updated_at: datetime | None = None


class TimestampedModelMixin(BaseModelMixin, Timestamped):

    def save(self, session: Session | None = None):

        if not self.created_at:
            self.created_at = datetime.now()

        self.updated_at = datetime.now()
        super().save(session)
