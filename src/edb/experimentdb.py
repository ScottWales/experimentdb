from .config import read_config
from .model.experiment import experiment_factory, Experiment
import sqlalchemy.orm as sqo
import sqlalchemy as sqa
from . import db
import typing as T

import glob
import pandas
import logging
import os
import xarray


class ExperimentDB:
    """
    A database of numerical climate & weather experiments

    - Add directories to the database with :meth:`scan()` or :meth:`scan_all()`
    - List known experiments with :meth:`experiments()`
    - Search for output variables with :meth:`search()`
    - Open variables with :meth:`open_datasets()`
    """

    def __init__(self, config=None, conn: sqa.engine.Connection = None):
        """
        Connect to the database

        Args:
            config: Path to configuration file (see :func:`read_config()`)
        """
        self.config = read_config(config)
        if conn is None:
            self.db = db.connect(self.config)
        else:
            self.db = conn
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
                db.variable.c.standard_name,
                db.variable.c.time_resolution,
                db.variable.c.long_name,
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

    def files(
        self, /, experiment: str = None, standard_name: str = None, freq: str = None
    ) -> pandas.DataFrame:
        """
        List the files present in matching variables
        """
        sel = sqa.select(
            [
                db.experiment.c.path,
                db.file.c.relative_path,
                db.variable.c.id,
            ]
        ).select_from(db.experiment.join(db.stream).join(db.variable))

        if standard_name is not None:
            sel = sel.where(db.variable.c.standard_name == standard_name)

        if experiment is not None:
            sel = sel.where(db.experiment.c.name == experiment)

        df = pandas.read_sql(
            sel,
            self.db,
            index_col="id",
        )

        return df.apply(lambda row: os.path.join(row.path, row.relative_path), axis=1)

    def open_dataarrays(
        self, vars: pandas.DataFrame = None, time: slice = None, **kwargs
    ) -> pandas.Series:
        """
        Open variables as xarray objects

        If vars is present, those variables will be opened (using the dataframe
        index as the variable id to open).

        If kwargs are present, those terms are used to search the database,
        equivalent to running::

            vars = db.search(**kwargs)
            db.open_datasets(vars)

        If both vars and kwargs are present, the records listed in vars are
        further filtered by the search terms in kwargs.

        Args:
            vars: pandas.DataFrame listing variables to open, index column must
                  be the database id of the variable (as  is returned by
                  :meth:`search`)
            time: time slice to open
            kwargs: if present, passed to :meth:`search` to select variables to
                    open
        """

        if vars is None:
            vars = self.search(**kwargs)
        elif len(kwargs) > 0:
            search_vars = self.search(**kwargs)
            vars = pandas.merge(vars, search_vars, how="inner")

        results = [_open_var_id(self.db, id, time) for id in vars.index]
        return pandas.Series(results, index=vars.index)


def _open_var_id(
    conn: sqa.engine.Connection, variable_id: int, time: slice = None
) -> xarray.DataArray:
    """
    Open the files for a specific variable_id
    """

    # Find the files for this variable
    files = (
        sqa.select(
            [
                db.experiment.c.path,
                db.file.c.relative_path,
                db.file.c.type_id,
                db.file.c.start_date,
                db.file.c.end_date,
                db.variable.c.name,
            ]
        )
        .select_from(db.experiment.join(db.stream).join(db.file).join(db.variable))
        .where(db.variable.c.id == variable_id)
        .order_by(db.file.c.start_date)
    )

    das = []
    for path, rel_path, type, start, end, varname in conn.execute(files):
        path = os.path.join(path, rel_path)

        if type == "netcdf":
            da = xarray.open_dataset(path)[varname]
        else:
            import iris

            cubes = iris.load_cubes(path, iris.AttributeConstraint(STASH=varname))
            # TODO: handle multiple matches
            da = xarray.DataArray.from_iris(cubes[0])

    das.append(da)

    return xarray.concat(das, dim="time")
