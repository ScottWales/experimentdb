"""
ORM model of the database
"""

from .experiment import all_subclasses
from .db import experiment
from .experiment.base import Experiment

import sqlalchemy.orm

# Set up ORM mappings for experiment subclasses
for c in all_subclasses(Experiment):
    if c.type is None:
        continue

    sqlalchemy.orm.mapper(
        c,
        experiment,
        polymorphic_on=experiment.c.type_id,
        polymorphic_identity=c.type,
    )
