from __future__ import annotations

import pathlib
import typing as T
import os

if T.TYPE_CHECKING:
    from .experiment.base import Experiment


class File:
    type: T.Optional[str] = None

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


class NCFile(File):
    type = "netcdf"

    def __init__(self, path: T.Union[str, pathlib.Path], exp: Experiment):
        super().__init__(path, exp)


class UMFile(File):
    type = "um_generic"

    def __init__(self, path: T.Union[str, pathlib.Path], exp: Experiment):
        super().__init__(path, exp)
