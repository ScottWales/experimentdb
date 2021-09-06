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
    """
    A database of numerical climate & weather experiments

    - Add directories to the database with :meth:`scan()` or :meth:`scan_all()`
    - List known experiments with :meth:`experiments()`
    - Search for output variables with :meth:`search()`
    - Open variables with :meth:`open_datasets()`
    """

    def __init__(self, config=None):
        """
        Connect to the database

        Args:
            config: Path to configuration file (see :func:`read_config()`)
        """
        self.config = read_config(config)
        self.db = db.connect(self.config)
        self.session = sqo.Session(self.db)

    def scan_all(self):
        """
        Scan all the paths listed in the config file

        It's expected that these paths will be globs, so doing a scan will find
        any new experiments
        """
        for p in self.config["scan paths"]:
            self.scan(p["type"], p["path"])

    def scan(self, type: str, path: str):
        """
        Scan a path glob for new experiments, adding newly found experiments to
        the database and updating already known experiments

        Args:
            type: Experiment type name (see :func:`experiment_factory`)
            path: Path glob to scan
        """
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

    def experiments(self) -> pandas.DataFrame:
        """
        List the known experiments in the database
        """
        return pandas.read_sql(sqa.select([db.experiment]), self.db, index_col="id")

    def query(self, *args) -> sqo.Query:
        """
        Perform an ORM query on the database, using the models from experimentdb.model

        Args:
            As sqlalchemy.orm.Session().query()
        """
        return self.session.query(*args)

    def search(
        self, /, experiment: str = None, standard_name: str = None, freq: str = None
    ) -> pandas.DataFrame:
        """
        Perform a search on the database

        Args:
            experiment: Experiment name
            standard_name: Standard name of variable
            freq: Variable output frequency
        """
        sel = sqa.select(
            [
                db.experiment.c.name.label("experiment"),
                db.stream.c.name.label("stream"),
                db.variable.c.name.label("variable"),
                db.variable.c.id,
            ]
        ).select_from(db.experiment.join(db.stream).join(db.variable))

        if standard_name is not None:
            sel = sel.where(db.variable.c.standard_name == standard_name)

        if experiment is not None:
            sel = sel.where(db.experiment.c.name == experiment)

        return pandas.read_sql(
            sel,
            self.db,
            index_col="id",
        )

    def open_datasets(
        self, vars: pandas.DataFrame = None, time: slice = None, **kwargs
    ) -> pandas.Series:
        """
        Open variables as xarray objects
        """

        if vars is None:
            vars = self.search(**kwargs)
        elif len(kwargs) > 0:
            search_vars = self.search(**kwargs)
            vars = pandas.merge(vars, search_vars, how="inner")

        return None
