try:
    from ..model.experiment.um import UMRose
except ImportError:
    pass

import os
import pytest
from ..model.file import UMFile


@pytest.mark.skipif(
    not os.environ.get("HOSTNAME", "").endswith("nci.org.au"), reason="Only at NCI"
)
def test_um_find_files():
    exp = UMRose("/scratch/w35/saw562/cylc-run/u-cg447")

    assert exp.name == "u-cg447"

    files = exp.find_files()

    assert "share/data/History_Data/cg447a.p71850jan" in [
        f.relative_path for f in files
    ]


@pytest.mark.skipif(
    not os.environ.get("HOSTNAME", "").endswith("nci.org.au"), reason="Only at NCI"
)
def test_um_identify_streams():
    exp = UMRose("/scratch/w35/saw562/cylc-run/u-cg447")

    assert "cg447a.p7" == exp.identify_stream(
        UMFile("share/data/History_Data/cg447a.p71850jan", exp)
    )


@pytest.mark.skipif(
    not os.environ.get("HOSTNAME", "").endswith("nci.org.au"), reason="Only at NCI"
)
def test_um_identify_variables():
    exp = UMRose("/scratch/w35/saw562/cylc-run/u-ce355")
    file = UMFile("share/data/History_Data/ce355a.pa1988sep", exp)

    vs = file.identify_variables()

    assert "m01s05i270" in [v.name for v in vs]

    v = {v.name: v for v in vs}["m01s05i270"]
    assert v.long_name == "SHALLOW CONVECTION INDICATOR"  # Variable name in STASH
    assert v.method == "mean: time (1 hour)"
