from __future__ import annotations

import iris
import xarray
import logging


class Variable:
    name: str
    standard_name: str
    method: str
    time_resolution: str
    lat_resolution: str
    lon_resolution: str
    units: str

    def __init__(self):
        pass

    @classmethod
    def from_iris(cls, cube: iris.Cube) -> Variable:
        v = cls()
        v.name = str(cube.attributes["STASH"])
        v.standard_name = cube.standard_name
        v.units = str(cube.units)
        return v

    @classmethod
    def from_xarray(cls, da: xarray.DataArray) -> Variable:
        v = cls()
        return v
