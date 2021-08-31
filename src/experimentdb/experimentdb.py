from .config import read_config
from .model.experiment import experiment_factory, Experiment
import sqlalchemy.orm as sqo
import sqlalchemy as sqa
from . import db

import glob
import pandas
import logging
import os


class ExperimentDB:
    def __init__(self, config=None):
        self.config = read_config(config)
        self.db = db.connect(self.config)
        self.session = sqo.Session(self.db)

    def scan_all(self):
        for p in self.config["scan paths"]:
            self.scan(p["type"], p["path"])

    def scan(self, type, path):
        for p in glob.glob(os.path.expanduser(path)):
            try:
                logging.debug("scanning path %s", p)
                exp = (
                    self.session.query(Experiment).filter_by(type_id=type, path=p).one()
                )
            except sqo.exc.NoResultFound:
                exp = experiment_factory(type, p)

            exp.update()

            if len(exp.files) > 0:
                self.session.add(exp)
        self.session.commit()

    def experiments(self, *args, **kwargs):
        return pandas.read_sql(sqa.select(db.experiment), self.db, index_col="id")

    def search(self, *args, **kwargs):
        pass

    def open_datasets(self, *args, **kwargs):
        pass
