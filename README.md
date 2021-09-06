# ⛅ edb - climate and weather experiment database


`edb` stores a record of what experiments have been run, including output files
and variables, in a sqlite database. You can access it through the command line
or python

`edb` knows about these experiment types:
<!---
>>> from edb.model.experiment import Experiment
>>> from edb.utils import all_subclasses
>>> ex = {e.type: e for e in all_subclasses(Experiment) if e.type is not None}
>>> for e in sorted(ex):
...     print(f"* {e}: {ex[e].description}") #--->
* access-cm-payu: ACCESS-CM 1.x run by Payu
* access-cm-rose: ACCESS-CM 2.x run by Rose/Cylc
* access-cm-script: ACCESS-CM 1.x run by CSIRO ksh script
* generic: Generic NetCDF output
* um-rose: UM >= vn10 run by Rose/Cylc
* um-umui: UM < vn10 run by UMUI

<!---
Setup for doctests
>>> from edb.config import config_defaults
>>> config_defaults['database'] = 'sqlite+pysqlite:///:memory:'
# --->

If interacting with `edb` in python, first connect to the database

```python
>>> import edb
>>> db = edb.ExperimentDB()

```

<!---
>>> from edb.tests.conftest import setup_sample_data
>>> setup_sample_data(db.session)
# --->

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
on the command line / open the database with `edb.ExperimentDB(config=PATH)` in
Python

## Scanning experiments

Scanning an experiment directory adds its path and the associated output
files/variables to the database. In order for `edb` to correctly find the 
outputs and experiment metadata you can specify the experiment type.

Scan all experiments listed in the config file

```bash
edb scan
```

Manually scan some paths

```bash
edb scan --type um-cylc /scratch/$PROJECT/$USER/cylc-run/u-ab123
```

## Listing experiments

Print a list of experiments known to the database (see `edb list --help` for
format options)

```bash
edb list
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
edb add-metadata u-ab123 --title "Experiment Title" --tags "convection" "rainfall"
```

And then used to filter searches:

```bash
edb list --tags "convection"
```

## Searching experiments

Print a list of matching variables (see `edb search --help` for format options)

```bash
edb search --standard_name temperature --freq P1M
```

Get a pandas DataFrame of all variables matching a search:

```python
>>> db.search(standard_name='temperature', freq='1M')
   experiment     stream variable
id                               
1     u-ab123  ab123a.pa        T

```

## Loading variables

Within python you can load the variables returned by a search as xarray
DataArrays (the search returns a pandas DataFrame, which can be
further filtered manually):

```python
>>> vars = db.search(experiment='u-ab123',
...                  standard_name='temperature',
...                  freq='M')
>>> db.open_datasets(vars, time=slice('1990-01-01', '2000-01-01'))

```

Or use the search terms directly in `open_dataset()`:

```python
>>> vars = db.open_datasets(experiment='u-ab123',
...                         standard_name='temperature',
...                         freq='M',
...                         time=slice('1990-01-01', '2000-01-01'))

```
