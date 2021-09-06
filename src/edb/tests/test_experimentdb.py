from ..experimentdb import ExperimentDB
import sqlalchemy as sqa
from .. import db
import pytest
from unittest.mock import patch
import xarray
import numpy


@pytest.fixture
def sample_generic(conn):
    # Set up an experiment with a netcdf file
    conn.execute(
        db.experiment.insert().values(id=1, name="foo", type_id="generic", path="/foo")
    )
    conn.execute(db.stream.insert().values(id=1, experiment_id=1, name="foo"))
    conn.execute(
        db.file.insert().values(
            id=1, stream_id=1, experiment_id=1, type_id="netcdf", relative_path="foo.nc"
        )
    )
    conn.execute(
        db.variable.insert(),
        [
            {"id": 5, "stream_id": 1, "name": "T", "standard_name": "temperature"},
            {"id": 6, "stream_id": 1, "name": "U", "standard_name": "u_wind"},
        ],
    )


def test_search(conn, sample_generic):

    edb = ExperimentDB(conn=conn)

    r = edb.search(standard_name="temperature")

    # 1 variable found
    assert len(r) == 1

    # Index is the variable id from the DB
    assert r.index[0] == 5


def test_open_dataarrays(conn, sample_generic):

    edb = ExperimentDB(conn=conn)

    sample = xarray.Dataset(
        {
            "T": (("time", "lat", "lon"), numpy.zeros((10, 10, 10))),
            "U": (("time", "lat", "lon"), numpy.zeros((10, 10, 10))),
        }
    )

    with patch("xarray.open_dataset", return_value=sample) as p:
        r = edb.open_dataarrays(standard_name="temperature")

        # 1 variable found
        assert len(r) == 1

        # Index is the variable id from the DB
        assert r.index[0] == 5

        # Correct path used in open_dataset
        p.assert_called_once_with("/foo/foo.nc")

        # Returned value is the 'temperature' from sample
        xarray.testing.assert_identical(r.iloc[0], sample["T"])
