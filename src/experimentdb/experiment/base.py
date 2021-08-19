import os


class Experiment:
    type = None

    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path


class Generic(Experiment):
    type = "generic"
