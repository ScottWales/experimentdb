from __future__ import annotations

import xarray


class Variable:
    name: str
    standard_name: str
    long_name: str
    method: str
    time_resolution: str
    lat_resolution: str
    lon_resolution: str
    units: str

    def __init__(self):
        pass

    @classmethod
    def from_iris(cls, cube, stashmaster=None) -> Variable:
        """
        Create a Variable from an iris Cube

        Args:
            cube iris.Cube: Source cube
            stashmaster: mule.stashmaster.STASHmaster with variable metadata
        """
        v = cls()

        stash = cube.attributes.get("STASH", None)

        if stash is not None:
            v.name = str(cube.attributes["STASH"])
        else:
            v.name = cube.name

        if stashmaster is not None and stash is not None:
            v.long_name = stashmaster[stash.lbuser3()]
        else:
            v.long_name = cube.long_name

        v.standard_name = cube.standard_name
        v.units = str(cube.units)
        v.method = " ".join(str(m) for m in cube.cell_methods)

        return v

    @classmethod
    def from_xarray(cls, da: xarray.DataArray) -> Variable:
        v = cls()
        return v
