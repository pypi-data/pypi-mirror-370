"""
Sleep for a specified number of seconds.
"""

# stdlib imports
import argparse
import inspect
import time
import os

# third party imports

# local imports
from shakemap_modules.base.base import CoreModule
from shakemap_modules.utils.logging import get_generic_logger
from shakemap_modules.base.cli import get_cli_args


class SleepModule(CoreModule):
    """
    sleep -- Sleep for a number of seconds.
    """

    command_name = "sleep"

    def __init__(self, eventid, seconds=None, process="shakemap", logger=None):
        """
        Instantiate a SleepModule class with an event ID.
        """
        super(SleepModule, self).__init__(eventid, logger=logger)
        if seconds is not None:
            self.seconds = seconds

    def execute(self, datafile=None, outdir=None, config=None):
        """
        Sleep for the specified number of seconds and return. The default
        is 60 seconds.
        """

        # Prompt for a comment string if none is provided on the command line
        if self.seconds is None:
            self.seconds = 60

        time.sleep(self.seconds)

    def parseArgs(self, arglist):
        """
        Set up the object to accept the --seconds flag.
        """
        parser = argparse.ArgumentParser(
            prog=self.__class__.command_name, description=inspect.getdoc(self.__class__)
        )
        parser.add_argument(
            "-s",
            "--seconds",
            help="Specify the number of seconds that the module should sleep.",
        )
        #
        # This line should be in any modules that overrides this
        # one. It will collect up everything after the current
        # modules options in args.rem, which should be returned
        # by this function. Note: doing parser.parse_known_args()
        # will not work as it will suck up any later modules'
        # options that are the same as this one's.
        #
        parser.add_argument("rem", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
        args = parser.parse_args(arglist)
        self.seconds = int(args.seconds)
        return args.rem


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Sleep for the specified number of seconds (60 is the default).
    """

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--seconds",
        help="Specify the number of seconds that the module should sleep.",
    )
    args = parser.parse_args()
    if args.seconds is None:
        seconds = 60
    else:
        seconds = int(args.seconds)

    mod = SleepModule("noid", seconds=seconds, process="main", logger=None)
    mod.execute()


if __name__ == "__main__":
    main()
