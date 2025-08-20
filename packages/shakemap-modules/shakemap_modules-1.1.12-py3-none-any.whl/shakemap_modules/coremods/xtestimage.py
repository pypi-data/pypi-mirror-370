# stdlib imports
import os.path

# third party imports
import matplotlib.pyplot as plt
import numpy as np

# local imports
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from esi_shakelib.utils.imt_string import oq_to_file
from shakemap_modules.base.base import CoreModule
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.base.cli import get_cli_args
from shakemap_modules.utils.logging import get_generic_logger


class XTestImage(CoreModule):
    """
    xtestimage -- Plot 2D images of ShakeMap arrays
    """

    command_name = "xtestimage"

    def __init__(self, eventid, process="shakemap", logger=None):
        """
        Instantiate a XTestImage class with an event ID.
        """
        super(XTestImage, self).__init__(eventid, logger=logger)
        self.process = process

    def execute(self, datafile=None, outdir=None, config=None):
        """
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
        info = container.getMetadata()
        evid = info["input"]["event_information"]["event_id"]
        if container.getDataType() != "grid":
            raise NotImplementedError(
                "xtestimage module can only operate on "
                "gridded data not sets of points"
            )

        datadict = {}
        imtlist = container.getIMTs("GREATER_OF_TWO_HORIZONTAL")
        for myimt in imtlist:
            datadict[myimt] = container.getIMTGrids(myimt, "GREATER_OF_TWO_HORIZONTAL")

        container.close()

        #
        # Make plots
        #
        for myimt in imtlist:
            if myimt == "MMI":
                yunits = "(MMI)"
            elif myimt == "PGV":
                yunits = "[ln(cm/s)]"
            else:
                yunits = "[ln(g)]"

            fileimt = oq_to_file(myimt)

            #
            # Do the ground motion plots
            #
            data = datadict[myimt]
            grddata = data["mean"]
            metadata = data["mean_metadata"]

            fig = plt.figure(figsize=(10, 10))
            gs = plt.GridSpec(4, 4, hspace=0.2, wspace=0.1)
            ax0 = fig.add_subplot(gs[:-1, 1:])
            plt.title(evid + ": " + myimt + " mean")
            im1 = ax0.imshow(
                grddata,
                extent=(
                    metadata["xmin"],
                    metadata["xmax"],
                    metadata["ymin"],
                    metadata["ymax"],
                ),
            )
            cbax = fig.add_axes([0.915, 0.34, 0.02, 0.5])
            plt.colorbar(im1, ax=ax0, cax=cbax)
            ycut = fig.add_subplot(gs[:-1, 0], sharey=ax0)
            xcut = fig.add_subplot(gs[-1, 1:], sharex=ax0)
            rows, cols = grddata.shape
            midrow = int(rows / 2)
            midcol = int(cols / 2)
            xvals = np.linspace(metadata["xmin"], metadata["xmax"], cols)
            yvals = np.linspace(metadata["ymin"], metadata["ymax"], rows)
            ycut.plot(grddata[:, midcol], yvals)
            xcut.plot(xvals, grddata[midrow, :])
            ycut.set(xlabel=myimt + " " + yunits, ylabel="Latitude")
            xcut.set(xlabel="Longitude", ylabel=myimt + " " + yunits)
            ycut.set_ylim((metadata["ymin"], metadata["ymax"]))
            xcut.set_xlim((metadata["xmin"], metadata["xmax"]))
            ax0.label_outer()

            pfile = os.path.join(datadir, evid + "_" + fileimt + ".pdf")
            plt.savefig(pfile, bbox_inches="tight")
            plt.close()

            #
            # Do the stddev plots
            #
            grddata = data["std"]

            fig = plt.figure(figsize=(10, 10))
            gs = plt.GridSpec(4, 4, hspace=0.2, wspace=0.1)
            ax0 = fig.add_subplot(gs[:-1, 1:])
            plt.title(evid + ": " + myimt + " stddev")
            im1 = ax0.imshow(
                grddata,
                extent=(
                    metadata["xmin"],
                    metadata["xmax"],
                    metadata["ymin"],
                    metadata["ymax"],
                ),
            )
            cbax = fig.add_axes([0.915, 0.34, 0.02, 0.5])
            plt.colorbar(im1, ax=ax0, cax=cbax)
            ycut = fig.add_subplot(gs[:-1, 0], sharey=ax0)
            xcut = fig.add_subplot(gs[-1, 1:], sharex=ax0)
            rows, cols = grddata.shape
            midrow = int(rows / 2)
            midcol = int(cols / 2)
            xvals = np.linspace(metadata["xmin"], metadata["xmax"], cols)
            yvals = np.linspace(metadata["ymin"], metadata["ymax"], rows)
            ycut.plot(grddata[:, midcol], yvals)
            xcut.plot(xvals, grddata[midrow, :])
            ycut.set(xlabel="stddev " + yunits, ylabel="Latitude")
            xcut.set(xlabel="Longitude", ylabel="stddev " + yunits)
            xcut.set_xlim((metadata["xmin"], metadata["xmax"]))
            xcut.set_ylim(bottom=0, top=np.max(grddata[midrow, :]) * 1.1)
            ycut.set_xlim(left=0, right=np.max(grddata[:, midcol] * 1.1))
            ycut.set_ylim((metadata["ymin"], metadata["ymax"]))
            ax0.label_outer()

            pfile = os.path.join(datadir, evid + "_" + fileimt + "_sd.pdf")
            plt.savefig(pfile, bbox_inches="tight")
            plt.close()


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Generate test images from shake_results.hdf file.
    """
    datafile, outdir, logdir, config = get_cli_args(description, config=False)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "xtestimage.log")
    logger = get_generic_logger(logfile=logfile)

    mod = XTestImage("noid", process="main", logger=logger)
    mod.execute(datafile=datafile, outdir=outdir, config=config)


if __name__ == "__main__":
    main()
