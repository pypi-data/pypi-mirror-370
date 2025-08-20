# stdlib imports
import glob
import os.path

# third party imports

# local imports
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from shakemap_modules.base.base import CoreModule
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.utils.logging import get_generic_logger
from shakemap_modules.base.cli import get_cli_args


class HistoryModule(CoreModule):
    """
    history -- Output the version history of an event.
    """

    command_name = "history"

    def __init__(self, eventid, process="shakemap", logger=None):
        super(HistoryModule, self).__init__(eventid, logger=logger)
        self.process = process

    def execute(self, datafile=None, outdir=None, config=None):
        """
        Output the version history of an event.

        Raises:
            NotADirectoryError: When the event data directory does not exist.
        """
        if self.process == "shakemap":
            _, data_path = get_config_paths()
            datadir = os.path.join(data_path, self._eventid, "current")
            backups = glob.glob(os.path.join(data_path, self._eventid, "backup*"))
            backups.sort(reverse=True)
            if not os.path.isdir(datadir):
                raise NotADirectoryError(f"{datadir} is not a valid directory.")
            datafile = os.path.join(datadir, "products", "shake_result.hdf")
        else:
            if datafile is None:
                raise FileNotFoundError(f"datafile must be provided.")
            backups = []

        # First try the current results file...
        if os.path.isfile(datafile):
            # Open the ShakeMapOutputContainer and extract the data
            container = ShakeMapOutputContainer.load(datafile)
            try:
                metadata = container.getMetadata()
            except LookupError:
                print("\nNo version history available for this event.\n")
                return
            history = metadata["processing"]["shakemap_versions"]["map_data_history"]
            final = False
            if len(backups) > 0:
                last_ver = int(backups[0][-4:])
                last_hist = history[-1][2]
                if last_ver == last_hist:
                    final = True
            print_history(history, final=final)
            return

        # Nope. Are there any backup files?
        if len(backups) == 0 or self.process != "shakemap":
            print("\nNo version history available for this event.\n")
            return

        # There should be a results file in the backup directory...
        datafile = os.path.join(
            data_path, self._eventid, backups[0], "products", "shake_result.hdf"
        )
        if os.path.isfile(datafile):
            # Open the ShakeMapOutputContainer and extract the data
            container = ShakeMapOutputContainer.load(datafile)
            try:
                metadata = container.getMetadata()
            except LookupError:
                print("\nNo version history available for this event.\n")
                return
            history = metadata["processing"]["shakemap_versions"]["map_data_history"]
            print_history(history, final=True)
            return

        print("\nNo version history available for this event.\n")
        return


def print_history(history, final=False):

    if len(history) == 0:
        print("\nVersion history is empty.\n")
        return

    print("\nVersion history:")
    print("Timestamp | Originator | Version | Comment")
    print("------------------------------------------")
    for ix, line in enumerate(history):
        if final is False and ix == len(history) - 1:
            asterisk = "*"
        else:
            asterisk = ""
        print("%s | %s | %d | %s%s" % (line[0], line[1], line[2], line[3], asterisk))
    print("")
    if final is False:
        print("*Not finalized.\n")


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Print the version history found in a shake_results.hdf file.
    """
    datafile, outdir, logdir, _ = get_cli_args(description, config=False)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "history.log")
    logger = get_generic_logger(logfile=logfile)

    mod = HistoryModule("noid", process="main", logger=logger)
    mod.execute(datafile=datafile, outdir=outdir)


if __name__ == "__main__":
    main()
