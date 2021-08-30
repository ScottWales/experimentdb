from experimentdb.db import experiment


import sqlalchemy as sqa


def test_experiment(conn):
    r = conn.execute(sqa.select([sqa.func.count()]).select_from(experiment))
    assert r.fetchone()[0] == 0

    r = conn.execute(
        sqa.insert(experiment).values(
            name="u-ab123", path="/scratch/foo", type_id="um-rose"
        )
    )

    r = conn.execute(sqa.select([sqa.func.count()]).select_from(experiment))
    assert r.fetchone()[0] == 1
