# stdlib imports
import os.path
import zipfile

# third party imports

# local imports
from mapio.gdal import GDALGrid
from mapio.geodict import GeoDict
from mapio.grid2d import Grid2D
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from esi_shakelib.utils.imt_string import oq_to_file
from shakemap_modules.base.base import Contents, CoreModule
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.base.cli import get_cli_args
from shakemap_modules.utils.logging import get_generic_logger

FORMATS = {"shapefile": ("ESRI Shapefile", "shp"), "geojson": ("GeoJSON", "json")}

DEFAULT_FILTER_SIZE = 10


class RasterModule(CoreModule):
    """
    raster -- Generate GIS raster files of all IMT values from
                    shake_result.hdf.
    """

    command_name = "raster"
    targets = [r"products/raster\.zip"]
    dependencies = [("products/shake_result.hdf", True)]

    def __init__(self, eventid, process="shakemap", logger=None):
        super(RasterModule, self).__init__(eventid, logger=logger)
        if process == "shakemap":
            self.contents = Contents(None, None, eventid)
        self.process = process

    def execute(self, datafile=None, outdir=None, config=None):
        """
        Write raster.zip file containing ESRI Raster files of all the IMTs
        in shake_result.hdf.

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
        if container.getDataType() != "grid":
            raise NotImplementedError(
                "raster module can only operate on " "gridded data, not sets of points"
            )

        # create GIS-readable .flt files of imt and uncertainty
        self.logger.debug("Creating GIS grids...")
        layers = container.getIMTs()

        # Package up all of these files into one zip file.
        zfilename = os.path.join(datadir, "raster.zip")
        zfile = zipfile.ZipFile(zfilename, mode="w", compression=zipfile.ZIP_DEFLATED)

        files_written = []
        for layer in layers:
            _, layer = layer.split("/")
            fileimt = oq_to_file(layer)
            # This is a bit hacky -- we only produce the raster for the
            # first IMC returned. It should work as long as we only have
            # one IMC produced per ShakeMap run.
            imclist = container.getComponents(layer)
            imtdict = container.getIMTGrids(layer, imclist[0])
            mean_grid = Grid2D(imtdict["mean"], GeoDict(imtdict["mean_metadata"]))
            std_grid = Grid2D(imtdict["std"], GeoDict(imtdict["std_metadata"]))
            mean_gdal = GDALGrid.copyFromGrid(mean_grid)
            std_gdal = GDALGrid.copyFromGrid(std_grid)
            mean_fname = os.path.join(datadir, f"{fileimt}_mean.flt")
            mean_hdr = os.path.join(datadir, f"{fileimt}_mean.hdr")
            std_fname = os.path.join(datadir, f"{fileimt}_std.flt")
            std_hdr = os.path.join(datadir, f"{fileimt}_std.hdr")
            self.logger.debug(f"Saving {mean_fname}...")
            mean_gdal.save(mean_fname)
            files_written.append(mean_fname)
            files_written.append(mean_hdr)
            self.logger.debug(f"Saving {std_fname}...")
            std_gdal.save(std_fname)
            files_written.append(std_fname)
            files_written.append(std_hdr)
            zfile.write(mean_fname, f"{fileimt}_mean.flt")
            zfile.write(mean_hdr, f"{fileimt}_mean.hdr")
            zfile.write(std_fname, f"{fileimt}_std.flt")
            zfile.write(std_hdr, f"{fileimt}_std.hdr")

        zfile.close()

        # nuke all of the copies of the files we just put in the zipfile
        for file_written in files_written:
            os.remove(file_written)

        if self.process == "shakemap":
            self.contents.addFile(
                "rasterData",
                "ESRI Raster Files",
                "Data and uncertainty grids in ESRI raster " "format",
                "raster.zip",
                "application/zip",
            )
        container.close()


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Generate GIS raster files from shake_results.hdf file.
    """
    datafile, outdir, logdir, _ = get_cli_args(description, config=False)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "raster.log")
    logger = get_generic_logger(logfile=logfile)

    mod = RasterModule("noid", process="main", logger=logger)
    mod.execute(datafile=datafile, outdir=outdir)


if __name__ == "__main__":
    main()
