from .base import Experiment
from ...utils import all_subclasses

# Import the subclasses so they're loaded
from . import accesscm, um, generic, payu


def experiment_factory(type: str, path: str) -> Experiment:
    """
    Try to create a 'type' Experiment at 'path'
    """

    # Each Experiment subclass has the type it's associated with as the parameter
    # 'type'. If it's an abstract class the type should be None
    types = {e.type: e for e in all_subclasses(Experiment) if e.type is not None}

    return types[type](path)
