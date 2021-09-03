from ..db import experiment
from ..model.experiment import Experiment
from .conftest import setup_sample_data

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


def test_sample_data(session):
    setup_sample_data(session)

    exp = session.query(Experiment).filter_by(type_id="um-rose").one()
