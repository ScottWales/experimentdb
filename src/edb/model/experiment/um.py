from .base import Experiment
from ..file import File, file_factory
from ..stream import Stream

import os
import logging
from glob import glob

import typing as T


class UMRose(Experiment):
    type = "um-rose"
    file_pattern = "share/data/History_Data/*"

    def __init__(self, path):
        super().__init__(path)

    def find_files(self) -> T.Iterator[File]:
        """
        Finds files in a Rose run
        """

        os.environ["UMDIR"] = "/g/data/access/projects/access/umdir"
        yield from super().find_files()

    def identify_stream(self, file) -> str:
        """
        Group files into streams with the same variables
        """
        return os.path.basename(file.relative_path)[:9]

    def find_variables(self, file):
        """
        Find the variables in a single file

        Since all files in a stream share the same variable, this only needs to
        be run once per stream
        """
        import iris

        cubes = iris.load(os.path.join(self.path, file))

        results = [str(c.attributes["STASH"]) for c in cubes]

        return results


class UMUMUI(Experiment):
    type = "um-umui"
