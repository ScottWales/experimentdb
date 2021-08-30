import typing as T
from .file import File


class Stream:
    def __init__(self, name: str, files: T.List[File]):
        self.name = name
        self.files = files
