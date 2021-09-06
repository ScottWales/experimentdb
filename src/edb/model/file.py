from __future__ import annotations

import pathlib
import typing as T
import os
import logging

from .variable import Variable

if T.TYPE_CHECKING:
    from .experiment.base import Experiment


def file_factory(path: str, exp: Experiment) -> T.Optional[File]:
    if not os.path.isabs(path):
        path = os.path.join(exp.path, path)

    try:
        # UM file
        import mule

        mf = mule.load_umfile(path)
        return UMFile(path, exp)
    except:
        pass

    return None


class File:
    type: T.Optional[str] = None
    experiment: Experiment

    def __init__(
        self,
        path: T.Union[str, pathlib.Path],
        exp: Experiment,
    ):
        """
        A file in the experiment

        Arguments:
            path: Absolute or relative path to the file
        """
        if os.path.isabs(path):
            self.relative_path = os.path.relpath(path, exp.path)
        else:
            self.relative_path = str(path)

        self.experiment = exp

    def identify_variables(self) -> T.List[Variable]:
        """
        Returns the variables found in this file
        """
        return []


class NCFile(File):
    type = "netcdf"

    def __init__(self, path: T.Union[str, pathlib.Path], exp: Experiment):
        super().__init__(path, exp)


class UMFile(File):
    type = "um_generic"

    def __init__(self, path: T.Union[str, pathlib.Path], exp: Experiment):
        super().__init__(path, exp)

    def identify_variables(self) -> T.List[Variable]:
        logging.debug("identify_variables %s", self.relative_path)
        try:
            import iris
            import mule

            path = os.path.join(self.experiment.path, self.relative_path)
            mf = mule.load_umfile(path)
            stashmaster = mule.STASHmaster.from_umfile(mf)
            cubes = iris.load(path)

            return [Variable.from_iris(c, stashmaster=stashmaster) for c in cubes]
        except Exception as e:
            logging.warning(e)
            return []
