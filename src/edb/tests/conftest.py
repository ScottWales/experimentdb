from ..model import variable
from ..db import metadata
from ..model import experiment_factory
from ..model.file import UMFile
from ..model.variable import Variable

import pytest
import sqlalchemy as sqa
import sqlalchemy.orm


@pytest.fixture(scope="session")
def db():
    engine = sqa.create_engine("sqlite+pysqlite:///:memory:", echo=False)
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


def setup_sample_data(session):
    """
    Sets up some sample data to use in the readme file
    """
    expa = experiment_factory(
        path="/scratch/w35/saw562/cylc-run/u-ab123", type="um-rose"
    )
    expa.files.append(UMFile("share/data/History_Data/ab123a.pa1980jan", expa))
    expa.files.append(UMFile("share/data/History_Data/ab123a.pa1980feb", expa))

    expa.collect_streams(expa.files)

    stream = expa.streams["ab123a.pa"]

    v = Variable()
    v.name = "T"
    v.standard_name = "temperature"
    v.frequency = "1M"
    stream.variables.append(v)

    v = Variable()
    v.name = "U"
    stream.variables.append(v)

    v = Variable()
    v.name = "V"
    stream.variables.append(v)

    session.add(expa)

    session.commit()
