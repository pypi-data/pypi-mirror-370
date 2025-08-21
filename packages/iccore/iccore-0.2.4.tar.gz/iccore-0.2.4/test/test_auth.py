from sqlmodel import Session, SQLModel, create_engine, select

from iccore.auth import User

from iccore.test_utils import get_test_output_dir


def test_user():

    user = User(
        name="my_user",
        first_name="First Name",
        surname="Surname",
        email="user@email.com",
    )

    output_dir = get_test_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{output_dir}/test.db")

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(user)
        session.commit()

    with Session(engine) as session:
        stmt = select(User).where(User.name == "my_user")

        db_user = session.exec(stmt).first()
        assert db_user.first_name == "First Name"
