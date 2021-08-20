from experimentdb.db import metadata

import pytest
import sqlalchemy as sqa
import sqlalchemy.orm


@pytest.fixture(scope="session")
def db():
    engine = sqa.create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    with engine.connect() as c:
        yield c


@pytest.fixture()
def conn(db):
    """
    A DB connection

    Automatically rolled back
    """
    with db.begin() as t:
        yield db
        t.rollback()


@pytest.fixture()
def session(conn):
    """
    An ORM session

    Automatically rolled back
    """
    s = sqlalchemy.orm.Session(bind=conn)
    yield s
    s.close()
