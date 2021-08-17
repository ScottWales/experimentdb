from .config import read_config


class ExperimentDB:
    def __init__(self, config=None):
        self.config = read_config(config)
        self.db = None

    def experiments(self, *args, **kwargs):
        pass

    def search(self, *args, **kwargs):
        pass

    def open_datasets(self, *args, **kwargs):
        pass
