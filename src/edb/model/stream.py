import typing as T
from .file import File


class Stream:
    def __init__(self, name: str, files: T.List[File] = []):
        self.name = name
        self.files = files

    def identify_variables(self):
        if len(self.variables) == 0:
            self.variables = self.files[0].identify_variables()
