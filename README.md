# An experiment database

<!---

Setup for doctests
>>> import experimentdb
>>> from experimentdb.config import config_defaults
>>> config_defaults['database'] = 'sqlite+pysqlite:///:memory:'

--->

```python
>>> db = experimentdb.ExperimentDB()

```

<!---
>>> from experimentdb.tests.conftest import setup_sample_data
>>> setup_sample_data(db.session)

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
>>> db.experiments()
       name                                  path  type_id
id                                                        
1   u-ab123  /scratch/w35/saw562/cylc-run/u-ab123  um-rose

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
experimentdb search --standard_name temperature --freq P1M
```

Get a pandas DataFrame of all variables matching a search:

```python
>>> db.search(standard_name='temperature', freq='1M')
   experiment     stream variable
id                               
1     u-ab123  ab123a.pa        T

```

## Loading variables

Load variables returned by a search (the search returns a pandas DataFrame, which can be
further filtered manually):

```python
>>> vars = db.search(experiment='u-ab123', standard_name='temperature', freq='M')
>>> db.open_datasets(vars, time=slice('1990-01-01', '2000-01-01'))

```

Or use the search terms directly in `open_dataset()`:

```python
>>> vars = db.open_datasets(experiment='u-ab123', standard_name='temperature', freq='M', time=slice('1990-01-01', '2000-01-01'))

```
