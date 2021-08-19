from .base import Experiment

# Import the subclasses so they're loaded
try:
    # Can only support UM if mule and iris are installed
    from . import accesscm, um
except ImportError:
    pass


def all_subclasses(cls):
    """
    Recursively  list all subclasses of a given class
    """
    # https://stackoverflow.com/a/3862957
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


def experiment_factory(type: str, path: str) -> Experiment:
    """
    Try to create a 'type' Experiment at 'path'
    """

    # Each Experiment subclass has the type it's associated with as the parameter
    # 'type'. If it's an abstract class the type should be None
    types = {e.type: e for e in all_subclasses(Experiment) if e.type is not None}

    return types[type](path)
