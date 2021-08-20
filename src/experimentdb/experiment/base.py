import os
import typing as T
import pathlib


class Experiment:
    type: T.Optional[str] = None

    def __init__(self, path: T.Union[str, pathlib.Path]):
        self.name: str = os.path.basename(path)
        self.path: str = str(path)


class Generic(Experiment):
    type = "generic"

    def __init__(self, path):
        super().__init__(path)
