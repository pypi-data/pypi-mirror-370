# stdlib imports
import argparse
import concurrent.futures as cf
import copy
import inspect
import json
import os.path

# third party
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import dill
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import rasterio.features
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader
from configobj import ConfigObj
from esi_shakelib.utils.imt_string import oq_to_file

# local imports
from esi_utils_colors.cpalette import ColorPalette
from esi_utils_geo.city import Cities
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from mapio.geodict import GeoDict
from mapio.grid2d import Grid2D
from mapio.reader import read
from matplotlib.ticker import NullLocator
from PIL import Image
from scipy.interpolate import griddata
from shakemap_modules.base.base import Contents, CoreModule
from shakemap_modules.base.cli import get_cli_args
from shakemap_modules.mapping.mapmaker import draw_map
from shakemap_modules.utils.config import (
    check_extra_values,
    config_error,
    get_config_paths,
    get_configspec,
    get_custom_validator,
    get_data_path,
)
from shakemap_modules.utils.logging import get_generic_logger

WATERCOLOR = "#7AA1DA"


class MappingModule(CoreModule):
    """
    mapping -- Generate maps of the IMTs found in shake_result.hdf.
    """

    command_name = "mapping"
    targets = [
        r"products/intensity\.jpg",
        r"products/intensity\.pdf",
        r"products/mmi_legend\.pdf",
        r"products/pga\.jpg",
        r"products/pga\.pdf",
        r"products/pgv\.jpg",
        r"products/pgv\.pdf",
        r"products/psa.*p.*\.jpg",
        r"products/psa.*p.*\.pdf",
    ]
    dependencies = [("products/shake_result.hdf", True)]
    configs = ["products.conf"]

    display_magnitude = None
    pickle_plots = False

    def __init__(self, eventid, process="shakemap", logger=None):
        super(MappingModule, self).__init__(eventid, logger=logger)
        if process == "shakemap":
            self.contents = Contents("Ground Motion Maps", "maps", eventid)
        self.process = process

    def parseArgs(self, arglist):
        """
        Set up the object to accept the --display-magnitude flag
        """
        parser = argparse.ArgumentParser(
            prog=self.__class__.command_name,
            description=inspect.getdoc(self.__class__),
        )
        parser.add_argument(
            "-m",
            "--display-magnitude",
            type=float,
            help="Override the magnitude displayed in " "map labels.",
        )
        parser.add_argument(
            "-p",
            "--pickle-plots",
            action="store_true",
            default=False,
            help="Save the figure objects from each plot as a binary file that can be plotted over.",
        )
        #
        # This line should be in any modules that overrides this
        # one. It will collect up everything after the current
        # modules options in args.rem, which should be returned
        # by this function. Note: doing parser.parse_known_args()
        # will not work as it will suck up any later modules'
        # options that are the same as this one's.
        #
        parser.add_argument(
            "rem", nargs=argparse.REMAINDER, help=argparse.SUPPRESS
        )
        args = parser.parse_args(arglist)
        if args.display_magnitude:
            self.display_magnitude = args.display_magnitude
        if args.pickle_plots:
            self.pickle_plots = args.pickle_plots
        return args.rem

    def execute(self, datafile=None, outdir=None, config=None):
        """
        Raises:
            NotADirectoryError: When the event data directory does not exist.
            FileNotFoundError: When the the shake_result HDF file does not
                exist.
        """
        if self.process == "shakemap":
            install_path, data_path = get_config_paths()
            datadir = os.path.join(
                data_path, self._eventid, "current", "products"
            )
            datafile = os.path.join(datadir, "shake_result.hdf")
        else:
            if outdir is None:
                raise FileNotFoundError("outdir must be provided.")
            datadir = outdir
            if datafile is None:
                raise FileNotFoundError("datafile must be provided.")

        if not os.path.isdir(datadir):
            raise NotADirectoryError(f"{datadir} is not a valid directory.")
        if not os.path.isfile(datafile):
            raise FileNotFoundError(f"{datafile} does not exist.")

        # Open the ShakeMapOutputContainer and extract the data
        container = ShakeMapOutputContainer.load(datafile)
        if container.getDataType() != "grid":
            raise NotImplementedError(
                "mapping module can only operate on gridded data, not sets of points"
            )

        # get the path to the products.conf file, load the config
        if self.process == "shakemap":
            config_file = os.path.join(install_path, "config", "products.conf")
        else:
            config_file = os.path.join(config, "products.conf")
        spec_file = f'{get_configspec("products")}'
        config = ConfigObj(config_file, configspec=spec_file)
        validator = get_custom_validator()
        results = config.validate(validator)
        check_extra_values(config, self.logger)
        if not isinstance(results, bool) or not results:
            config_error(config, results)

        # create contour files
        self.logger.debug("Mapping...")

        # get the filter size from the products.conf
        filter_size = config["products"]["contour"]["filter_size"]

        # get the operator setting from config
        operator = config["products"]["mapping"]["operator"]

        # get all of the pieces needed for the mapping functions
        layers = config["products"]["mapping"]["layers"]
        if "topography" in layers and layers["topography"] != "":
            topofile = layers["topography"]
        else:
            topofile = None
        if "roads" in layers and layers["roads"] != "":
            roadfile = layers["roads"]
        else:
            roadfile = None
        if "faults" in layers and layers["faults"] != "":
            faultfile = layers["faults"]
        else:
            faultfile = None
        if "countries" in layers and layers["countries"] != "":
            countries_file = layers["countries"]
        else:
            countries_file = None
        if "states_provs" in layers and layers["states_provs"] != "":
            states_provs_file = layers["states_provs"]
        else:
            states_provs_file = None
        if "oceans" in layers and layers["oceans"] != "":
            oceans_file = layers["oceans"]
        else:
            oceans_file = None
        if "lakes" in layers and layers["lakes"] != "":
            lakes_file = layers["lakes"]
        else:
            lakes_file = None

        # Get the number of parallel workers
        max_workers = config["products"]["mapping"]["max_workers"]

        # Reading HDF5 files currently takes a long time, due to poor
        # programming in MapIO.  To save us some time until that issue is
        # resolved, we'll coarsely subset the topo grid once here and pass
        # it into both mapping functions
        # get the bounds of the map
        info = container.getMetadata()
        xmin = info["output"]["map_information"]["min"]["longitude"]
        xmax = info["output"]["map_information"]["max"]["longitude"]
        ymin = info["output"]["map_information"]["min"]["latitude"]
        ymax = info["output"]["map_information"]["max"]["latitude"]
        dy = float(
            info["output"]["map_information"]["grid_spacing"]["latitude"]
        )
        dx = float(
            info["output"]["map_information"]["grid_spacing"]["longitude"]
        )
        padx = 5 * dx
        pady = 5 * dy
        sxmin = float(xmin) - padx
        sxmax = float(xmax) + padx
        symin = float(ymin) - pady
        symax = float(ymax) + pady

        sampledict = GeoDict.createDictFromBox(
            sxmin, sxmax, symin, symax, dx, dy
        )
        if topofile:
            topogrid = read(
                topofile,
                samplegeodict=sampledict,
                resample=False,
                doPadding=True,
                padValue=0.0,
            )
        else:
            tdata = np.full([sampledict.ny, sampledict.nx], 0.0)
            topogrid = Grid2D(data=tdata, geodict=sampledict)

        model_config = container.getConfig()

        imtlist = container.getIMTs()

        textfile = (
            get_data_path()
            / "mapping"
            / ("map_strings." + config["products"]["mapping"]["language"])
        )
        text_dict = get_text_strings(textfile)
        if config["products"]["mapping"]["fontfamily"] != "":
            matplotlib.rcParams["font.family"] = config["products"]["mapping"][
                "fontfamily"
            ]
            matplotlib.rcParams["axes.unicode_minus"] = False

        allcities = Cities.fromDefault()
        states_provs = None
        countries = None
        oceans = None
        lakes = None
        faults = None
        roads = None
        if states_provs_file is not None:
            states_provs = ShapelyFeature(
                Reader(states_provs_file).geometries(),
                ccrs.PlateCarree(),
                facecolor="none",
            )
        elif "CALLED_FROM_PYTEST" not in os.environ:
            states_provs = cfeature.NaturalEarthFeature(
                category="cultural",
                name="admin_1_states_provinces_lines",
                scale="10m",
                facecolor="none",
            )
            # The feature constructor doesn't necessarily download the
            # data, but we want it to so that multiple threads don't
            # try to do it at once when they actually access the data.
            # So below we just call the geometries() method to trigger
            # the download if necessary.
            _ = states_provs.geometries()

        if countries_file is not None:
            countries = ShapelyFeature(
                Reader(countries_file).geometries(),
                ccrs.PlateCarree(),
                facecolor="none",
            )
        elif "CALLED_FROM_PYTEST" not in os.environ:
            countries = cfeature.NaturalEarthFeature(
                category="cultural",
                name="admin_0_countries",
                scale="10m",
                facecolor="none",
            )
            _ = countries.geometries()

        if oceans_file is not None:
            oceans = ShapelyFeature(
                Reader(oceans_file).geometries(),
                ccrs.PlateCarree(),
                facecolor=WATERCOLOR,
            )
        elif "CALLED_FROM_PYTEST" not in os.environ:
            oceans = cfeature.NaturalEarthFeature(
                category="physical",
                name="ocean",
                scale="10m",
                facecolor=WATERCOLOR,
            )
            _ = oceans.geometries()

        if lakes_file is not None:
            lakes = ShapelyFeature(
                Reader(lakes_file).geometries(),
                ccrs.PlateCarree(),
                facecolor=WATERCOLOR,
            )
        elif "CALLED_FROM_PYTEST" not in os.environ:
            lakes = cfeature.NaturalEarthFeature(
                category="physical",
                name="lakes",
                scale="10m",
                facecolor=WATERCOLOR,
            )
            _ = lakes.geometries()

        if faultfile is not None:
            faults = ShapelyFeature(
                Reader(faultfile).geometries(),
                ccrs.PlateCarree(),
                facecolor="none",
            )

        if roadfile is not None:
            roads = ShapelyFeature(
                Reader(roadfile).geometries(),
                ccrs.PlateCarree(),
                facecolor="none",
            )

        alist = []
        llogo = config["products"]["mapping"].get("license_logo") or None
        ltext = config["products"]["mapping"].get("license_text") or None
        for imtype in imtlist:
            _, imtype = imtype.split("/")
            comp = container.getComponents(imtype)[0]
            d = {
                "imtype": imtype,
                "topogrid": topogrid,
                "allcities": allcities,
                "states_provinces": states_provs,
                "countries": countries,
                "oceans": oceans,
                "lakes": lakes,
                "roads": roads,
                "roadcolor": layers["roadcolor"],
                "roadwidth": layers["roadwidth"],
                "faults": faults,
                "faultcolor": layers["faultcolor"],
                "faultwidth": layers["faultwidth"],
                "datadir": datadir,
                "operator": operator,
                "filter_size": filter_size,
                "info": info,
                "component": comp,
                "imtdict": container.getIMTGrids(imtype, comp),
                "ruptdict": copy.deepcopy(container.getRuptureDict()),
                "stationdict": container.getStationDict(),
                "config": model_config,
                "tdict": text_dict,
                "display_magnitude": self.display_magnitude,
                "pickle_plots": self.pickle_plots,
                "pdf_dpi": config["products"]["mapping"]["pdf_dpi"],
                "img_dpi": config["products"]["mapping"]["img_dpi"],
                "license_logo": llogo,
                "license_text": ltext,
            }
            alist.append(d)
            if imtype == "MMI":
                for value in d.values():
                    if hasattr(value, "_crs") and isinstance(
                        value._crs, ccrs.Projection
                    ):
                        value._crs = ccrs.PlateCarree()
                g = copy.deepcopy(d)
                g["imtype"] = "thumbnail"
                alist.append(g)
                h = copy.deepcopy(d)
                h["imtype"] = "overlay"
                alist.append(h)
                if self.process == "shakemap":
                    self.contents.addFile(
                        "intensityMap",
                        "Intensity Map",
                        "Map of macroseismic intensity.",
                        "intensity.jpg",
                        "image/jpeg",
                    )
                    self.contents.addFile(
                        "intensityMap",
                        "Intensity Map",
                        "Map of macroseismic intensity.",
                        "intensity.pdf",
                        "application/pdf",
                    )
                    self.contents.addFile(
                        "intensityThumbnail",
                        "Intensity Thumbnail",
                        "Thumbnail of intensity map.",
                        "pin-thumbnail.png",
                        "image/png",
                    )
                    self.contents.addFile(
                        "intensityOverlay",
                        "Intensity Overlay and World File",
                        "Macroseismic intensity rendered as a "
                        "PNG overlay and associated world file",
                        "intensity_overlay.png",
                        "image/png",
                    )
                    self.contents.addFile(
                        "intensityOverlay",
                        "Intensity Overlay and World File",
                        "Macroseismic intensity rendered as a "
                        "PNG overlay and associated world file",
                        "intensity_overlay.pngw",
                        "text/plain",
                    )
            else:
                fileimt = oq_to_file(imtype)
                if self.process == "shakemap":
                    self.contents.addFile(
                        fileimt + "Map",
                        fileimt.upper() + " Map",
                        "Map of " + imtype + ".",
                        fileimt + ".jpg",
                        "image/jpeg",
                    )
                    self.contents.addFile(
                        fileimt + "Map",
                        fileimt.upper() + " Map",
                        "Map of " + imtype + ".",
                        fileimt + ".pdf",
                        "application/pdf",
                    )

        if max_workers > 0:
            with cf.ProcessPoolExecutor(max_workers=max_workers) as ex:
                results = ex.map(make_map, alist)
                list(results)
        else:
            for adict in alist:
                make_map(adict)

        container.close()


