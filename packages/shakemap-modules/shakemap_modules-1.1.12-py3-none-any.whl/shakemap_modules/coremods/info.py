# stdlib imports
import json
import os.path

# third party imports
import numpy as np

# local imports
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from shakemap_modules.base.base import Contents, CoreModule
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.base.cli import get_cli_args
from shakemap_modules.utils.logging import get_generic_logger


class InfoModule(CoreModule):
    """
    info -- Extract info.json from shake_result.hdf and write it as a file.
    """

    command_name = "info"
    targets = [r"products/info\.json"]
    dependencies = [("products/shake_result.hdf", True)]

    def __init__(self, eventid, process="shakemap", logger=None):
        super(InfoModule, self).__init__(eventid, logger=logger)
        if process == "shakemap":
            self.contents = Contents(None, None, eventid)
        self.process = process

    def execute(self, datafile=None, outdir=None, config=None):
        """
        Write info.json metadata file.

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

        # Create ShakeMap metadata file
        self.logger.debug("Writing info.json file...")
        info = container.getMetadata()

        # Clean up strec results to be valid json
        if "strec" in info:
            for k, v in info["strec"].items():
                if isinstance(v, float):
                    if not np.isfinite(v):
                        info["strec"][k] = None

        infostring = json.dumps(info, allow_nan=False)
        info_file = os.path.join(datadir, "info.json")
        f = open(info_file, "wt")
        f.write(infostring)
        f.close()
        container.close()
        cap = "ShakeMap processing parameters and map summary information."
        if self.process == "shakemap":
            self.contents.addFile(
                "supplementalInformation",
                "Supplemental Information",
                cap,
                "info.json",
                "application/json",
            )


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Generate JSON metadata file from shake_results.hdf file.
    """
    datafile, outdir, logdir, _ = get_cli_args(description, config=False)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "info.log")
    logger = get_generic_logger(logfile=logfile)

    mod = InfoModule("noid", process="main", logger=logger)
    mod.execute(datafile=datafile, outdir=outdir)


if __name__ == "__main__":
    main()
