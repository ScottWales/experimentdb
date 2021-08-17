import sqlalchemy as sqa

engine = None
metadata = sqa.MetaData()


def connect(config):
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
    sqa.Column("type", sqa.String, nullable=False),
)
