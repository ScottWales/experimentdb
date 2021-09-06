from ..config import read_config, config_defaults, config_schema
import jsonschema
import os
import pytest


def test_parse_config(tmp_path):

    # Config from README.md
    config = """
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
    """

    path = tmp_path / "a.yaml"
    path.write_text(config)

    c = read_config(path)

    assert "database" in c
    assert "scan paths" in c

    # Value in file should override default
    assert c["database"] == os.path.expandvars(
        "sqlite:////g/data/$PROJECT/$USER/experimentdb.sqlite"
    )

    # Schema errors
    config = """
    # Paths to scan
    scan paths:
        - name: Generic UM Cylc Runs
          path: /scratch/$PROJECT/$USER/cylc-run/*
    """

    path = tmp_path / "b.yaml"
    path.write_text(config)

    with pytest.raises(jsonschema.ValidationError):
        c = read_config(path)


def test_config_defaults():
    jsonschema.validate(config_defaults, schema=config_schema)
