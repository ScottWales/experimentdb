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

search_params = {
    "experiment": {
        "description": "experiment name",
        "column": db.experiment.c.name,
    },
    "experiment_type": {
        "description": "experiment type",
        "column": db.experiment.c.type_id,
    },
    "stream": {
        "description": "stream name",
        "column": db.stream.c.name,
    },
    "variable": {"description": "variable text search", "special": "variable_fts"},
    "variable_name": {
        "description": "variable name",
        "column": db.variable.c.name,
    },
    "variable_id": {
        "description": "variable database id",
        "column": db.variable.c.id,
    },
    "standard_name": {
        "description": "variable cf standard_name",
        "column": db.variable.c.standard_name,
    },
    "long_name": {
        "description": "variable long_name",
        "column": db.variable.c.long_name,
    },
}


def document_search_args(func):
    """
    Add search_params documentation to a function
    """
    args = []
    for k, v in search_params.items():
        args.append(f"{k}: {v['description']}")
    doc = "\n        ".join(args)

    func.__doc__ = func.__doc__.replace("{{search_args}}", doc)

    return func


@document_search_args
def search_filter(sel: sqa.select, **kwargs):
    """
    Filters a database query using ExperimentDB search parameters

    Args:
        {{search_args}}
    """
    # Applies the filters listed in search_params
    for k, v in kwargs.items():
        if v is not None:
            if "column" in search_params[k]:
                sel = sel.where(search_params[k]["column"] == v)

            # Handle special filters
            elif search_params[k]["special"] == "variable_fts":
                sel = sel.where(db.variable_fts.c.variable_fts.match(v))

    return sel


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
            self.db = db.connect(self.config["database"])
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

                # Commit the experiment to the database
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

    @document_search_args
    def search(self, /, **kwargs) -> pandas.DataFrame:
        """
        Perform a search of experiments/streams/variables in the database

        A variable_id is returned as the dataframe index, use
        `files(variable_id=ID)` to list the files containing the variable or
        `open_dataarray(variable_id=ID)` to open the files

        Args:
            {{search_args}}
        """
        # Columns to return
        sel = sqa.select(
            [
                db.experiment.c.name.label("experiment"),
                db.stream.c.name.label("stream"),
                db.variable.c.name.label("variable"),
                db.variable.c.standard_name,
                db.variable.c.time_resolution,
                db.variable.c.long_name,
                db.variable.c.id.label("variable_id"),
            ]
        ).select_from(
            db.experiment.join(db.stream).join(db.variable).join(db.variable_fts)
        )

        # Filter the search
        sel = search_filter(sel, **kwargs)

        return pandas.read_sql(
            sel,
            self.db,
            index_col="variable_id",
        )

    @document_search_args
    def files(self, /, **kwargs) -> pandas.DataFrame:
        """
        List the files present in matching variables

        A variable_id is returned as the dataframe index, use
        `search(variable_id=ID)` to get more information about the variable

        Args:
            {{search_args}}
        """
        # Columns to return
        sel = sqa.select(
            [
                db.experiment.c.path,
                db.file.c.relative_path,
                db.variable.c.id.label("variable_id"),
            ]
        ).select_from(
            db.experiment.join(db.stream)
            .join(db.variable)
            .join(db.variable_fts)
            .join(db.file, db.file.c.stream_id == db.stream.c.id)
        )

        # Filter the search
        sel = search_filter(sel, **kwargs)

        df = pandas.read_sql(
            sel,
            self.db,
            index_col="variable_id",
        )

        return df.apply(
            lambda row: {"path": os.path.join(row.path, row.relative_path)},
            axis=1,
            result_type="expand",
        )

    @document_search_args
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
            {{search_args}}
        """

        if vars is None:
            vars = self.search(**kwargs)
        elif len(kwargs) > 0:
            search_vars = self.search(**kwargs)
            vars = pandas.merge(vars, search_vars, how="inner")

        results = [_open_var_id(self.db, id, time) for id in vars.index]
        return pandas.Series(results, index=vars.index)

    @document_search_args
    def open_dataarray(self, **kwargs) -> xarray.DataArray:
        """
        Single variable version of :meth:`open_dataarrays`

        An error will be raised if more than one result matches

        Args:
            See :meth:`open_dataarrays`
        """

        s = self.open_dataarrays(**kwargs)
        if len(s) == 0:
            raise Exception("No results found")
        if len(s) > 1:
            raise Exception("Multiple results found, try 'open_dataarrays' instead")

        return s.iloc[0]


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
