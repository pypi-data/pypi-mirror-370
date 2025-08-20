"""
Raise an exception (used for testing.)
"""

# stdlib imports
import os

# third party imports

# local imports
from shakemap_modules.base.base import CoreModule


class ExceptionModule(CoreModule):
    """
    Module to raise an exception for testing purposes.
    """

    command_name = "exception"

    def __init__(self, eventid):
        """
        Instantiate a CoreModule class with an event ID.
        """
        self._eventid = eventid

    def execute(self):
        """
        Raise an Exception object.

        This module exists for the purposes of testing shake's exception
        handling logic.
        """

        raise Exception("This is a test of exception handling.")


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Emit an exception.
    """
    mod = ExceptionModule("noid")
    mod.execute()


if __name__ == "__main__":
    main()
