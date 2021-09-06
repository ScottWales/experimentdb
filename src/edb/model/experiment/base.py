from __future__ import annotations

import os
import typing as T
import pathlib
from glob import glob
import logging
from ..file import file_factory
from datetime import datetime

from ..stream import Stream

if T.TYPE_CHECKING:
    from ..file import File


class Experiment:
    type: T.Optional[str] = None
    file_pattern = "*"

    def __init__(self, path: T.Union[str, pathlib.Path]):
        self.name: str = os.path.basename(path)
        self.path: str = str(path)
        self.files: T.List[File] = []
        self.streams: T.Dict[str, Stream] = {}

    def find_files(self) -> T.Iterable[File]:
        """
        Find all files that are part of the experiment
        """

        for path in glob(os.path.join(self.path, self.file_pattern)):
            rel = os.path.relpath(path, self.path)
            ff: T.Optional[File] = None
            for ef in self.files:
                if ef.relative_path == rel:
                    ff = ef
                    logging.debug("existing file %s", rel)

            if ff is None:
                ff = file_factory(rel, self)
                logging.debug("new file %s", rel)

            if ff is None:
                continue

            ff.last_seen = datetime.now()

            yield ff

    def collect_streams(self, files: T.Iterable[File]) -> T.Dict[str, Stream]:
        """
        Group the listed files into streams containing similar variables
        """

        for f in files:
            stream_name = self.identify_stream(f)

            stream = self.streams.get(stream_name)
            if stream is None:
                logging.debug("new stream %s", stream_name)
                stream = Stream(stream_name)
                self.streams[stream_name] = stream

            if f not in stream.files:
                logging.debug("adding to stream %s", stream_name)
                stream.files.append(f)

        return self.streams

    def update(self):
        """
        Update the experiment with the latest filesystem state
        """
        self.files = list(self.find_files())
        self.streams = self.collect_streams(self.files)

        for s in self.streams.values():
            if s.last_seen is None or (s.last_seen - datetime.now()).days > 30:
                s.identify_variables()
                s.last_seen = datetime.now()

    def identify_stream(self, file: File) -> str:
        """
        Returns the stream name of a file
        """
        pass
