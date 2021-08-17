import sqlalchemy as sqa


def connect(url):
    engine = sqa.create_engine(url)
    return engine
