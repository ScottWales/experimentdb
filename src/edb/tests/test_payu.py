from ..model.experiment.payu import Payu
from ..model.file import NCFile
import pytest
import os


@pytest.mark.skipif(
    not os.environ.get("HOSTNAME", "").endswith("nci.org.au"), reason="Only at NCI"
)
def test_payu_find_files():
    exp = Payu("/g/data3/hh5/tmp/cosima/access-om2-01/01deg_jra55v13_ryf8485_spinup6")

    # Name defaults to directory name
    assert exp.name == "01deg_jra55v13_ryf8485_spinup6"

    files = list(exp.find_files())

    # Finds ocean files
    assert "output414/ocean/ocean.nc" in [f.relative_path for f in files]

    # Finds ice files
    assert "output414/ice/OUTPUT/iceh.1937-03.nc" in [f.relative_path for f in files]


def test_payu_identify_streams():
    exp = Payu("/g/data3/hh5/tmp/cosima/access-om2-01/01deg_jra55v13_ryf8485_spinup6")

    tests = {
        "ocean": "output414/ocean/ocean.nc",
        "ocean_grid": "output414/ocean/ocean_grid.nc",
        "ocean_month": "output414/ocean/ocean_month.nc",
        "ocean_scalar": "output414/ocean/ocean_scalar.nc",
        "iceh": "output414/ice/OUTPUT/iceh.1937-03.nc",
        "iceh_daily": "output414/ice/OUTPUT/iceh.1937-03-daily.nc",
    }

    for expect, sample in tests.items():
        assert exp.identify_stream(NCFile(sample, exp)) == expect
