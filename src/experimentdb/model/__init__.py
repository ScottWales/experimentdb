"""
ORM model of the database
"""
from ..utils import all_subclasses
from .experiment.base import Experiment

import sqlalchemy.orm as sqo
import sqlalchemy as sqa
import pathlib
import typing as T
import os

from .file import File
from .stream import Stream

from ..db import experiment, stream, file

# Set up ORM mappings for file types
sqo.mapper(
    File,
    file,
    polymorphic_on=file.c.type_id,
    polymorphic_identity=None,
    properties={"stream": sqo.relationship(Stream, back_populates="files")},
)
for c in all_subclasses(File):
    if c.type is None:
        continue

    sqo.mapper(
        c,
        file,
        polymorphic_on=file.c.type_id,
        polymorphic_identity=c.type,
        inherits=File,
    )

sqo.mapper(
    Stream,
    stream,
    properties={
        "experiment": sqo.relationship(Experiment, back_populates="streams"),
        "files": sqo.relationship(
            File,
            back_populates="stream",
        ),
    },
)

# Set up ORM mappings for experiment subclasses
sqo.mapper(
    Experiment,
    experiment,
    polymorphic_on=experiment.c.type_id,
    polymorphic_identity=None,
    properties={
        "streams": sqo.relationship(
            Stream,
            back_populates="experiment",
            collection_class=sqo.collections.attribute_mapped_collection("name"),
        )
    },
)
for c in all_subclasses(Experiment):
    if c.type is None:
        continue

    sqo.mapper(
        c,
        experiment,
        polymorphic_on=experiment.c.type_id,
        polymorphic_identity=c.type,
        inherits=Experiment,
    )
