try:
    from experimentdb.experiment.um import UMRose
except ImportError:
    pass

import os
import pytest


@pytest.mark.skipif(
    not os.environ.get("HOSTNAME", "").endswith("nci.org.au"), reason="Only at NCI"
)
def test_um_find_files():
    exp = UMRose("/scratch/w35/saw562/cylc-run/u-cg447")

    assert exp.name == "u-cg447"

    files = exp.find_files()

    assert "share/data/History_Data/cg447a.p71850jan" in files


@pytest.mark.skipif(
    not os.environ.get("HOSTNAME", "").endswith("nci.org.au"), reason="Only at NCI"
)
def test_um_identify_streams():
    exp = UMRose("/scratch/w35/saw562/cylc-run/u-cg447")

    streams = exp.identify_streams(
        [
            "share/data/History_Data/cg447a.da18500102_00",
            "share/data/History_Data/cg447a.p71850jan",
            "share/data/History_Data/cg447a.p81850jan",
            "share/data/History_Data/cg447a.pd1850jan",
        ]
    )

    assert streams["cg447a.p7"] == ["share/data/History_Data/cg447a.p71850jan"]


@pytest.mark.skipif(
    not os.environ.get("HOSTNAME", "").endswith("nci.org.au"), reason="Only at NCI"
)
def test_um_find_variables():
    exp = UMRose("/scratch/w35/saw562/cylc-run/u-ce355")

    vars = exp.find_variables("share/data/History_Data/ce355a.pa1988sep")

    # UM variables are identified by STASH code
    assert "m01s05i270" in vars