def make_map(adict):

    imtype = adict["imtype"]

    if imtype == "thumbnail":
        make_pin_thumbnail(adict)
        return
    elif imtype == "overlay":
        make_overlay(adict)
        return

    fig1, fig2 = draw_map(adict)

    if imtype == "MMI":
        # save to pdf/jpeg
        pdf_file = os.path.join(adict["datadir"], "intensity.pdf")
        jpg_file = os.path.join(adict["datadir"], "intensity.jpg")
        # save the legend file
        legend_file = os.path.join(adict["datadir"], "mmi_legend.png")
        fig2.gca().xaxis.set_major_locator(NullLocator())
        fig2.gca().yaxis.set_major_locator(NullLocator())
        fig2.savefig(legend_file, bbox_inches="tight", pad_inches=0)
        if adict["pickle_plots"]:
            pickle_name = os.path.join(adict["datadir"], "intensity.pickle")
            with open(pickle_name, "wb") as fobj:
                dill.dump(fig1, fobj)
        plt.close(fig2)
    else:
        fileimt = oq_to_file(imtype)
        pdf_file = os.path.join(adict["datadir"], f"{fileimt}.pdf")
        jpg_file = os.path.join(adict["datadir"], f"{fileimt}.jpg")
        if adict["pickle_plots"]:
            pickle_name = os.path.join(adict["datadir"], f"{fileimt}.pickle")
            with open(pickle_name, "wb") as fobj:
                dill.dump(fig1, fobj)

    fig1.savefig(pdf_file, bbox_inches="tight", dpi=adict["pdf_dpi"])
    fig1.savefig(jpg_file, bbox_inches="tight", dpi=adict["img_dpi"])
    plt.close(fig1)


