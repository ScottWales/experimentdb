from .config import read_config
from .db import connect
from .model.experiment import experiment_factory
import sqlalchemy.orm as sqo

import glob


class ExperimentDB:
    def __init__(self, config=None):
        self.config = read_config(config)
        self.db = connect(self.config)
        self.session = sqo.Session(self.db)

    def scan_all(self):
        for p in self.config["scan paths"]:
            self.scan(p["type"], p["path"])

    def scan(self, type, path):
        for p in glob.glob(path):
            exp = experiment_factory(type, p)
            self.session.add(exp)
            self.session.commit()

    def experiments(self, *args, **kwargs):
        pass

    def search(self, *args, **kwargs):
        pass

    def open_datasets(self, *args, **kwargs):
        pass
