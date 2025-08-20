# stdlib imports
import json
import os.path

# third party imports
import numpy as np
from scipy.ndimage import gaussian_filter
from openquake.hazardlib import imt

# local imports
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from esi_shakelib.utils.imt_string import oq_to_file
from shakemap_modules.base.base import Contents, CoreModule
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.base.cli import get_cli_args
from shakemap_modules.utils.logging import get_generic_logger

# Not really relevant, but seemingly necessary
COMPONENT = "GREATER_OF_TWO_HORIZONTAL"


class CoverageModule(CoreModule):
    """
    coverage -- Create JSON coverage(s) of the ground motion layers.
    """

    command_name = "coverage"
    targets = [
        r"products/coverage_h\.json",
        r"products/coverage_m\.json",
        r"products/coverage_l\.json",
    ]
    dependencies = [("products/shake_result.hdf", True)]

    def __init__(self, eventid, process="shakemap", logger=None):
        super(CoverageModule, self).__init__(eventid, logger=logger)
        if process == "shakemap":
            self.contents = Contents("JSON Coverages", "coverages", eventid)
        self.process = process

    def execute(self, datafile=None, outdir=None, config=None):
        """Create high, medium, and low resolution coverage of the mapped
        parameters.

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

        # get all of the grid layers and the geodict
        if container.getDataType() != "grid":
            raise NotImplementedError(
                "coverage module can only function on gridded data, not sets of points"
            )

        imtlist = container.getIMTs()
        for imtype in imtlist:
            component, imtype = imtype.split("/")
            fileimt = oq_to_file(imtype)
            oqimt = imt.from_string(imtype)

            imtdict = container.getIMTGrids(imtype, component)
            grid_data = imtdict["mean"]
            metadata = imtdict["mean_metadata"]

            if imtype == "MMI":
                description = ("Modified Mercalli Intensity",)
                property_id = (
                    "https://earthquake.usgs.gov/learn/topics/mercalli.php",
                )  # noqa
                decimals = 1
            elif imtype == "PGA":
                description = ("Peak Ground Acceleration",)
                units = 'natural logarithm of "g"'
                symbol = "ln(g)"
                decimals = 2
            elif imtype == "PGV":
                description = ("Peak Ground Velocity",)
                units = "natural logarithm of centimeters per second"
                symbol = "ln(cm/s)"
                decimals = 2
            elif imtype.startswith("SA"):
                description = (str(oqimt.period) + "-second Spectral Acceleration",)
                units = 'natural logarithm of "g"'
                symbol = "ln(g)"
                decimals = 2
            else:
                raise TypeError("Unknown IMT in coverage module")

            for i in range(3):
                if i == 0:
                    resolution = "high"
                    fgrid = grid_data
                    decimation = 1
                elif i == 1:
                    resolution = "medium"
                    fgrid = gaussian_filter(grid_data, sigma=1)
                    decimation = 2
                elif i == 2:
                    resolution = "low"
                    fgrid = gaussian_filter(grid_data, sigma=2)
                    decimation = 4

                rgrid = fgrid[::decimation, ::decimation]
                ny, nx = rgrid.shape
                rnd_grd = np.flipud(np.around(rgrid, decimals=decimals)).flatten()
                if imtype == "MMI":
                    rnd_grd = np.clip(rnd_grd, 1.0, 10.0)
                xstart = metadata["xmin"]
                xstop = metadata["xmin"] + (nx - 1) * decimation * metadata["dx"]
                ystart = metadata["ymin"]
                ystop = metadata["ymin"] + (ny - 1) * decimation * metadata["dy"]

                coverage = {
                    "type": "Coverage",
                    "domain": {
                        "type": "Domain",
                        "domainType": "Grid",
                        "axes": {
                            "x": {"start": xstart, "stop": xstop, "num": nx},
                            "y": {"start": ystart, "stop": ystop, "num": ny},
                        },
                        "referencing": [
                            {
                                "coordinates": ["x", "y"],
                                "system": {
                                    "type": "GeographicCRS",
                                    "id": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",  # noqa
                                },
                            }
                        ],
                    },
                    "parameters": {
                        imtype: {
                            "type": "Parameter",
                            "description": {"en": description},
                            "observedProperty": {
                                "id": property_id,
                                "label": {"en": imtype},
                            },
                        }
                    },
                    "ranges": {
                        imtype: {
                            "type": "NdArray",
                            "dataType": "float",
                            "axisNames": ["y", "x"],
                            "shape": [ny, nx],
                            "values": rnd_grd.tolist(),
                        }
                    },
                }
                if imtype == "MMI":
                    coverage["parameters"]["MMI"]["preferredPalette"] = {
                        "colors": [
                            "rgb(255, 255, 255)",
                            "rgb(255, 255, 255)",
                            "rgb(191, 204, 255)",
                            "rgb(160, 230, 255)",
                            "rgb(128, 255, 255)",
                            "rgb(122, 255, 147)",
                            "rgb(255, 255, 0)",
                            "rgb(255, 200, 0)",
                            "rgb(255, 145, 0)",
                            "rgb(255, 0, 0)",
                            "rgb(200, 0, 0)",
                        ],
                        "extent": [0, 10],
                        "interpolation": "linear",
                    }
                else:
                    coverage["parameters"][imtype]["unit"] = {
                        "label": {"en": units},
                        "symbol": {
                            "value": symbol,
                            "type": "http://www.opengis.net/def/uom/UCUM/",
                        },
                    }

                if component == "GREATER_OF_TWO_HORIZONTAL":
                    fname = f"coverage_{fileimt}_{resolution}_res.covjson"
                else:
                    fname = f"coverage_{fileimt}_{resolution}_{component}_res.covjson"
                filepath = os.path.join(datadir, fname)
                with open(filepath, "w") as outfile:
                    json.dump(coverage, outfile, separators=(",", ":"))
                if self.process == "shakemap":
                    self.contents.addFile(
                        imtype + "_" + resolution + "_res_coverage",
                        resolution + "-res " + imtype.upper() + " Coverage",
                        "Coverage of " + resolution + " resolution " + imtype,
                        fname,
                        "application/json",
                    )
        container.close()


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Generate JSON coverage files from shake_results.hdf file.
    """
    datafile, outdir, logdir, _ = get_cli_args(description, config=False)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "coverage.log")
    logger = get_generic_logger(logfile=logfile)

    mod = CoverageModule("noid", process="main", logger=logger)
    mod.execute(datafile=datafile, outdir=outdir)


if __name__ == "__main__":
    main()
