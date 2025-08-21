from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import create_engine, SQLModel


_SHARED_DB_ENGINE: Engine | None = None


def set_shared_db_engine(engine: Engine):
    global _SHARED_DB_ENGINE
    _SHARED_DB_ENGINE = engine


def get_db_engine() -> Engine:
    if not _SHARED_DB_ENGINE:
        raise RuntimeError("No DB Engine created or set")
    return _SHARED_DB_ENGINE


def init_db():
    if not _SHARED_DB_ENGINE:
        raise RuntimeError("No DB Engine created or set")
    SQLModel.metadata.create_all(_SHARED_DB_ENGINE)


def create_sqlite_engine(db_path: Path | None, connect_args: dict | None):

    if not connect_args:
        connect_args = {}

    if db_path is not None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(f"sqlite:///{db_path}", connect_args=connect_args)
    else:
        engine = create_engine("sqlite://", connect_args=connect_args)

    set_shared_db_engine(engine)


def create_db_engine(db_url: str, connect_args: dict | None):
    if not connect_args:
        connect_args = {}

    engine = create_engine(db_url, connect_args=connect_args)
    set_shared_db_engine(engine)
