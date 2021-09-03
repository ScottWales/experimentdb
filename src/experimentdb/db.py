"""
ExperimentDB SQLAlchemy database tables

These tables hold all of the data ExperimentDB knows about, and can be used for
manual searches
"""


import sqlalchemy as sqa

engine: sqa.engine = None
metadata = sqa.MetaData()


def connect(config):
    """
    Connect to the database

    Args:
        config: configuration data from :func:`experimentdb.config.read_config()`
    Returns:
        sqlalchemy.engine connected to the configured database
    """
    global engine
    if engine is None:
        engine = sqa.create_engine(config["database"])
        metadata.create_all(engine)
    return engine


experiment = sqa.Table(
    "experiment",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("name", sqa.String, nullable=False),
    sqa.Column("path", sqa.Integer, nullable=False),
    sqa.Column("type_id", sqa.String, nullable=False),
    sqa.UniqueConstraint("type_id", "path"),
)
"""
A single model run

:param name: Run name
:param path: Base path of the run
:param type_id: Experiment type, see :func:`experimentdb.model.experiment_factory`
"""

stream = sqa.Table(
    "stream",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("experiment_id", sqa.Integer, sqa.ForeignKey("experiment.id")),
    sqa.Column("name", sqa.String),
    sqa.Column("time_units", sqa.String),
    sqa.Column("calendar", sqa.String),
    sqa.UniqueConstraint("experiment_id", "name"),
)
"""
A stream of files with identical variables, but covering different times

The stream is made up of multiple files, found in the 'file' table

The stream is made up of multiple variables, present in all attached files,
found in the 'variable' table
"""

file = sqa.Table(
    "file",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("stream_id", sqa.Integer, sqa.ForeignKey("stream.id")),
    sqa.Column("experiment_id", sqa.Integer, sqa.ForeignKey("experiment.id")),
    sqa.Column("relative_path", sqa.String, nullable=False),
    sqa.Column("start_date", sqa.Float),
    sqa.Column("end_date", sqa.Float),
    sqa.Column("type_id", sqa.String, nullable=False),
    sqa.UniqueConstraint("stream_id", "relative_path"),
)
"""
A single file in the stream

The file contains all the variables attached to the stream
"""

variable = sqa.Table(
    "variable",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("stream_id", sqa.Integer, sqa.ForeignKey("stream.id")),
    sqa.Column("name", sqa.String, nullable=False, index=True),
    sqa.Column("standard_name", sqa.String, index=True),
    sqa.Column("method", sqa.String),
    sqa.Column("time_resolution", sqa.String),
    sqa.Column("lat_resolution", sqa.String),
    sqa.Column("lon_resolution", sqa.String),
    sqa.Column("units", sqa.String),
)
"""
A variable in the stream

The variable is expected to be present for all files in the same stream, with
each file covering a different date range
"""
