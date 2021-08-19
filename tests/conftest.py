from experimentdb.db import metadata

import pytest
import sqlalchemy as sqa


@pytest.fixture(scope="session")
def db():
    engine = sqa.create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    with engine.connect() as c:
        yield c


@pytest.fixture()
def conn(db):
    with db.begin() as t:
        yield db
        t.rollback()
