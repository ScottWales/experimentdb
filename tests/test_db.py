from experimentdb.db import metadata, experiment

import pytest
import sqlalchemy as sqa


@pytest.fixture(scope="session")
def conn():
    engine = sqa.create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    with engine.connect() as c:
        with c.begin() as t:
            yield c
            t.rollback()


def test_experiment(conn):
    r = conn.execute(sqa.select(sqa.func.count()).select_from(experiment))
    assert r.one()[0] == 0

    r = conn.execute(
        sqa.insert(experiment).values(
            name="u-ab123", path="/scratch/foo", type="um-rose"
        )
    )

    r = conn.execute(sqa.select(sqa.func.count()).select_from(experiment))
    assert r.one()[0] == 1
