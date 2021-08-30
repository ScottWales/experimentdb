from __future__ import annotations

import os
import typing as T
import pathlib

if T.TYPE_CHECKING:
    from ..file import File
    from ..stream import Stream


class Experiment:
    type: T.Optional[str] = None

    def __init__(self, path: T.Union[str, pathlib.Path]):
        self.name: str = os.path.basename(path)
        self.path: str = str(path)

        self.files = self.find_files()
        self.streams = self.identify_streams(self.files)

    def find_files(self) -> T.Iterable[File]:
        """
        Find all files that are part of the experiment
        """
        return []

    def identify_streams(self, files: T.Iterable[File]) -> T.Dict[str, Stream]:
        """
        Group the listed files into streams containing similar variables
        """
        return {}
