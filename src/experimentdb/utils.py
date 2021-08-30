def all_subclasses(cls):
    """
    Recursively  list all subclasses of a given class
    """
    # https://stackoverflow.com/a/3862957
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )
