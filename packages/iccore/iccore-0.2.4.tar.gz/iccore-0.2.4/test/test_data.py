import shutil
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

from iccore.test_utils import get_test_output_dir
from iccore.auth import User
from iccore.data.product import Product
from iccore.database import create_sqlite_engine, init_db


def setup_db(output_dir: Path | None):

    if output_dir and output_dir.exists():
        shutil.rmtree(output_dir)

    create_sqlite_engine(output_dir / "test.db" if output_dir else None)
    init_db()


def setup_user(engine) -> User:

    user = User(name="my_user")
    user.save()
    return User.object("my_user", "name")


def xtest_product():

    engine = setup_db(get_test_output_dir())

    user = setup_user(engine)

    product = Product(name="lidar_dbs", added_by=user.id)

    product.save()
    product = Product.object("lidar_dbs", "name")

    assert product.name == "lidar_dbs"
    assert product.added_by == user.id
