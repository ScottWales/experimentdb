import argparse
import textwrap
import yaml
import logging
import pandas

from .experimentdb import ExperimentDB, search_params
from .model.experiment import Experiment
from .utils import all_subclasses


class CLIFunction:
    name: str
    help: str

    def __init__(self, subparser):
        parser = subparser.add_parser(
            self.name,
            description=textwrap.dedent(self.__doc__),
            help=self.help,
        )
        self.setup_parser(parser)
        parser.add_argument(
            "--config", type=argparse.FileType("r"), help="configuration file"
        )
        parser.add_argument("--debug", action="store_true", help="print debug info")
        parser.set_defaults(call=self.top_call)

    def top_call(self, args):
        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

        expdb = ExperimentDB(args.config)
        self.call(expdb, args)

    def setup_parser(self, parser: argparse.ArgumentParser):
        """
        Setup the CLI command arguments
        """
        pass

    def call(self, expdb: ExperimentDB, args: argparse.Namespace):
        """
        Call the CLI command
        """
        pass


class Scan(CLIFunction):
    """
    Scan the filesystem for experiments.

    If no paths are given, the paths in the configuration will be used
    """

    name = "scan"
    help = "scan filesystem for experiments"

    def setup_parser(self, parser):
        expt_types = sorted(
            [e.type for e in all_subclasses(Experiment) if e.type is not None]
        )
        parser.add_argument(
            "--type", default="generic", help="experiment type", choices=expt_types
        )
        parser.add_argument("path", nargs="*", help="paths to scan")

    def call(self, expdb, args):
        if len(args.path) > 0:
            for p in args.path:
                expdb.scan(args.type, p)
        else:
            expdb.scan_all()


class List(CLIFunction):
    """
    List known experiments
    """

    name = "experiments"
    help = "list known experiments"

    def setup_parser(self, parser):
        expt_types = sorted(
            [e.type for e in all_subclasses(Experiment) if e.type is not None]
        )
        parser.add_argument(
            "--type", default="generic", help="experiment type", choices=expt_types
        )

    def call(self, expdb, args):
        print(expdb.experiments())


class Search(CLIFunction):
    """
    Search through output variables
    """

    name = "search"
    help = "search output variables"

    def setup_parser(self, parser):
        for k, v in search_params.items():
            parser.add_argument(f"--{k}", help=v["description"])

    def call(self, expdb, args):
        # search_params in args
        args = vars(args)
        args_params = args.keys() & search_params.keys()
        with pandas.option_context("display.max_colwidth", None, "display.max_columns", None, "display.width", None):
            print(expdb.search(**{k: args[k] for k in args_params}))


class Files(CLIFunction):
    """
    List file paths
    """

    name = "files"
    help = "list file paths"

    def setup_parser(self, parser):
        for k, v in search_params.items():
            parser.add_argument(f"--{k}", help=v["description"])

    def call(self, expdb, args):
        # search_params in args
        args = vars(args)
        args_params = args.keys() & search_params.keys()

        with pandas.option_context("display.max_colwidth", None):
            print(expdb.files(**{k: args[k] for k in args_params}))


class ShowConfig(CLIFunction):
    """
    Configuration tools
    """

    name = "config"
    help = "configuration tools"

    def setup_parser(self, parser):
        pass

    def call(self, expdb, args):
        print(yaml.dump(expdb.config))


description = """
⛅ Climate and Weather Experiment Database

Maintains a record of experiments, allowing searches through experiments and
outputs
"""


def main():

    parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(title="commands", metavar=None)

    for c in CLIFunction.__subclasses__():
        c(subparsers)

    args = parser.parse_args()
    args.call(args)


if __name__ == "__main__":
    main()