def make_pin_thumbnail(adict):
    """Make the artsy-thumbnail for the pin on the USGS webpages."""
    imtdict = adict["imtdict"]
    grid = np.nan_to_num(imtdict["mean"])
    metadata = imtdict["mean_metadata"]
    num_pixels = 300
    randx = np.random.rand(num_pixels)
    randy = np.random.rand(num_pixels)
    rx = (randx * metadata["nx"]).astype(np.int_)
    ry = (randy * metadata["ny"]).astype(np.int_)
    rvals = np.arange(num_pixels)

    x_grid = np.arange(400)
    y_grid = np.arange(400)

    mx_grid, my_grid = np.meshgrid(x_grid, y_grid)

    grid = griddata(
        np.hstack(
            [randx.reshape((-1, 1)) * 400, randy.reshape((-1, 1)) * 400]
        ),
        grid[ry, rx],
        (mx_grid, my_grid),
        method="nearest",
    )
    grid = (grid * 10 + 0.5).astype(np.int_).astype(np.float32) / 10.0

    rgrid = griddata(
        np.hstack(
            [randx.reshape((-1, 1)) * 400, randy.reshape((-1, 1)) * 400]
        ),
        rvals,
        (mx_grid, my_grid),
        method="nearest",
    )
    irgrid = rgrid.astype(np.int32)
    mypols = [p[0]["coordinates"] for p in rasterio.features.shapes(irgrid)]

    mmimap = ColorPalette.fromPreset("mmi")
    plt.figure(figsize=(2.75, 2.75), dpi=96, frameon=False)
    plt.axis("off")
    plt.tight_layout()
    plt.imshow(grid, cmap=mmimap.cmap, vmin=1.5, vmax=9.5)
    for pol in mypols:
        mycoords = list(zip(*pol[0]))
        plt.plot(mycoords[0], mycoords[1], color="#cccccc", linewidth=0.2)
    plt.savefig(
        os.path.join(adict["datadir"], "pin-thumbnail.png"),
        dpi=96,
        bbox_inches=matplotlib.transforms.Bbox([[0.47, 0.39], [2.50, 2.50]]),
        pad_inches=0,
    )


