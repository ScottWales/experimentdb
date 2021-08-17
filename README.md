# An experiment database

<!---

Setup for doctests
>>> import experimentdb
>>> from experimentdb.config import config_defaults
>>> config_defaults['database'] = 'sqlite+pysqlite:///:memory:'

--->

## Configuring the database

The database is configured using a Yaml file:

```yaml
# ~/.config/experimentdb.yaml

# Database file to use
database: sqlite:////g/data/$PROJECT/$USER/experimentdb.sqlite

# Paths to scan
scan paths:
    - name: Generic UM Cylc Runs
      path: /scratch/$PROJECT/$USER/cylc-run/*
      type: um-cylc
    - name: UM Nesting Suite Runs
      path: /scratch/$PROJECT/$USER/cylc-run/*
      type: um-nesting
    - name: ACCESS-ESM Payu Runs
      path: /scratch/$PROJECT/$USER/access-esm/*
      type: access-esm-payu
```

By default `~/.config/experimentdb.yaml` will be used, or use `--config PATH`
on the command line / open the database with `ExperimentDB(config=PATH)` in
Python

## Scanning experiments

Scan all experiments in the configuration

```bash
experimentdb scan
```

Manually scan some paths

```bash
experimentdb scan --type um-cylc /scratch/$PROJECT/$USER/cylc-run/u-ab123
```

## Listing experiments

Print a list of experiments known to the database (see `experimentdb list --help` for format options)

```bash
experimentdb list
```

Get a pandas DataFrame of all experiments:

```python
>>> db = experimentdb.ExperimentDB()
>>> db.experiments()

```

## Experiment metadata

Metadata can be added to an experiment:

```bash
experimentdb add-metadata u-ab123 --title "Experiment Title" --tags "convection" "rainfall"
```

And then used to filter searches:

```bash
experimentdb list --tags "convection"
```

## Searching experiments

Print a list of matching variables (see `experimentdb search --help` for format options)

```bash
experimentdb search --standard_name temperature --freq M
```

Get a pandas DataFrame of all variables matching a search:

```python
>>> db = experimentdb.ExperimentDB()
>>> db.search(standard_name='temperature', freq='M')

```

## Loading variables

Load variables returned by a search (the search returns a pandas DataFrame, which can be
further filtered manually):

```python
>>> db = experimentdb.ExperimentDB()
>>> vars = db.search(experiment='u-ab123', standard_name='temperature', freq='M')
>>> db.open_datasets(vars, time=slice('1990-01-01', '2000-01-01'))

```

Or use the search terms directly in `open_dataset()`:

```python
>>> db = experimentdb.ExperimentDB()
>>> vars = db.open_datasets(experiment='u-ab123', standard_name='temperature', freq='M', time=slice('1990-01-01', '2000-01-01'))

```
