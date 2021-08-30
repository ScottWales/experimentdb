from .base import Experiment
from ..file import File, NCFile
from ..stream import Stream

import os
import typing as T


class Generic(Experiment):
    type = "generic"

    def __init__(self, path):
        super().__init__(path)

    def find_files(self) -> T.Iterator[File]:
        for root, dir, files in os.walk(self.path):
            for f in files:
                if not f.endswith(".nc"):
                    # Ignore non-netcdf files
                    continue

                p = os.path.join(root, f)
                print(p)
                yield NCFile(p, self)

    def identify_streams(self, files: T.Iterable[File]) -> T.Dict[str, Stream]:
        streams = {f.relative_path: [f] for f in files}
        print(streams)

        return {k: Stream(k, v) for k, v in streams.items()}
