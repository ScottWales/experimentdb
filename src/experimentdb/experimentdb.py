from .config import read_config
from .db import connect


class ExperimentDB:
    def __init__(self, config=None):
        self.config = read_config(config)
        self.db = connect(self.config)

    def scan(self, paths=None):
        pass

    def experiments(self, *args, **kwargs):
        pass

    def search(self, *args, **kwargs):
        pass

    def open_datasets(self, *args, **kwargs):
        pass
