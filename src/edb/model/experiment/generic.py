from .base import Experiment
from ..file import File, NCFile
from ..stream import Stream

import os
import typing as T
import logging


class Generic(Experiment):
    type = "generic"
    description = "Generic NetCDF output"

    def __init__(self, path):
        super().__init__(path)

    def find_files(self) -> T.Iterator[File]:
        for root, dir, files in os.walk(self.path):
            for f in files:
                if not f.endswith(".nc"):
                    # Ignore non-netcdf files
                    continue

                p = os.path.join(root, f)
                relp = os.path.relpath(p, self.path)
                outf = None

                # Is the file already known?
                for ef in self.files:
                    if ef.relative_path == relp:
                        logging.debug("existing file %s", relp)
                        outf = ef

                # Not already known
                if outf is None:
                    logging.debug("new file %s", relp)
                    outf = NCFile(p, self)

                # Yield the found file
                yield outf

    def identify_stream(self, file: File) -> str:
        return file.relative_path