def get_text_strings(stringfile):
    """Read the file containing the translated text strings, remove the
    comments and parse as JSON.

    Args:
        stringfile (str): Path to the map_strings.xx file specified in the
            config. The file is assumend to be UTF-8.

    Returns:
        dict: A dictionary of strings for use in writing text to the maps.
    """
    if not os.path.isfile(stringfile):
        raise FileNotFoundError(f"File {stringfile} not found")
    f = open(stringfile, "rt", encoding="utf-8-sig")
    jline = ""
    for line in f:
        if line.startswith("//"):
            continue
        jline += line
    f.close()
    return json.loads(jline)


def make_overlay(adict):
    """
    Make a transparent PNG of intensity and a world file

    Args:
        adict (dict): The usual dictionary for the mapping functions.

    Returns:
        nothing: Nothing.
    """
    mmidict = adict["imtdict"]
    mmi_array = np.nan_to_num(mmidict["mean"])
    geodict = GeoDict(mmidict["mean_metadata"])
    palette = ColorPalette.fromPreset("mmi")
    mmi_rgb = palette.getDataColor(mmi_array, color_format="array")
    img = Image.fromarray(mmi_rgb)
    pngfile = os.path.join(adict["datadir"], "intensity_overlay.png")
    img.save(pngfile, "PNG")

    # write out a world file
    # https://en.wikipedia.org/wiki/World_file
    worldfile = os.path.join(adict["datadir"], "intensity_overlay.pngw")
    with open(worldfile, "wt", encoding="utf-8") as f:
        f.write(f"{geodict.dx:.4f}\n")
        f.write("0.0\n")
        f.write("0.0\n")
        f.write(f"-{geodict.dy:.4f}\n")
        f.write(f"{geodict.xmin:.4f}\n")
        f.write(f"{geodict.ymax:.4f}\n")
    return


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Generate maps from shake_results.hdf file.
    """
    datafile, outdir, logdir, config = get_cli_args(description, config=True)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "mapping.log")
    logger = get_generic_logger(logfile=logfile)

    mod = MappingModule("noid", process="main", logger=logger)
    mod.execute(datafile=datafile, outdir=outdir, config=config)


if __name__ == "__main__":
    main()
