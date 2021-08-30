try:
    from experimentdb.model.experiment.um import UMRose
except ImportError:
    pass

import os
import pytest
from experimentdb.model.file import UMFile


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

    streams = exp.identify_streams(
        [
            UMFile(f, exp)
            for f in [
                "share/data/History_Data/cg447a.da18500102_00",
                "share/data/History_Data/cg447a.p71850jan",
                "share/data/History_Data/cg447a.p81850jan",
                "share/data/History_Data/cg447a.pd1850jan",
            ]
        ]
    )

    assert "share/data/History_Data/cg447a.p71850jan" in [
        f.relative_path for f in streams["cg447a.p7"].files
    ]
