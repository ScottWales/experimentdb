import os
import typing as T


class Experiment:
    type: T.Optional[str] = None

    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path


class Generic(Experiment):
    type = "generic"
