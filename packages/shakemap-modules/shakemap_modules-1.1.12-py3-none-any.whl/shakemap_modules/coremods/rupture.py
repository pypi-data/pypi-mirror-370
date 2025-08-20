# stdlib imports
import json
import os.path

# third party imports

# local imports
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from shakemap_modules.base.base import Contents, CoreModule
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.base.cli import get_cli_args
from shakemap_modules.utils.logging import get_generic_logger

ALLOWED_FORMATS = ["json"]


class RuptureModule(CoreModule):
    """
    rupture -- Generate rupture.json from shake_result.hdf.
    """

    command_name = "rupture"
    targets = [r"products/rupture\.json"]
    dependencies = [("products/shake_result.hdf", True)]

    def __init__(self, eventid, process="shakemap", logger=None):
        super(RuptureModule, self).__init__(eventid, logger=logger)
        if process == "shakemap":
            self.contents = Contents(None, None, eventid)
        self.process = process

    def execute(self, datafile=None, outdir=None, config=None):
        """
        Write rupture.json file.

        Raises:
            NotADirectoryError: When the event data directory does not exist.
            FileNotFoundError: When the the shake_result HDF file does not
                exist.
        """
        if self.process == "shakemap":
            install_path, data_path = get_config_paths()
            datadir = os.path.join(data_path, self._eventid, "current", "products")
            datafile = os.path.join(datadir, "shake_result.hdf")
        else:
            if outdir is None:
                raise FileNotFoundError(f"outdir must be provided.")
            datadir = outdir
            if datafile is None:
                raise FileNotFoundError(f"datafile must be provided.")

        if not os.path.isdir(datadir):
            raise NotADirectoryError(f"{datadir} is not a valid directory.")
        if not os.path.isfile(datafile):
            raise FileNotFoundError(f"{datafile} does not exist.")

        # Open the ShakeMapOutputContainer and extract the data
        container = ShakeMapOutputContainer.load(datafile)

        # create ShakeMap rupture file
        for fformat in ALLOWED_FORMATS:
            if fformat == "json":
                self.logger.info("Writing rupture.json file...")
                rupture_dict = container.getRuptureDict()
                rupture_file = os.path.join(datadir, "rupture.json")
                f = open(rupture_file, "w")
                json.dump(rupture_dict, f)
                f.close()

        container.close()

        if self.process == "shakemap":
            self.contents.addFile(
                "ruptureJSON",
                "Fault Rupture",
                "JSON Representation of Fault Rupture.",
                "rupture.json",
                "application/json",
            )


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Generate rupture.json from shake_results.hdf file.
    """
    datafile, outdir, logdir, _ = get_cli_args(description, config=False)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "rupture.log")
    logger = get_generic_logger(logfile=logfile)

    mod = RuptureModule("noid", process="main", logger=logger)
    mod.execute(datafile=datafile, outdir=outdir)


if __name__ == "__main__":
    main()
