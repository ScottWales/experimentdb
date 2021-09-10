"""
ExperimentDB SQLAlchemy database tables

These tables hold all of the data ExperimentDB knows about, and can be used for
manual searches
"""


import sqlalchemy as sqa

metadata = sqa.MetaData()


def connect(url):
    """
    Connect to the database

    Args:
        config: configuration data from :func:`experimentdb.config.read_config()`
    Returns:
        sqlalchemy.engine connected to the configured database
    """
    engine = sqa.create_engine(url)

    experiment.create(engine, checkfirst=True)
    stream.create(engine, checkfirst=True)
    variable.create(engine, checkfirst=True)
    file.create(engine, checkfirst=True)

    with engine.connect() as conn:
        r = conn.execute(sqa.text("PRAGMA table_info(variable_fts)")).fetchall()

        # Setup fts
        if len(r) == 0:
            commands = [
                """
                CREATE VIRTUAL TABLE variable_fts
                    USING fts5(
                        name, 
                        long_name, 
                        standard_name, 
                        tokenize = 'porter', 
                        content = variable,
                        content_rowid = id);
                """,
                """
                CREATE TRIGGER variable_fts_ai AFTER INSERT ON variable BEGIN
                INSERT INTO variable_fts (rowid, name, long_name, standard_name)
                    VALUES (new.id, new.name, new.long_name, new.standard_name);
                END;
                """,
                """
                CREATE TRIGGER variable_fts_ad AFTER DELETE ON variable BEGIN
                INSERT INTO variable_fts (rowid, name, long_name, standard_name)
                    VALUES ('delete', old.name, old.long_name, old.standard_name);
                END;
                """,
                """
                CREATE TRIGGER variable_fts_au AFTER UPDATE ON variable BEGIN
                INSERT INTO variable_fts (rowid, name, long_name, standard_name)
                    VALUES ('delete', old.name, old.long_name, old.standard_name);
                INSERT INTO variable_fts (rowid, name, long_name, standard_name)
                    VALUES (new.id, new.name, new.long_name, new.standard_name);
                END;
                """,
            ]

            for c in commands:
                conn.execute(sqa.text(c))

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
    sqa.Column("name", sqa.String, nullable=False),
    sqa.Column("time_units", sqa.String),
    sqa.Column("calendar", sqa.String),
    sqa.Column("last_seen", sqa.DateTime),
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
    sqa.Column("start_date", sqa.String),
    sqa.Column("end_date", sqa.String),
    sqa.Column("type_id", sqa.String, nullable=False),
    sqa.Column("last_seen", sqa.DateTime),
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
    sqa.Column("long_name", sqa.String),
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

variable_fts = sqa.Table(
    "variable_fts",
    metadata,
    sqa.Column("rowid", sqa.Integer, sqa.ForeignKey("variable.id")),
    sqa.Column("name", sqa.String),
    sqa.Column("long_name", sqa.String),
    sqa.Column("standard_name", sqa.String),
    sqa.Column("variable_fts", sqa.String),
)
