import yaml
import jsonschema
import os

config_defaults = {
    "database": os.path.expandvars(
        "sqlite:////scratch/$PROJECT/$USER/tmp/experimentdb.sqlite3"
    ),
    "scan paths": [],
}

config_schema = yaml.safe_load(
    """
type: object
properties:
    database:
        type: string
    scan paths:
        type: array
        items:
            type: object
            properties:
                name:
                    type: string
                path:
                    type: string
                type:
                    type: string
            required: [name, path, type]
required: [database, scan paths]
"""
)


def read_config(path=None):
    if path is None:
        path = "~/.config/experimentdb.yaml"

    try:
        with open(path) as f:
            # Expand environment variables
            text = f.read()
            text = os.path.expandvars(text)

            # Parse the yaml
            config = yaml.safe_load(text)
    except FileNotFoundError:
        config = {}

    config = config_defaults | config

    jsonschema.validate(config, schema=config_schema)

    return config
