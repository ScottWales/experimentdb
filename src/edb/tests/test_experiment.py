from ..model.experiment import experiment_factory
from ..model.experiment.generic import Generic
import xarray
import numpy


def test_experiment_generic(session, tmp_path):
    ds = xarray.DataArray(
        numpy.zeros((10, 10, 10)), dims=["time", "latitude", "longitude"], name="foo"
    )
    ds.to_netcdf(tmp_path / "foo_1234.nc")

    exp = Generic(tmp_path)
    assert exp.type == "generic"

    # Scan the directory
    exp.update()
    session.add(exp)
    session.commit()

    assert exp.id is not None
    assert len(exp.streams) == 1
    assert len(exp.files) == 1

    # Rescan a second time
    exp.update()
    session.add(exp)
    session.commit()

    assert len(exp.streams) == 1
    assert len(exp.files) == 1


def test_experiment_factory():
    exp = experiment_factory("generic", "")
    assert exp.type == "generic"

    exp = experiment_factory("access-cm-payu", "")
    assert exp.type == "access-cm-payu"
