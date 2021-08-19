"""
ExperimentDB database
"""


import sqlalchemy as sqa

engine: sqa.engine = None
metadata = sqa.MetaData()


def connect(config):
    """
    Connect to the database

    Args:
        config: from experimentdb.config.read_config()
    Returns:
        sqlalchemy.engine connected to the configured database
    """
    global engine
    if engine is None:
        engine = sqa.create_engine(config["database"])
        metadata.create_all(engine)
    return engine


"""
A single model run

name: Run name
path: Base path of the run
type: Experiment type, see experimentdb.experiment
"""
experiment = sqa.Table(
    "experiment",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("name", sqa.String, nullable=False),
    sqa.Column("path", sqa.Integer, nullable=False),
    sqa.Column("type", sqa.String, nullable=False),
)

"""
A stream of files with identical variables, but covering different times

The stream is made up of multiple files, found in the 'file' table

The stream is made up of multiple variables, present in all attached files,
found in the 'variable' table
"""
stream = sqa.Table(
    "stream",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("experiment_id", sqa.Integer),
    sqa.Column("time_units", sqa.String),
    sqa.Column("calendar", sqa.String),
)

"""
A single file in the stream

The file contains all the variables attached to the stream
"""
file = sqa.Table(
    "file",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("stream_id", sqa.Integer),
    sqa.Column("relative_path", sqa.String),
    sqa.Column("start_date", sqa.Float),
    sqa.Column("end_date", sqa.Float),
)

"""
A variable in the stream

The variable is expected to be present for all files in the same stream, with
each file covering a different date range
"""
variable = sqa.Table(
    "variable",
    metadata,
    sqa.Column("id", sqa.Integer, primary_key=True),
    sqa.Column("stream_id", sqa.Integer),
    sqa.Column("name", sqa.String, nullable=False, index=True),
    sqa.Column("standard_name", sqa.String, index=True),
    sqa.Column("method", sqa.String),
    sqa.Column("time_resolution", sqa.String),
    sqa.Column("lat_resolution", sqa.String),
    sqa.Column("lon_resolution", sqa.String),
    sqa.Column("units", sqa.String),
)
