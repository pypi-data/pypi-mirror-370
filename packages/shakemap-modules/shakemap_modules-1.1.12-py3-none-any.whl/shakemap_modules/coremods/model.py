"""
Process a ShakeMap, based on the configuration and data found in
shake_data.hdf, and produce output in shake_result.hdf.
"""

# stdlib imports
import argparse
import copy
import importlib.metadata
import inspect
import json
import os
import os.path
import pathlib
import shutil

# import secrets
from datetime import date
from time import gmtime, strftime

# third party imports
import cartopy.io.shapereader as shpreader
import fiona
import numpy as np
import numpy.ma as ma
import openquake.hazardlib.const as oqconst
from openquake.hazardlib.imt import SA
from openquake.hazardlib import imt
import pandas as pd
from shapely.geometry import shape

# local imports
from esi_core.shakemap.covariance_matrix import (
    make_sd_array,
    make_sigma_matrix,
)
from esi_core.shakemap.geodetic_distances import geodetic_distance_fast
from esi_shakelib.directivity.rowshandel2013 import Rowshandel2013
from esi_shakelib.multigmpe import MultiGMPE
from esi_shakelib.sites import Sites, addDepthParameters
from esi_shakelib.utils.containers import ShakeMapInputContainer
from esi_shakelib.utils.imt_string import oq_to_file
from esi_shakelib.utils.utils import (
    get_extent,
    get_shakelib_version,
    #    thirty_sec_max,
    #    thirty_sec_min,
)
from esi_shakelib.virtualipe import VirtualIPE
from esi_shakelib.ffsimmer import FFSimmer, RandomFiniteFault
from esi_shakelib.generic_site_amplitication import GenericSiteAmplification
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from esi_utils_rupture import constants
from esi_utils_rupture.distance import (
    Distance,
    get_distance,
    get_distance_measures,
)
from esi_utils_rupture.point_rupture import PointRupture
from mapio.geodict import GeoDict
from mapio.grid2d import Grid2D
from shakemap_modules.base.base import Contents, CoreModule
from shakemap_modules.base.cli import get_module_args
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.utils.generic_amp import get_generic_amp_factors
from shakemap_modules.utils.logging import get_generic_logger
from shakemap_modules.utils.utils import get_object_from_config

# from shakemap.utils.exception import TerminateShakeMap


#
# default_stddev_inter: This is a stand-in for tau when the gmpe set
#                       doesn't provide it. It is an educated guess based
#                       on the NGA-west, Akkar et al, and BC Hydro gmpes.
#                       It's not perfect, but probably isn't too far off.
#                       It is only used when the GMPE(s) don't provide a
#                       breakdown of the uncertainty terms. When used,
#                       this value is multiplied by the total standard
#                       deviation to get tau. The square of tau is then
#                       subtracted from the squared total stddev and the
#                       square root of the result is then used as the
#                       within-event stddev (phi).
#
SM_CONSTS = {"default_stddev_inter": 0.55, "default_stddev_inter_mmi": 0.55}

stddev_types = [
    oqconst.StdDev.TOTAL,
    oqconst.StdDev.INTER_EVENT,
    oqconst.StdDev.INTRA_EVENT,
]

FFSIMMER_SEED = 84608478034892579362136552699077168019


class DataFrame:
    """
    Class to hold the two types of dataframes (instrumented and
    non-instrumented)
        df - the actual dataframe
        imts - the IMTs present in df
        sx - the sites context for the dataframe
        dx - the distance context for the dataframe
    """

    def __init__(self):
        self.df = None  # noqa
        self.imts = None  # noqa
        self.sx = None  # noqa
        self.dx = None  # noqa


class ModelModule(CoreModule):
    """
    model -- Interpolate ground motions to a grid or list of locations.
    """

    command_name = "model"
    targets = [r"products/shake_result\.hdf"]
    dependencies = [("shake_data.hdf", True)]

    no_seismic = False
    no_macroseismic = False
    no_rupture = False
    use_simulations = False

    rock_vs30 = 760.0
    soil_vs30 = 180.0

    def __init__(
        self,
        eventid,
        process="shakemap",
        logger=None,
        no_seismic=False,
        no_macroseismic=False,
        no_rupture=False,
        shakemap_version=None,
    ):
        super(ModelModule, self).__init__(eventid, logger=logger)
        if process == "shakemap":
            self.contents = Contents(None, None, eventid)
        self.process = process
        self.no_seismic = no_seismic
        self.no_macroseismic = no_macroseismic
        self.no_rupture = no_rupture
        self.shakemap_version = shakemap_version
        #
        # Set up a bunch of dictionaries that will be keyed to IMTs
        #
        self.nominal_bias = {}  # holds an average bias for each IMT
        self.psd_raw = {}  # raw phi (intra-event stddev) of the output points
        self.psd = {}  # phi (intra-event stddev) of the output points
        self.tsd = {}  # tau (inter-event stddev) of the output points
        #
        # These are arrays (keyed by IMT) of the station data that will be
        # used to compute the bias and do the interpolation, they are filled
        # in the _fill_data_arrays method
        #
        self.sta_per_ix = {}
        self.sta_lons_rad = {}
        self.sta_lats_rad = {}
        self.sta_resids = {}
        self.sta_phi = {}
        self.sta_tau = {}
        self.sta_sig_extra = {}
        self.sta_rrups = {}
        self.pred_out = {}
        self.pred_out_sd = {}
        #
        # These are useful matrices that we compute in the bias function
        # that we can reuse in the MVN function
        #
        self.t_d = {}
        self.cov_wd_wd_inv = {}
        self.mu_h_yd = {}
        self.cov_hh_yd = {}
        #
        # Some variables and arrays used in both the bias and MVN functions
        #
        self.no_native_flag = {}
        self.imt_types = {}
        self.len_types = {}
        self.imt_y_ind = {}
        #
        # These hold the main outputs of the MVN
        #
        self.outgrid = {}  # Holds the interpolated output arrays keyed by IMT
        self.outsd = {}  # Holds the standard deviation arrays keyed by IMT
        self.outphi = {}  # Holds the intra-event standard deviation arrays
        self.outtau = {}  # Holds the inter-event standard deviation arrays
        #
        # Places to put the results for the attenuation plots
        #
        self.atten_rock_mean = {}
        self.atten_soil_mean = {}
        self.atten_rock_sd = {}
        self.atten_soil_sd = {}
        #
        # Helper parameters initialized in execute and elsewhere
        #
        self.config = None
        self.sim_imt_paths = None
        self.default_gmpe = None
        self.rupture_obj = None
        self.origin = None
        self.rx = None
        self.rff = None
        self.gmice = None
        self.ipe_gmpe = None
        self.ipe = None
        self.ipe_extent = None
        self.ipe_total_sd_only = False
        self.ipe_stddev_types = None
        self.atten_coords = None
        self.point_source = None
        self.gmpe_total_sd_only = False
        self.gmpe_stddev_types = None
        self.do_directivity = False
        self.dir_results = None
        self.dir_output = None
        self.sim_df = None
        self.imt_per = None
        self.imt_per_ix = None
        self.ccf = None
        self.datadir = None
        self.ic = None
        self.apply_gafs = False
        self.do_bias = True
        self.bias_max_range = None
        self.bias_max_mag = None
        self.bias_max_dsigma = None
        self.do_outliers = True
        self.outlier_deviation_level = None
        self.outlier_max_mag = None
        self.outlier_valid_stations = None
        self.imt_out_set = None
        self.smdx = None
        self.smdy = None
        self.nmax = None
        self.vs30default = None
        self.vs30_file = None
        self.mask_file = None
        self.west = None
        self.east = None
        self.south = None
        self.north = None
        self.sx_out = None
        self.dx_out = None
        self.smnx = None
        self.smny = None
        self.lons = None
        self.lats = None
        self.depths = None
        self.idents = None
        self.vs30 = None
        self.atten_sx_rock = None
        self.atten_sx_soil = None
        self.atten_dx = None
        self.lons_out_rad = None
        self.lats_out_rad = None
        self.flip_lons = False
        self.dataframes = None
        self.stations = None
        self.do_grid = True
        self.sites_obj_out = None
        self.max_workers = None
        self.rez_add_uncertainty = {}
        self.rez_sigma_hh_yd = {}
        self.rez_c = {}
        self.rez_sta_per_ix = {}
        self.directivity = None
        self.info = {"multigmpe": {}}
        # self.rng_seed = secrets.randbits(128)
        self.rng_seed = FFSIMMER_SEED
        self.true_grid = False
        self.gmpe_dict = {}
        self.oqimt_dict = {}
        self.full_out_set = None

    def parseArgs(self, arglist):
        """
        Set up the object to accept the --no_seismic, --no_macroseismic,
        and --no_rupture flags.
        """
        parser = argparse.ArgumentParser(
            prog=self.__class__.command_name,
            description=inspect.getdoc(self.__class__),
        )
        parser.add_argument(
            "-s",
            "--no_seismic",
            action="store_true",
            help="Exclude instrumental seismic data from "
            "the processing, ignoring any that may exist in "
            "the input directory.",
        )
        parser.add_argument(
            "-m",
            "--no_macroseismic",
            action="store_true",
            help="Exclude macroseismic data from the "
            "processing, ignoring any that may exist in the "
            "input directory.",
        )
        parser.add_argument(
            "-r",
            "--no_rupture",
            action="store_true",
            help="Exclude a rupture model from the "
            "processing, ignoring any that may exist in the "
            "input directory.",
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
        if args.no_seismic:
            self.no_seismic = True
        if args.no_macroseismic:
            self.no_macroseismic = True
        if args.no_rupture:
            self.no_rupture = True
        return args.rem

    def execute(self, indir=None, outdir=None):
        """
        Interpolate ground motions to a grid or list of locations.

        Raises:
            NotADirectoryError: When the event data directory does not exist.
            FileNotFoundError: When the the shake_data HDF file does not exist.
        """
        self.logger.debug("Starting model...")
        # ---------------------------------------------------------------------
        # Make the input container and extract the config
        # ---------------------------------------------------------------------
        self._set_input_container(indir=indir)
        self.config = self.ic.getConfig()

        self.sim_imt_paths = [
            x for x in self.ic.getArrays() if "simulations" in x
        ]
        if len(self.sim_imt_paths):
            self.use_simulations = True

        self.config["use_simulations"] = self.use_simulations

        # ---------------------------------------------------------------------
        # Clear away results from previous runs
        # ---------------------------------------------------------------------
        self._clear_products()

        # ---------------------------------------------------------------------
        # Retrieve a bunch of config options and set them as attributes
        # ---------------------------------------------------------------------
        self._set_config_options()

        # ---------------------------------------------------------------------
        # Set up the gmpes and output imts that we can make
        # We assume that we're making MMI
        # ---------------------------------------------------------------------
        if "MMI" in self.imt_out_set:
            self.imt_out_set.remove("MMI")
            do_mmi = True
        else:
            do_mmi = False
        imt_set = set()
        for imt_str in self.imt_out_set:
            oqimt = imt.from_string(imt_str)
            gmpe = MultiGMPE.__from_config__(self.config, filter_imt=oqimt)
            if gmpe is None:
                continue
            imt_set.add(imt_str)
            self.gmpe_dict[oqimt] = gmpe
            self.oqimt_dict[imt_str] = oqimt
        self.imt_out_set = imt_set
        self.full_out_set = copy.copy(imt_set)
        if do_mmi:
            self.full_out_set.add("MMI")
        # ---------------------------------------------------------------------
        # If we're making a virtual IPE, make sure the PGV or PGA is in the
        # list of IMTs and GMPEs. (Yes, we could use SA(1.0), but we're not
        # gonna.)
        # ---------------------------------------------------------------------
        if (
            self.config["ipe_modules"][self.config["modeling"]["ipe"]][0]
            == "VirtualIPE"
        ):
            if not any(e for e in ["PGV", "PGA"] if e in self.imt_out_set):
                oqimt = imt.from_string("PGV")
                gmpe = MultiGMPE.__from_config__(self.config, filter_imt=oqimt)
                if gmpe is not None:
                    self.imt_out_set.add("PGV")
                    self.gmpe_dict[oqimt] = gmpe
                    self.oqimt_dict["PGV"] = oqimt
                else:
                    oqimt = imt.from_string("PGA")
                    gmpe = MultiGMPE.__from_config__(
                        self.config, filter_imt=oqimt
                    )
                    if gmpe is not None:
                        self.imt_out_set.add("PGA")
                        self.gmpe_dict[oqimt] = gmpe
                        self.oqimt_dict["PGA"] = oqimt
                    else:
                        raise TypeError(
                            "Your gmpe set can't make PGV or PGA, please pick"
                            " an IPE instead of the VirtualIPE"
                        )

        # ---------------------------------------------------------------------
        # Here we make a placeholder gmpe so that we can make the
        # rupture and distance contexts;
        # ---------------------------------------------------------------------
        self.default_gmpe = MultiGMPE.__from_config__(self.config)

        # ---------------------------------------------------------------------
        # Get the rupture object and rupture context
        # ---------------------------------------------------------------------
        self.rupture_obj = self.ic.getRuptureObject()
        self.origin = self.rupture_obj.getOrigin()
        # If the --no_rupture flag is used, switch to a PointRupture
        if self.no_rupture:
            self.rupture_obj = PointRupture(self.origin)
        if self.config["modeling"]["mechanism"] is not None:
            self.origin.setMechanism(mech=self.config["modeling"]["mechanism"])
        self.rx = self.rupture_obj.getRuptureContext([self.default_gmpe])

        # ---------------------------------------------------------------------
        # Add mechanism and tectonic regime to origin
        # ---------------------------------------------------------------------
        try:
            strecdata = self.ic.getStrecJson()
        except AttributeError:
            self.origin.mech = "ALL"
            self.origin.tectonic_region = "unknown"
            self.origin.slab_model_dip = 65.0
            self.origin.slab_model_strike = 0.0
            self.origin.sub_interface_prob = 0.0
            self.origin.sub_crustal_prob = 0.0
            self.origin.sub_slab_prob = 0.0
        else:
            strec_results = json.loads(strecdata)
            self.origin.mech = strec_results["FocalMechanism"]
            self.origin.tectonic_region = strec_results["TectonicRegion"]
            self.origin.slab_model_dip = strec_results["SlabModelDip"]
            self.origin.slab_model_strike = strec_results["SlabModelStrike"]
            self.origin.sub_interface_prob = strec_results[
                "ProbabilitySubductionInterface"
            ]
            self.origin.sub_crustal_prob = strec_results[
                "ProbabilitySubductionCrustal"
            ]
            self.origin.sub_slab_prob = strec_results[
                "ProbabilitySubductionIntraslab"
            ]

        # Get a set of random finite faults for FFSimmer
        if isinstance(self.rupture_obj, PointRupture):
            self.rff = RandomFiniteFault(
                self.origin,
                self.config["modeling"]["ffsim_nsim"],
                min_strike=self.config["modeling"]["ffsim_min_strike"],
                max_strike=self.config["modeling"]["ffsim_max_strike"],
                min_dip=self.config["modeling"]["ffsim_min_dip"],
                max_dip=self.config["modeling"]["ffsim_max_dip"],
                dy_min_frac=self.config["modeling"]["ffsim_dy_min_frac"],
                dy_max_frac=self.config["modeling"]["ffsim_dy_max_frac"],
                ztor=self.config["modeling"]["ffsim_ztor"],
                aspect_ratio=self.config["modeling"]["ffsim_aspect_ratio"],
                min_sz_depth=self.config["modeling"]["ffsim_min_sz_depth"],
                max_sz_depth=self.config["modeling"]["ffsim_max_sz_depth"],
                area_trunc=self.config["modeling"]["ffsim_area_trunc"],
                seed=self.rng_seed,
            )
            # with open("rupt_quads.txt", "wt", encoding="utf-8") as f:
            #     for irupt in self.rff.rupts:
            #         irupt.writeTextFile(f)

            if self.config["modeling"]["ffsim_true_grid"] is True:
                self.true_grid = True

        # ---------------------------------------------------------------------
        # Instantiate the gmpe, gmice, and ipe
        # ---------------------------------------------------------------------

        self.gmice = get_object_from_config("gmice", "modeling", self.config)

        # ---------------------------------------------------------------------
        # Set up the IPE or Virtual IPE
        # ---------------------------------------------------------------------
        if (
            self.config["ipe_modules"][self.config["modeling"]["ipe"]][0]
            == "VirtualIPE"
        ):
            if "PGV" in self.imt_out_set:
                ipe_imt = self.oqimt_dict["PGV"]
            elif "PGA" in self.imt_out_set:
                ipe_imt = self.oqimt_dict["PGA"]
            else:
                raise ValueError("This should never happen.")
            self.ipe_gmpe = self.gmpe_dict[ipe_imt]
            self.ipe = VirtualIPE.__fromFuncs__(
                self.ipe_gmpe, self.gmice, rupture_obj=self.rupture_obj
            )
            self.ipe_extent = VirtualIPE.__fromFuncs__(
                self.ipe_gmpe, self.gmice
            )
        else:
            ipe = get_object_from_config("ipe", "modeling", self.config)
            if "vs30" not in ipe.REQUIRES_SITES_PARAMETERS:
                # REQUIRES_SITES_PARAMETERS is now a frozen set so we have to
                # work around it
                tmpset = set(ipe.REQUIRES_SITES_PARAMETERS)
                tmpset.add("vs30")
                ipe.REQUIRES_SITES_PARAMETERS = frozenset(tmpset)
            ipe.DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = (
                oqconst.IMC.GREATER_OF_TWO_HORIZONTAL
            )
            self.ipe = MultiGMPE.__from_list__([ipe], [1.0])
            self.ipe_extent = self.ipe

        ipe_sd_types = self.ipe.DEFINED_FOR_STANDARD_DEVIATION_TYPES
        if len(ipe_sd_types) == 1:
            self.ipe_total_sd_only = True
            self.ipe_stddev_types = [oqconst.StdDev.TOTAL]
        else:
            self.ipe_total_sd_only = False
            self.ipe_stddev_types = [
                oqconst.StdDev.TOTAL,
                oqconst.StdDev.INTER_EVENT,
                oqconst.StdDev.INTRA_EVENT,
            ]

        #
        # Set up the coordinates for the attenuation curves
        #
        repi = np.logspace(-1, 3, 200)
        pt = self.origin.getHypo()
        self.atten_coords = {
            "lons": np.full_like(repi, pt.x),
            "lats": np.array([pt.y + x / 111.0 for x in repi]),
        }
        self.point_source = PointRupture(self.origin)

        # ---------------------------------------------------------------------
        # The output locations: either a grid or a list of points
        # ---------------------------------------------------------------------
        self.logger.debug("Setting output params...")
        self._set_output_params()

        landmask = self._get_land_mask()
        # We used to do this, but we've decided not to. Leaving the code
        # in place in case we change our minds.
        # if landmask is not None and np.all(landmask):
        #     raise TerminateShakeMap("Mapped area is entirely water")

        # ---------------------------------------------------------------------
        # If the gmpe doesn't break down its stardard deviation into
        # within- and between-event terms, we need to handle things
        # somewhat differently.
        # ---------------------------------------------------------------------
        gmpe_sd_types = self.default_gmpe.DEFINED_FOR_STANDARD_DEVIATION_TYPES
        if len(gmpe_sd_types) == 1:
            self.gmpe_total_sd_only = True
            self.gmpe_stddev_types = [oqconst.StdDev.TOTAL]
        else:
            self.gmpe_total_sd_only = False
            self.gmpe_stddev_types = [
                oqconst.StdDev.TOTAL,
                oqconst.StdDev.INTER_EVENT,
                oqconst.StdDev.INTRA_EVENT,
            ]

        # ---------------------------------------------------------------------
        # Are we going to include directivity?
        # ---------------------------------------------------------------------
        dir_conf = self.config["modeling"]["directivity"]

        # Is the rupture not a point source?
        rup_check = not isinstance(self.rupture_obj, PointRupture)

        if dir_conf and rup_check:
            self.do_directivity = True
            # The following attribute will be used to store a list of tuples,
            # where each tuple will contain the 1) result of the directivity
            # model (for the periods defined by Rowshandel2013) and 2) the
            # associated distance context. The distance context is needed
            # within the _gmas function for figuring out which of the results
            # should be used when combining it with the GMPE result. We store
            # the pre-defined period first and interpolate later because there
            # is some optimization to doing it this way (some of the
            # calculation is period independent).
            self.dir_results = []
            # But if we want to save the results that were actually used for
            # each IMT, so we use a dictionary. This uses keys that are
            # the same as self.outgrid.
            self.dir_output = {}
        else:
            self.do_directivity = False

        # ---------------------------------------------------------------------
        # Station data: Create DataFrame(s) with the input data:
        # df1 for instrumented data
        # df2 for non-instrumented data
        # ---------------------------------------------------------------------
        self.logger.debug("Setting data frames...")
        self._set_data_frames()

        # ---------------------------------------------------------------------
        # Add the predictions, etc. to the data frames
        # ---------------------------------------------------------------------
        self.logger.debug("Populating data frames...")
        self._populate_data_frames()

        # ---------------------------------------------------------------------
        # Try to make all the derived IMTs possible from MMI (if we have MMI)
        # ---------------------------------------------------------------------
        self._derive_imts_from_mmi()
        # ---------------------------------------------------------------------
        # Now make MMI from the station data where possible
        # ---------------------------------------------------------------------
        self._derive_mmi_from_imts()

        self.logger.debug("Getting combined IMTs")

        # ---------------------------------------------------------------------
        # Get the combined set of input and output IMTs, their periods,
        # and an index dictionary, then make the cross-correlation function
        # ---------------------------------------------------------------------
        if self.use_simulations:
            #
            # Ignore what is in the configuration and make maps only for the
            # IMTs that are in the set of simulations (and MMI).
            #
            combined_imt_set = set(
                [x.split("/")[-1] for x in self.sim_imt_paths]
            )
            self.sim_df = {}
            for imtstr in combined_imt_set:
                dset, _ = self.ic.getArray(["simulations"], imtstr)
                self.sim_df[imtstr] = dset
            if do_mmi:
                combined_imt_set |= set(["MMI"])
        else:
            combined_imt_set = self.full_out_set.copy()
            for ndf in self.dataframes:
                combined_imt_set |= getattr(self, ndf).imts

        self.imt_per, self.imt_per_ix = _get_period_arrays(combined_imt_set)
        self.ccf = get_object_from_config(
            "ccf", "modeling", self.config, self.imt_per
        )

        self.logger.debug("Doing bias")

        # ---------------------------------------------------------------------
        # Do the bias for all of the input and output IMTs. Hold on
        # to some of the products that will be used for the interpolation.
        # The "raw" values are the stddevs that have not been inflated by
        # the additional sigma (if any) of the point-source to finite
        # rupture approximation.
        # ---------------------------------------------------------------------

        # ---------------------------------------------------------------------
        # Do some prep, the bias, and the directivity prep
        # ---------------------------------------------------------------------
        self._fill_data_arrays()

        self._compute_bias()

        self._compute_directivity_prediction_locations()

        # ---------------------------------------------------------------------
        # Now do the MVN with the intra-event residuals
        # ---------------------------------------------------------------------
        self.logger.debug("Doing MVN...")
        # if self.max_workers > 0:
        #     with cf.ThreadPoolExecutor(max_workers=self.max_workers) as ex:
        #         results = ex.map(self._compute_mvn, self.imt_out_set)
        #         list(results)  # Check threads for possible exceptions, etc.
        # else:

        full_oqimt_dict = copy.copy(self.oqimt_dict)
        if do_mmi:
            immi = imt.from_string("MMI")
            full_oqimt_dict["MMI"] = immi
        if isinstance(self.rupture_obj, PointRupture):
            ffsim = FFSimmer(self.rff, measure="mean")
            vs30grid = self.sites_obj_out.getVs30Grid()
            if self.do_grid:
                if self.true_grid:
                    griddict = ffsim.true_grid(
                        vs30grid,
                        self.gmpe_dict,
                        list(self.oqimt_dict.values()),
                    )
                    if self.apply_gafs:
                        for oqimt in self.oqimt_dict.values():
                            gafs = get_generic_amp_factors(
                                self.dx_out, str(oqimt)
                            )
                            if gafs is not None:
                                griddict[oqimt]["mean"] += gafs
                else:
                    griddict = ffsim.compute_grid(
                        vs30grid,
                        self.gmpe_dict,
                        list(self.oqimt_dict.values()),
                    )
                    gsa = GenericSiteAmplification(
                        self.origin.tectonic_region,
                        vs30grid.getData(),
                    )
                    oqpga = imt.PGA()
                    for oqimt in self.oqimt_dict.values():
                        amp_grid = gsa.applySiteAmp(
                            griddict[oqimt]["mean"],
                            griddict[oqpga]["mean"],
                            oqimt,
                        )
                        if self.apply_gafs:
                            gafs = get_generic_amp_factors(
                                self.dx_out, str(oqimt)
                            )
                            if gafs is not None:
                                amp_grid += gafs
                        griddict[oqimt]["mean"] = amp_grid
            else:
                shapes = []
                for k, v in vars(self.sx_out).items():
                    if k in ["lons", "lats"]:
                        continue
                    shapes.append(v.shape)
                    setattr(self.sx_out, k, np.reshape(v, (-1,)))
                shapeset = set(shapes)
                if len(shapeset) != 1:
                    raise ValueError(
                        "All sites elements must have same shape."
                    )
                orig_shape = list(shapeset)[0]
                ptdict = ffsim.compute_points(
                    self.sx_out, self.gmpe_dict, list(self.oqimt_dict.values())
                )
                griddict = {}
                for oqimt in self.oqimt_dict.values():
                    griddict[oqimt] = {}
                    for kk, vv in ptdict[oqimt]["site"].items():
                        griddict[oqimt][kk] = vv.reshape(orig_shape)
                        if self.apply_gafs and kk == "mean":
                            gafs = get_generic_amp_factors(
                                self.dx_out, str(oqimt)
                            )
                            if gafs is not None:
                                griddict[oqimt][kk] += gafs
            # Compute MMI from PGMs or IPE
            if do_mmi:
                immi = imt.MMI()
                griddict[immi] = {}
                if isinstance(self.ipe, VirtualIPE):
                    gmice_imt = self.ipe.imt
                    griddict[immi]["mean"], dmda = self.gmice.getMIfromGM(
                        griddict[gmice_imt]["mean"],
                        gmice_imt,
                        self.dx_out.repi,
                        self.rx.mag,
                    )
                    gm2mi_var = (self.gmice.getGM2MIsd()[gmice_imt]) ** 2
                    dmda *= dmda

                    if self.apply_gafs:
                        gafs = get_generic_amp_factors(self.dx_out, str(immi))
                        if gafs is not None:
                            griddict[immi]["mean"] += gafs
                    for sdt in stddev_types:
                        if sdt not in griddict[gmice_imt]:
                            continue
                        gm_var_in_mmi = dmda * griddict[gmice_imt][sdt] ** 2
                        if sdt == oqconst.StdDev.INTER_EVENT:
                            griddict[immi][sdt] = np.sqrt(gm_var_in_mmi)
                        else:
                            griddict[immi][sdt] = np.sqrt(
                                gm2mi_var + gm_var_in_mmi
                            )
                else:
                    ffsim = FFSimmer(self.rff, measure="mean")
                    if self.do_grid:
                        if self.true_grid:
                            mmidict = ffsim.true_grid(
                                self.sites_obj_out.getVs30Grid(),
                                {immi: self.ipe},
                                [immi],
                            )
                        else:
                            mmidict = ffsim.compute_grid(
                                self.sites_obj_out.getVs30Grid(),
                                {immi: self.ipe},
                                [immi],
                            )
                        for sdt in mmidict[immi]:
                            griddict[immi][sdt] = mmidict[immi][sdt]
                        if self.apply_gafs:
                            gafs = get_generic_amp_factors(
                                self.dx_out, str(immi)
                            )
                            if gafs is not None:
                                griddict[immi]["mean"] += gafs
                    else:
                        ptdict = ffsim.compute_points(
                            self.sx_out, {immi: self.ipe}, [immi]
                        )
                        for sdt in ptdict[immi]["site"]:
                            griddict[immi][sdt] = ptdict[immi]["site"][sdt]
                            if self.apply_gafs and sdt == "mean":
                                gafs = get_generic_amp_factors(
                                    self.dx_out, str(immi)
                                )
                                if gafs is not None:
                                    griddict[immi][sdt] += gafs
        else:
            griddict = {}
            shapes = []
            # Reshape the 2D stuff into 1D for the OQ GMMs
            for dd in (self.sx_out, self.dx_out):
                for k, v in vars(dd).items():
                    if dd == self.sx_out and k in ["lons", "lats"]:
                        continue
                    shapes.append(v.shape)
                    setattr(dd, k, np.reshape(v, (-1,)))
            shapeset = set(shapes)
            if len(shapeset) != 1:
                raise ValueError(
                    "All dists and sites elements must have same shape."
                )
            orig_shape = list(shapeset)[0]
            for imt_str in self.full_out_set:
                oqimt = full_oqimt_dict[imt_str]
                if imt_str == "MMI":
                    gmpe = self.ipe
                else:
                    gmpe = self.gmpe_dict[oqimt]
                pout_mean, pout_sd = self._gmas(
                    gmpe, self.sx_out, self.dx_out, oqimt, self.apply_gafs
                )
                griddict[oqimt] = {
                    "mean": pout_mean.reshape(orig_shape),
                    oqconst.StdDev.TOTAL: pout_sd[0].reshape(orig_shape),
                }
                if len(pout_sd) > 1:
                    griddict[oqimt][oqconst.StdDev.INTER_EVENT] = pout_sd[
                        1
                    ].reshape(orig_shape)
                    griddict[oqimt][oqconst.StdDev.INTRA_EVENT] = pout_sd[
                        2
                    ].reshape(orig_shape)
            # Undo reshapes of inputs
            for dd in (self.dx_out, self.sx_out):
                for k, v in vars(dd).items():
                    if dd == self.sx_out and k in ["lons", "lats"]:
                        continue
                    setattr(dd, k, np.reshape(v, orig_shape))

        for imt_str in self.full_out_set:
            oqimt = full_oqimt_dict[imt_str]
            if imt_str == "MMI":
                gmpe = self.ipe
            else:
                gmpe = self.gmpe_dict[oqimt]
            #
            # Make the attenuation curves
            #
            x_mean, x_sd = self._gmas(
                gmpe,
                self.atten_sx_rock,
                self.atten_dx,
                oqimt,
                False,
            )
            self.atten_rock_mean[imt_str] = x_mean
            self.atten_rock_sd[imt_str] = x_sd[0]
            x_mean, x_sd = self._gmas(
                gmpe,
                self.atten_sx_soil,
                self.atten_dx,
                oqimt,
                False,
            )
            self.atten_soil_mean[imt_str] = x_mean
            self.atten_soil_sd[imt_str] = x_sd[0]
            self._compute_mvn(imt_str, griddict[oqimt])

        self._apply_custom_mask()

        # ---------------------------------------------------------------------
        # Output the data and metadata
        # ---------------------------------------------------------------------
        if self.process == "shakemap":
            product_path = os.path.join(self.datadir, "products")
        else:
            product_path = outdir
        if not os.path.isdir(product_path):
            os.mkdir(product_path)
        oc = ShakeMapOutputContainer.create(
            os.path.join(product_path, "shake_result.hdf")
        )

        # ---------------------------------------------------------------------
        # Might as well stick the whole config in the result
        # ---------------------------------------------------------------------
        oc.setConfig(self.config)

        # ---------------------------------------------------------------------
        # We're going to need masked arrays of the output grids later, so
        # make them now.
        # ---------------------------------------------------------------------
        moutgrid = self._get_masked_grids(landmask)

        # ---------------------------------------------------------------------
        # Get the info dictionary that will become info.json, and
        # store it in the output container
        # ---------------------------------------------------------------------
        info = self._get_info(moutgrid)
        oc.setMetadata(info)

        # ---------------------------------------------------------------------
        # Add the rupture JSON as a text string
        # ---------------------------------------------------------------------
        oc.setRuptureDict(self.rupture_obj.getGeoJson())

        # ---------------------------------------------------------------------
        # Fill the station dictionary for stationlist.json and add it to
        # the output container
        # ---------------------------------------------------------------------
        sjdict = self._fill_station_json()
        oc.setStationDict(sjdict)

        # ---------------------------------------------------------------------
        # Add the output grids or points to the output; include some
        # metadata.
        # ---------------------------------------------------------------------
        if self.do_grid:
            self._store_gridded_data(oc)
        else:
            self._store_point_data(oc)

        self._store_attenuation_data(oc)

        oc.close()
        self.ic.close()

        if self.process == "shakemap":
            self.contents.addFile(
                "shakemapHDF",
                "Comprehensive ShakeMap HDF Data File",
                "HDF file containing all ShakeMap results.",
                "shake_result.hdf",
                "application/x-bag",
            )

    # -------------------------------------------------------------------------
    # End execute()
    # -------------------------------------------------------------------------

    def _set_input_container(self, indir=None):
        """
        Open the input container and set
        the event's current data directory.

        Raises:
            NotADirectoryError: When the event data directory does not exist.
            FileNotFoundError: When the the shake_data HDF file does not exist.
        """
        #
        # Find the shake_data.hdf file
        #
        if self.process == "shakemap":
            _, data_path = get_config_paths()
            datadir = os.path.join(data_path, self._eventid, "current")
        else:
            datadir = indir
        if not os.path.isdir(datadir):
            raise NotADirectoryError(f"{datadir} is not a valid directory.")

        datafile = os.path.join(datadir, "shake_data.hdf")
        if not os.path.isfile(datafile):
            raise FileNotFoundError(f"{datafile} does not exist.")
        self.datadir = datadir
        self.ic = ShakeMapInputContainer.load(datafile)

    def _clear_products(self):
        """
        Function to delete an event's products directory if it exists.

        Returns:
            nothing
        """
        products_path = os.path.join(self.datadir, "products")
        if os.path.isdir(products_path):
            shutil.rmtree(products_path, ignore_errors=True)
        pdl_path = os.path.join(self.datadir, "pdl")
        if os.path.isdir(pdl_path):
            shutil.rmtree(pdl_path, ignore_errors=True)

    def _set_config_options(self):
        """
        Pull various useful configuration options out of the config
        dictionary.

        Returns:
            nothing
        """
        # ---------------------------------------------------------------------
        # Processing parameters
        # ---------------------------------------------------------------------
        self.max_workers = self.config["system"]["max_workers"]

        # ---------------------------------------------------------------------
        # Do we apply the generic amplification factors?
        # ---------------------------------------------------------------------
        self.apply_gafs = self.config["modeling"]["apply_generic_amp_factors"]

        # ---------------------------------------------------------------------
        # Bias parameters
        # ---------------------------------------------------------------------
        self.do_bias = self.config["modeling"]["bias"]["do_bias"]
        self.bias_max_range = self.config["modeling"]["bias"]["max_range"]
        self.bias_max_mag = self.config["modeling"]["bias"]["max_mag"]
        self.bias_max_dsigma = self.config["modeling"]["bias"][
            "max_delta_sigma"
        ]

        # ---------------------------------------------------------------------
        # Outlier parameters
        # ---------------------------------------------------------------------
        self.do_outliers = self.config["data"]["outlier"]["do_outliers"]
        self.outlier_deviation_level = self.config["data"]["outlier"][
            "max_deviation"
        ]
        self.outlier_max_mag = self.config["data"]["outlier"]["max_mag"]
        self.outlier_valid_stations = self.config["data"]["outlier"][
            "valid_stations"
        ]

        # ---------------------------------------------------------------------
        # These are the IMTs we want to make
        # ---------------------------------------------------------------------
        self.imt_out_set = set(self.config["interp"]["imt_list"])

        # ---------------------------------------------------------------------
        # The x and y resolution of the output grid
        # ---------------------------------------------------------------------
        self.smdx = self.config["interp"]["prediction_location"]["xres"]
        self.smdy = self.config["interp"]["prediction_location"]["yres"]
        self.nmax = self.config["interp"]["prediction_location"]["nmax"]

        # ---------------------------------------------------------------------
        # Get the Vs30 file name
        # ---------------------------------------------------------------------
        self.vs30default = self.config["data"]["vs30default"]
        self.vs30_file = self.config["data"]["vs30file"]
        if not self.vs30_file:
            self.vs30_file = None
        self.mask_file = self.config["data"]["maskfile"]
        if not self.mask_file:
            self.mask_file = None

    def _set_output_params(self):
        """
        Set variables dealing with the output grid or points

        Returns:
            nothing
        """
        if self.use_simulations:
            self.do_grid = True
            imt_grp = self.sim_imt_paths[0]
            groups = imt_grp.split("/")
            myimt = groups[-1]
            del groups[-1]
            _, geodict = self.ic.getArray(groups, myimt)
            self.west = geodict["xmin"]
            self.east = geodict["xmax"]
            self.south = geodict["ymin"]
            self.north = geodict["ymax"]
            self.smdx = geodict["dx"]
            self.smdy = geodict["dy"]

            self.sites_obj_out = Sites.fromBounds(
                self.west,
                self.east,
                self.south,
                self.north,
                self.smdx,
                self.smdy,
                defaultVs30=self.vs30default,
                vs30File=self.vs30_file,
                padding=True,
                resample=True,
            )
            self.smnx, self.smny = self.sites_obj_out.getNxNy()
            self.sx_out = self.sites_obj_out.getSitesContext()
            lons, lats = np.meshgrid(self.sx_out.lons, self.sx_out.lats)
            # self.sx_out.lons = lons.copy()
            # self.sx_out.lats = lats.copy()
            self.lons = lons.flatten()
            self.lats = lats.flatten()
            self.depths = np.zeros_like(lats)
            dist_obj_out = Distance.fromSites(
                self.default_gmpe, self.sites_obj_out, self.rupture_obj
            )
        elif (
            self.config["interp"]["prediction_location"]["file"]
            and self.config["interp"]["prediction_location"]["file"] != "None"
        ):
            #
            # FILE: Open the file and get the output points
            # we've pre-processed this file to be a CSV with fixed columns
            #
            self.do_grid = False
            points_file = pathlib.Path(
                self.config["interp"]["prediction_location"]["file"]
            )
            dataframe = pd.read_csv(points_file, dtype={"id": str})
            self.lons = dataframe["lon"].to_numpy().reshape(1, -1)
            self.lats = dataframe["lat"].to_numpy().reshape(1, -1)
            self.idents = dataframe["id"].to_numpy()
            self.vs30 = dataframe["vs30"].to_numpy().reshape(1, -1)

            self.depths = np.zeros_like(self.lats)
            # self.west = thirty_sec_min(np.min(self.lons))
            # self.east = thirty_sec_max(np.max(self.lons))
            # self.south = thirty_sec_min(np.min(self.lats))
            # self.north = thirty_sec_max(np.max(self.lats))
            if self.config["interp"]["prediction_location"]["extent"]:
                self.west, self.south, self.east, self.north = self.config[
                    "interp"
                ]["prediction_location"]["extent"]
            else:
                self.west, self.east, self.south, self.north = get_extent(
                    config=self.config,
                    ipe=self.ipe_extent,
                    rupture=self.rupture_obj,
                )
            self.smnx = np.size(self.lons)
            self.smny = 1
            dist_obj_out = Distance(
                self.default_gmpe,
                self.lons,
                self.lats,
                self.depths,
                self.rupture_obj,
            )

            self.sites_obj_out = Sites.fromBounds(
                self.west,
                self.east,
                self.south,
                self.north,
                self.smdx,
                self.smdy,
                defaultVs30=self.vs30default,
                vs30File=self.vs30_file,
                padding=True,
                resample=True,
            )

            self.sx_out = self.sites_obj_out.getSitesContext(
                {"lats": self.lats, "lons": self.lons}
            )
            # Replace the Vs30 from the grid (or default) with the Vs30
            # provided with the site list.
            if np.any(self.vs30 > 0):
                self.sx_out.vs30 = self.vs30
                addDepthParameters(self.sx_out)
        else:
            #
            # GRID: Figure out the grid parameters and get output points
            #
            self.do_grid = True

            if self.config["interp"]["prediction_location"]["extent"]:
                self.west, self.south, self.east, self.north = self.config[
                    "interp"
                ]["prediction_location"]["extent"]
            else:
                self.west, self.east, self.south, self.north = get_extent(
                    config=self.config,
                    ipe=self.ipe_extent,
                    rupture=self.rupture_obj,
                )

            # Adjust resolution to be under nmax
            self._adjust_resolution()

            self.sites_obj_out = Sites.fromBounds(
                self.west,
                self.east,
                self.south,
                self.north,
                self.smdx,
                self.smdy,
                defaultVs30=self.vs30default,
                vs30File=self.vs30_file,
                padding=True,
                resample=True,
            )
            self.smnx, self.smny = self.sites_obj_out.getNxNy()
            self.sx_out = self.sites_obj_out.getSitesContext()
            lons, lats = np.meshgrid(self.sx_out.lons, self.sx_out.lats)
            # self.sx_out.lons = lons.copy()
            # self.sx_out.lats = lats.copy()
            self.lons = lons.flatten()
            self.lats = lats.flatten()
            self.depths = np.zeros_like(lats)
            dist_obj_out = Distance.fromSites(
                self.default_gmpe, self.sites_obj_out, self.rupture_obj
            )

        #
        # TODO: This will break if the IPE needs distance measures
        # that the GMPE doesn't; should make this a union of the
        # requirements of both
        #
        self.dx_out = dist_obj_out.getDistanceContext()
        #
        # Set up the sites and distance contexts for the attenuation curves
        #
        self.atten_sx_rock = self.sites_obj_out.getSitesContext(
            self.atten_coords, rock_vs30=self.rock_vs30
        )
        self.atten_sx_soil = self.sites_obj_out.getSitesContext(
            self.atten_coords, rock_vs30=self.soil_vs30
        )
        self.atten_dx = Distance(
            self.default_gmpe,
            self.atten_coords["lons"],
            self.atten_coords["lats"],
            np.zeros_like(self.atten_coords["lons"]),
            rupture=self.point_source,
        ).getDistanceContext()

        self.lons_out_rad = np.radians(self.lons).flatten()
        self.lats_out_rad = np.radians(self.lats).flatten()
        self.flip_lons = False
        if self.east < 0 < self.west:
            self.flip_lons = True
            self.lons_out_rad[self.lons_out_rad < 0] += 2 * np.pi

    def _set_data_frames(self):
        """
        Extract the StationList object from the input container and
        fill the DataFrame class and keep a list of dataframes.

            - df1 holds the instrumented data (PGA, PGV, SA)
            - df2 holds the non-instrumented data (MMI)
        """
        self.dataframes = []
        try:
            self.stations = self.ic.getStationList()
        except AttributeError:
            return
        if self.stations is None:
            return
        component = self.config["interp"]["component"]
        for dfid, val, comp in (
            ("df1", True, component),
            ("df2", False, "GREATER_OF_TWO_HORIZONTAL"),
        ):
            if dfid == "df1" and self.no_seismic:
                continue
            if dfid == "df2" and self.no_macroseismic:
                continue
            sdf, imts = self.stations.getStationDictionary(
                instrumented=val,
                min_nresp=self.config["data"]["min_nresp"],
                component=comp,
            )
            if sdf is not None:
                df = DataFrame()
                df.df = sdf
                setattr(self, dfid, df)
                self.dataframes.append(dfid)
                df.imts = imts

        # Flag the stations in the bad stations list from the config
        df1 = getattr(self, "df1", None)
        if df1 is None:
            return
        evdt = date(
            self.origin.time.year,
            self.origin.time.month,
            self.origin.time.day,
        )
        nostart = date(1970, 1, 1)
        df1.df["flagged"] = np.full_like(df1.df["lon"], 0, dtype=bool)
        if "bad_stations" not in self.config["data"]:
            return
        for sid, dates in self.config["data"]["bad_stations"].items():
            ondate, offdate = dates.split(":")
            year, month, day = map(int, ondate.split("-"))
            ondt = date(year, month, day)
            if offdate:
                year, month, day = map(int, offdate.split("-"))
                offdt = date(year, month, day)
            else:
                offdt = None
            bad = False
            if (ondt == nostart or ondt <= evdt) and (
                offdt is None or offdt >= evdt
            ):
                bad = True
            if bad:
                df1.df["flagged"] |= df1.df["id"] == sid

    def _populate_data_frames(self):
        """
        Make the sites and distance contexts for each dataframe then
        compute the predictions for the IMTs in that dataframe.
        """
        for dfid in self.dataframes:
            dfn = getattr(self, dfid)
            df = dfn.df
            # -----------------------------------------------------------------
            # Get the sites and distance contexts
            # -----------------------------------------------------------------
            df["depth"] = np.zeros_like(df["lon"])
            lldict = {"lons": df["lon"], "lats": df["lat"]}
            dfn.sx = self.sites_obj_out.getSitesContext(lldict)
            dfn.sx_rock = copy.deepcopy(dfn.sx)
            dfn.sx_rock.vs30 = np.full_like(dfn.sx.vs30, self.rock_vs30)
            dfn.sx_soil = copy.deepcopy(dfn.sx)
            dfn.sx_soil.vs30 = np.full_like(dfn.sx.vs30, self.soil_vs30)
            dist_obj = Distance(
                self.default_gmpe,
                df["lon"],
                df["lat"],
                df["depth"],
                self.rupture_obj,
            )
            dfn.dx = dist_obj.getDistanceContext()

            # -----------------------------------------------------------------
            # Are we doing directivity?
            # -----------------------------------------------------------------
            if self.do_directivity is True:
                self.logger.info("Directivity for %d...", dfid)
                dir_df = Rowshandel2013(
                    self.origin,
                    self.rupture_obj,
                    df["lat"].reshape((1, -1)),
                    df["lon"].reshape((1, -1)),
                    df["depth"].reshape((1, -1)),
                    dx=1.0,
                    T=Rowshandel2013.getPeriods(),
                    a_weight=0.5,
                    mtype=1,
                )
                self.dir_results.append((dir_df, dfn.dx))

            # -----------------------------------------------------------------
            # Do the predictions and other bookkeeping for each IMT
            # We only need predictions for output IMTs
            # -----------------------------------------------------------------
            pdict = self.get_point_amps(
                dfn, self.gmpe_dict, list(self.oqimt_dict.values())
            )

            # for imtstr in self.imt_out_set:
            for oqimt, pval in pdict.items():
                imtstr = str(oqimt)
                # oqimt = self.oqimt_dict[imtstr]
                pmean = pval["site"]["mean"]
                pstddev = [
                    pval["site"][oqconst.StdDev.TOTAL],
                ]
                if oqconst.StdDev.INTER_EVENT in pval["site"]:
                    pstddev.append(pval["site"][oqconst.StdDev.INTER_EVENT])
                    pstddev.append(pval["site"][oqconst.StdDev.INTRA_EVENT])
                pmean_rock = pval["rock"]["mean"]
                pstddev_rock = [pval["rock"][oqconst.StdDev.TOTAL]]
                pmean_soil = pval["soil"]["mean"]
                pstddev_soil = [pval["soil"][oqconst.StdDev.TOTAL]]

                df[imtstr + "_pred"] = pmean
                df[imtstr + "_pred_sigma"] = pstddev[0]
                df[imtstr + "_pred_rock"] = pmean_rock
                df[imtstr + "_pred_sigma_rock"] = pstddev_rock[0]
                df[imtstr + "_pred_soil"] = pmean_soil
                df[imtstr + "_pred_sigma_soil"] = pstddev_soil[0]

                if imtstr != "MMI":
                    total_only = self.gmpe_total_sd_only
                    tau_guess = SM_CONSTS["default_stddev_inter"]
                else:
                    total_only = self.ipe_total_sd_only
                    tau_guess = SM_CONSTS["default_stddev_inter_mmi"]
                if total_only:
                    df[imtstr + "_pred_tau"] = tau_guess * pstddev[0]
                    df[imtstr + "_pred_phi"] = np.sqrt(
                        pstddev[0] ** 2 - df[imtstr + "_pred_tau"] ** 2
                    )
                else:
                    df[imtstr + "_pred_tau"] = pstddev[1]
                    df[imtstr + "_pred_phi"] = pstddev[2]
                #
                # If we're just computing the predictions of an output
                # IMT, then we can skip the residual and outlier stuff
                #
                if imtstr not in df:
                    continue
                #
                # Compute the total residual
                #
                df[imtstr + "_residual"] = df[imtstr] - df[imtstr + "_pred"]
                # -------------------------------------------------------------
                # Do the outlier flagging if we have a fault, or we don't
                # have a fault but the event magnitude is under the limit
                # -------------------------------------------------------------
                if self.do_outliers and (
                    not isinstance(self.rupture_obj, PointRupture)
                    or self.rx.mag <= self.outlier_max_mag
                ):
                    #
                    # Make a boolean array of stations that have been
                    # manually rehabilitated by the operator
                    #
                    is_valid = np.full(np.shape(df["id"]), False, dtype=bool)
                    for valid in self.outlier_valid_stations:
                        is_valid |= valid == df["id"]
                    #
                    # turn off nan warnings for this statement
                    #
                    np.seterr(invalid="ignore")
                    flagged = (
                        np.abs(df[imtstr + "_residual"])
                        > self.outlier_deviation_level
                        * df[imtstr + "_pred_sigma"]
                    ) & (~is_valid)
                    np.seterr(invalid="warn")
                    #
                    # Add NaN values to the list of outliers
                    #
                    flagged |= np.isnan(df[imtstr + "_residual"])

                    self.logger.debug(
                        "IMT: %s, flagged: %d", imtstr, np.sum(flagged)
                    )
                    df[imtstr + "_outliers"] = flagged
                else:
                    #
                    # Not doing outliers, but should still flag NaNs
                    #
                    flagged = np.isnan(df[imtstr + "_residual"])
                    df[imtstr + "_outliers"] = flagged
                #
                # If uncertainty hasn't been set for MMI, give it
                # the default value
                #
                if imtstr == "MMI" and all(df["MMI_sd"] == 0):
                    df["MMI_sd"][:] = self.config["data"]["default_mmi_stddev"]
            #
            # Get the lons/lats in radians while we're at it
            #
            df["lon_rad"] = np.radians(df["lon"])
            df["lat_rad"] = np.radians(df["lat"])
            if self.flip_lons:
                df["lon_rad"][df["lon_rad"] < 0] += 2 * np.pi
            #
            # It will be handy later on to have the rupture distance
            # in the dataframes
            #
            if isinstance(self.rupture_obj, PointRupture):
                dd = get_distance(
                    ["rhypo"],
                    df["lat"],
                    df["lon"],
                    df["depth"],
                    self.rupture_obj,
                )
                df["rrup"] = dd["rhypo"]
            else:
                dd = get_distance(
                    ["rrup"],
                    df["lat"],
                    df["lon"],
                    df["depth"],
                    self.rupture_obj,
                )
                df["rrup"] = dd["rrup"]

    def get_point_amps(self, dfn, gmpedict, oqimtlist):
        """
        Get predictions for site, rock, and soil for a set of locations for a
        list of IMTs.
        """
        pdict = {}
        if isinstance(self.rupture_obj, PointRupture):
            ffs = FFSimmer(self.rff, measure="mean")
            pdict = ffs.compute_points(dfn.sx, gmpedict, oqimtlist)
            immi = imt.from_string("MMI")
            pffs = ffs.compute_points(dfn.sx, {immi: self.ipe}, [immi])
            pdict[immi] = pffs[immi]
        else:
            for oqimt in oqimtlist:
                pmean, pstddev = self._gmas(
                    gmpedict[oqimt], dfn.sx, dfn.dx, oqimt, self.apply_gafs
                )
                pmean_rock, pstddev_rock = self._gmas(
                    gmpedict[oqimt],
                    dfn.sx_rock,
                    dfn.dx,
                    oqimt,
                    self.apply_gafs,
                )
                pmean_soil, pstddev_soil = self._gmas(
                    gmpedict[oqimt],
                    dfn.sx_soil,
                    dfn.dx,
                    oqimt,
                    self.apply_gafs,
                )
                pdict[oqimt] = {
                    "site": {
                        "mean": pmean,
                        oqconst.StdDev.TOTAL: pstddev[0],
                    },
                    "rock": {
                        "mean": pmean_rock,
                        oqconst.StdDev.TOTAL: pstddev_rock[0],
                    },
                    "soil": {
                        "mean": pmean_soil,
                        oqconst.StdDev.TOTAL: pstddev_soil[0],
                    },
                }
                if len(pstddev) > 1:
                    pdict[oqimt]["site"][oqconst.StdDev.INTER_EVENT] = pstddev[
                        1
                    ]
                    pdict[oqimt]["site"][oqconst.StdDev.INTRA_EVENT] = pstddev[
                        2
                    ]
                    pdict[oqimt]["rock"][oqconst.StdDev.INTER_EVENT] = (
                        pstddev_rock[1]
                    )
                    pdict[oqimt]["rock"][oqconst.StdDev.INTRA_EVENT] = (
                        pstddev_rock[2]
                    )
                    pdict[oqimt]["soil"][oqconst.StdDev.INTER_EVENT] = (
                        pstddev_soil[1]
                    )
                    pdict[oqimt]["soil"][oqconst.StdDev.INTRA_EVENT] = (
                        pstddev_soil[2]
                    )

            immi = imt.from_string("MMI")
            pmean, pstddev = self._gmas(
                self.ipe, dfn.sx, dfn.dx, immi, self.apply_gafs
            )
            pmean_rock, pstddev_rock = self._gmas(
                self.ipe, dfn.sx_rock, dfn.dx, immi, self.apply_gafs
            )
            pmean_soil, pstddev_soil = self._gmas(
                self.ipe, dfn.sx_soil, dfn.dx, immi, self.apply_gafs
            )
            pdict[immi] = {
                "site": {
                    "mean": pmean,
                    oqconst.StdDev.TOTAL: pstddev[0],
                },
                "rock": {
                    "mean": pmean_rock,
                    oqconst.StdDev.TOTAL: pstddev_rock[0],
                },
                "soil": {
                    "mean": pmean_soil,
                    oqconst.StdDev.TOTAL: pstddev_soil[0],
                },
            }
            if len(pstddev) > 1:
                pdict[immi]["site"][oqconst.StdDev.INTER_EVENT] = pstddev[1]
                pdict[immi]["site"][oqconst.StdDev.INTRA_EVENT] = pstddev[2]
                pdict[immi]["rock"][oqconst.StdDev.INTER_EVENT] = pstddev_rock[
                    1
                ]
                pdict[immi]["rock"][oqconst.StdDev.INTRA_EVENT] = pstddev_rock[
                    2
                ]
                pdict[immi]["soil"][oqconst.StdDev.INTER_EVENT] = pstddev_soil[
                    1
                ]
                pdict[immi]["soil"][oqconst.StdDev.INTRA_EVENT] = pstddev_soil[
                    2
                ]
        return pdict

    def _derive_imts_from_mmi(self):
        """
        Compute all the IMTs possible from MMI
        TODO: This logic needs to be revisited. We should probably make what
        we have to to do the CMS to make the needed output IMTs, but
        for now, we're just going to use what we have and the ccf.
        """
        if "df2" not in self.dataframes:
            return

        this_df = getattr(self, "df2")
        df2 = this_df.df
        imtlist = []
        gmpedict = {}
        gmice_imts = [
            imt.__name__
            for imt in self.gmice.DEFINED_FOR_INTENSITY_MEASURE_TYPES
        ]
        for gmice_imt in gmice_imts:
            if "SA" in gmice_imt:
                iterlist = self.gmice.DEFINED_FOR_SA_PERIODS
            else:
                iterlist = [None]
            for period in iterlist:
                if period:
                    oqimt = SA(period)
                else:
                    oqimt = imt.from_string(gmice_imt)
                imtstr = str(oqimt)
                np.seterr(invalid="ignore")
                df2[imtstr], _ = self.gmice.getGMfromMI(
                    df2["MMI"], oqimt, dists=df2["rrup"], mag=self.rx.mag
                )
                df2[imtstr][
                    df2["MMI"] < self.config["data"]["min_mmi_convert"]
                ] = np.nan
                np.seterr(invalid="warn")
                df2[imtstr + "_sd"] = np.full_like(
                    df2["MMI"], self.gmice.getMI2GMsd()[oqimt]
                )
                this_df.imts.add(imtstr)
                if imtstr not in self.imt_out_set:
                    continue
                imtlist.append(oqimt)
                gmpedict[oqimt] = self.gmpe_dict[oqimt]

        pdict = self.get_point_amps(this_df, gmpedict, imtlist)
        for oqimt in imtlist:
            imtstr = str(oqimt)
            pmean = pdict[oqimt]["site"]["mean"]
            pstddev = [
                pdict[oqimt]["site"][oqconst.StdDev.TOTAL],
            ]
            if oqconst.StdDev.INTER_EVENT in pdict[oqimt]["site"]:
                pstddev.append(
                    pdict[oqimt]["site"][oqconst.StdDev.INTER_EVENT]
                )
                pstddev.append(
                    pdict[oqimt]["site"][oqconst.StdDev.INTRA_EVENT]
                )
            pmean_rock = pdict[oqimt]["rock"]["mean"]
            pstddev_rock = [pdict[oqimt]["rock"][oqconst.StdDev.TOTAL]]
            pmean_soil = pdict[oqimt]["soil"]["mean"]
            pstddev_soil = [pdict[oqimt]["soil"][oqconst.StdDev.TOTAL]]
            df2[imtstr + "_pred"] = pmean
            df2[imtstr + "_pred_sigma"] = pstddev[0]
            df2[imtstr + "_pred_rock"] = pmean_rock
            df2[imtstr + "_pred_sigma_rock"] = pstddev_rock[0]
            df2[imtstr + "_pred_soil"] = pmean_soil
            df2[imtstr + "_pred_sigma_soil"] = pstddev_soil[0]
            if imtstr != "MMI":
                total_only = self.gmpe_total_sd_only
                tau_guess = SM_CONSTS["default_stddev_inter"]
            else:
                total_only = self.ipe_total_sd_only
                tau_guess = SM_CONSTS["default_stddev_inter_mmi"]
            if total_only:
                df2[imtstr + "_pred_tau"] = tau_guess * pstddev[0]
                df2[imtstr + "_pred_phi"] = np.sqrt(
                    pstddev[0] ** 2 - df2[imtstr + "_pred_tau"] ** 2
                )
            else:
                df2[imtstr + "_pred_tau"] = pstddev[1]
                df2[imtstr + "_pred_phi"] = pstddev[2]
            df2[imtstr + "_residual"] = df2[imtstr] - pmean
            df2[imtstr + "_outliers"] = np.isnan(df2[imtstr + "_residual"])
            df2[imtstr + "_outliers"] |= df2["MMI_outliers"]

    def _derive_mmi_from_imts(self):
        """
        Make derived MMI from each of the IMTs in the input (for
        which the GMICE is defined; then select the best MMI for
        each station based on a list of "preferred" IMTs; also
        calculate the predicted MMI and the residual.
        """
        if "df1" not in self.dataframes:
            return
        this_df = getattr(self, "df1")
        df1 = this_df.df
        gmice_imts = [
            imt.__name__
            for imt in self.gmice.DEFINED_FOR_INTENSITY_MEASURE_TYPES
        ]
        gmice_pers = self.gmice.DEFINED_FOR_SA_PERIODS
        np.seterr(invalid="ignore")
        df1["MMI"] = self.gmice.getPreferredMI(
            df1, dists=df1["rrup"], mag=self.rx.mag
        )
        np.seterr(invalid="warn")
        mmi_sd = self.gmice.getPreferredSD()
        if mmi_sd is not None:
            df1["MMI_sd"] = np.full_like(df1["lon"], mmi_sd)
        for imtstr in this_df.imts:
            if not (
                imtstr in gmice_imts
                or (imtstr.startswith("SA") and "SA" in gmice_imts)
            ):
                continue
            oqimt = imt.from_string(imtstr)
            if "SA" in imtstr and oqimt.period not in gmice_pers:
                continue

            np.seterr(invalid="ignore")
            df1["derived_MMI_from_" + imtstr], _ = self.gmice.getMIfromGM(
                df1[imtstr], oqimt, dists=df1["rrup"], mag=self.rx.mag
            )
            np.seterr(invalid="warn")
            df1["derived_MMI_from_" + imtstr + "_sd"] = np.full_like(
                df1[imtstr], self.gmice.getGM2MIsd()[oqimt]
            )

        preferred_imts = ["PGV", "PGA", "SA(1.0)", "SA(0.3)", "SA(3.0)"]
        if df1["MMI"] is None:
            df1["MMI"] = np.full_like(df1["lon"], np.nan)
            df1["MMI_sd"] = np.full_like(df1["lon"], np.nan)
        df1["MMI_outliers"] = np.full_like(df1["lon"], True, dtype=bool)
        for imtstr in preferred_imts:
            if "derived_MMI_from_" + imtstr in df1:
                ixx = (np.isnan(df1["MMI"]) | df1["MMI_outliers"]) & ~(
                    np.isnan(df1["derived_MMI_from_" + imtstr])
                    | df1[imtstr + "_outliers"]
                )
                df1["MMI"][ixx] = df1["derived_MMI_from_" + imtstr][ixx]
                df1["MMI_sd"][ixx] = df1["derived_MMI_from_" + imtstr + "_sd"][
                    ixx
                ]
                df1["MMI_outliers"][ixx] = False
        this_df.imts.add("MMI")
        #
        # Get the prediction and stddevs
        #
        immi = imt.from_string("MMI")
        pdict = self.get_point_amps(this_df, {immi: self.ipe}, [immi])

        pmean = pdict[immi]["site"]["mean"]
        pstddev = [
            pdict[immi]["site"][oqconst.StdDev.TOTAL],
        ]
        if oqconst.StdDev.INTER_EVENT in pdict[immi]["site"]:
            pstddev.append(pdict[immi]["site"][oqconst.StdDev.INTER_EVENT])
            pstddev.append(pdict[immi]["site"][oqconst.StdDev.INTRA_EVENT])
        pmean_rock = pdict[immi]["rock"]["mean"]
        pstddev_rock = [pdict[immi]["rock"][oqconst.StdDev.TOTAL]]
        pmean_soil = pdict[immi]["soil"]["mean"]
        pstddev_soil = [pdict[immi]["soil"][oqconst.StdDev.TOTAL]]

        df1["MMI" + "_pred"] = pmean
        df1["MMI" + "_pred_sigma"] = pstddev[0]
        df1["MMI" + "_pred_rock"] = pmean_rock
        df1["MMI" + "_pred_sigma_rock"] = pstddev_rock[0]
        df1["MMI" + "_pred_soil"] = pmean_soil
        df1["MMI" + "_pred_sigma_soil"] = pstddev_soil[0]
        if self.ipe_total_sd_only:
            tau_guess = SM_CONSTS["default_stddev_inter_mmi"]
            df1["MMI" + "_pred_tau"] = tau_guess * pstddev[0]
            df1["MMI" + "_pred_phi"] = np.sqrt(
                pstddev[0] ** 2 - df1["MMI" + "_pred_tau"] ** 2
            )
        else:
            df1["MMI" + "_pred_tau"] = pstddev[1]
            df1["MMI" + "_pred_phi"] = pstddev[2]
        df1["MMI" + "_residual"] = df1["MMI"] - pmean
        df1["MMI" + "_outliers"] |= np.isnan(df1["MMI" + "_residual"])

    def _fill_data_arrays(self):
        """
        For each IMT get lists of the amplitudes that can contribute
        to the bias and the interpolation. Keep lists of IMT, period
        index, lons, lats, residuals, tau, phi, additional uncertainty,
        and rupture distance.
        """
        imtsets = {}
        sasets = {}
        for ndf in ("df1", "df2"):
            df = getattr(self, ndf, None)
            if df is None:
                continue
            imtsets[ndf], sasets[ndf] = _get_imt_lists(df)

        for imtstr in self.full_out_set:
            #
            # Fill the station arrays; here we use lists and append to
            # them because it is much faster than appending to a numpy
            # array; after the loop, the lists are converted to numpy
            # arrays:
            #
            lons_rad = []  # longitude (in radians) of the input station
            lats_rad = []  # latitude (in radians) of the input station
            resids = []  # The residual of the input IMT
            tau = []  # The between-event stddev of the input IMT
            phi = []  # The within-event stddev of the input IMT
            sig_extra = []  # Additional stddev of the input IMT
            rrups = []  # The rupture distance of the input station
            per_ix = []
            for ndf in ("df1", "df2"):
                tdf = getattr(self, ndf, None)
                if tdf is None:
                    continue
                sdf = tdf.df
                for i in range(np.size(sdf["lon"])):
                    #
                    # Each station can provide 0, 1, or 2 IMTs:
                    #
                    for imtin in _get_nearest_imts(
                        imtstr, imtsets[ndf][i], sasets[ndf][i]
                    ):
                        per_ix.append(self.imt_per_ix[imtin])
                        lons_rad.append(sdf["lon_rad"][i])
                        lats_rad.append(sdf["lat_rad"][i])
                        resids.append(sdf[imtin + "_residual"][i])
                        tau.append(sdf[imtin + "_pred_tau"][i])
                        phi.append(sdf[imtin + "_pred_phi"][i])
                        sig_extra.append(sdf[imtin + "_sd"][i])
                        rrups.append(sdf["rrup"][i])

            self.sta_per_ix[imtstr] = np.array(per_ix)
            self.sta_lons_rad[imtstr] = np.array(lons_rad)
            self.sta_lats_rad[imtstr] = np.array(lats_rad)
            if self.flip_lons:
                self.sta_lons_rad[imtstr][self.sta_lons_rad[imtstr] < 0] += (
                    2 * np.pi
                )
            self.sta_resids[imtstr] = np.array(resids).reshape((-1, 1))
            self.sta_tau[imtstr] = np.array(tau).reshape((-1, 1))
            self.sta_phi[imtstr] = np.array(phi).reshape((-1, 1))
            self.sta_sig_extra[imtstr] = np.array(sig_extra)
            self.sta_rrups[imtstr] = np.array(rrups)

    def _compute_bias(self):
        """
        Compute a bias for all of the IMTs in the outputs
        """
        for imtstr in self.full_out_set:
            #
            # Get the index of the (pseudo-) period of the output IMT
            #
            outperiod_ix = self.imt_per_ix[imtstr]
            #
            # Get the data and distance-limited residuals for computing
            # the bias
            #
            sta_per_ix = self.sta_per_ix[imtstr]
            sta_lons_rad = self.sta_lons_rad[imtstr]
            sta_lats_rad = self.sta_lats_rad[imtstr]
            sta_tau = self.sta_tau[imtstr]
            sta_phi = self.sta_phi[imtstr]
            sta_sig_extra = self.sta_sig_extra[imtstr]

            dix = self.sta_rrups[imtstr] > self.bias_max_range
            sta_resids_dl = self.sta_resids[imtstr].copy()
            if len(dix) > 0:
                sta_resids_dl[dix] = 0.0
            #
            # If there are no stations, bail out
            #
            nsta = np.size(sta_lons_rad)
            if nsta == 0:
                self.mu_h_yd[imtstr] = 0.0
                self.cov_hh_yd[imtstr] = 0.0
                self.nominal_bias[imtstr] = 0.0
                nom_variance = 0.0
                #
                # Write the nominal values of the bias and its stddev to log
                #
                self.logger.debug(
                    "%s: nom bias %f nom stddev %f; %d stations",
                    imtstr,
                    self.nominal_bias[imtstr],
                    np.sqrt(nom_variance),
                    nsta,
                )
                continue
            #
            # Set up the IMT indices
            #
            imt_types = np.sort(np.unique(sta_per_ix))
            len_types = len(imt_types)
            self.imt_types[imtstr] = imt_types
            self.len_types[imtstr] = len_types
            sa_inds = {}
            for i in range(len_types):
                sa_inds[imt_types[i]] = np.where(sta_per_ix == imt_types[i])[0]

            if outperiod_ix not in imt_types:
                self.no_native_flag[imtstr] = True
                imt_types_alt = np.sort(
                    np.concatenate([imt_types, np.array([outperiod_ix])])
                )
                self.imt_y_ind[imtstr] = np.where(
                    outperiod_ix == imt_types_alt
                )[0][0]
            else:
                self.no_native_flag[imtstr] = False
            #
            # Build t_d and corr_hh_d
            #
            if self.no_native_flag[imtstr] is False:
                t_d = np.zeros((nsta, len_types))
                for i in range(len_types):
                    t_d[sa_inds[imt_types[i]], i] = sta_tau[
                        sa_inds[imt_types[i]], 0
                    ]
                corr_hh_d = np.zeros((len_types, len_types))
                ones = np.ones(len_types, dtype=np.int_).reshape((-1, 1))
                t1 = imt_types.reshape((1, -1)) * ones
                t2 = imt_types.reshape((-1, 1)) * ones.T
                self.ccf.getCorrelation(t1, t2, corr_hh_d)
            else:
                t_d = np.zeros((nsta, len_types + 1))
                for i in range(len_types + 1):
                    if i == self.imt_y_ind[imtstr]:
                        continue
                    if i < self.imt_y_ind[imtstr]:
                        t_d[sa_inds[imt_types[i]], i] = sta_tau[
                            sa_inds[imt_types[i]], 0
                        ]
                    else:
                        t_d[sa_inds[imt_types[i - 1]], i] = sta_tau[
                            sa_inds[imt_types[i - 1]], 0
                        ]
                corr_hh_d = np.zeros((len_types + 1, len_types + 1))
                ones = np.ones(len_types + 1, dtype=np.int_).reshape((-1, 1))
                t1 = imt_types_alt.reshape((1, -1)) * ones
                t2 = imt_types_alt.reshape((-1, 1)) * ones.T
                self.ccf.getCorrelation(t1, t2, corr_hh_d)
            #
            # Make cov_wd_wd_inv (Sigma_22_inv)
            #
            matrix22 = np.empty((nsta, nsta), dtype=np.double)
            geodetic_distance_fast(
                sta_lons_rad,
                sta_lats_rad,
                sta_lons_rad,
                sta_lats_rad,
                matrix22,
            )
            ones = np.ones(nsta, dtype=np.int_).reshape((-1, 1))
            t1_22 = sta_per_ix.reshape((1, -1)) * ones
            t2_22 = sta_per_ix.reshape((-1, 1)) * ones.T
            self.ccf.getCorrelation(t1_22, t2_22, matrix22)
            sta_phi_flat = sta_phi.flatten()
            make_sigma_matrix(matrix22, sta_phi_flat, sta_phi_flat)
            np.fill_diagonal(matrix22, np.diag(matrix22) + sta_sig_extra**2)
            cov_wd_wd_inv = np.linalg.pinv(matrix22)
            #
            # Hold on to some things we'll need later
            #
            self.t_d[imtstr] = t_d
            self.cov_wd_wd_inv[imtstr] = cov_wd_wd_inv
            #
            # Compute the bias mu_h_yd and cov_hh_yd pieces
            #
            cov_hh_yd = np.linalg.pinv(
                np.linalg.multi_dot([t_d.T, cov_wd_wd_inv, t_d])
                + np.linalg.pinv(corr_hh_d)
            )
            mu_h_yd = np.linalg.multi_dot(
                [cov_hh_yd, t_d.T, cov_wd_wd_inv, sta_resids_dl]
            )
            if self.do_bias and (
                not isinstance(self.rupture_obj, PointRupture)
                or self.rx.mag <= self.bias_max_mag
            ):
                self.mu_h_yd[imtstr] = mu_h_yd
            else:
                self.mu_h_yd[imtstr] = np.zeros_like(mu_h_yd)
            self.cov_hh_yd[imtstr] = cov_hh_yd
            #
            # Get the nominal bias and variance
            #
            delta_b_yd = t_d.dot(mu_h_yd)
            self.nominal_bias[imtstr] = np.mean(delta_b_yd)
            sig_b_yd = np.sqrt(
                np.diag(np.linalg.multi_dot([t_d, cov_hh_yd, t_d.T]))
            )
            nom_variance = np.mean(sig_b_yd)

            #
            # Write the nominal values of the bias and its stddev to log
            #
            self.logger.debug(
                "%s: nom bias %f nom stddev %f; %d stations",
                imtstr,
                self.nominal_bias[imtstr],
                np.sqrt(nom_variance),
                nsta,
            )

    def _compute_directivity_prediction_locations(self):
        """
        Figure out if we need the directivity factors, and if so, pre-calculate
        them. These will be used later in _compute_mvn.
        """
        if self.do_directivity is True:
            self.logger.info("Directivity for prediction locations...")

            # Precompute directivity at all periods
            dir_out = Rowshandel2013(
                self.origin,
                self.rupture_obj,
                self.lats.reshape((1, -1)),
                self.lons.reshape((1, -1)),
                np.zeros_like((len(self.lats), 1)),
                dx=1.0,
                T=Rowshandel2013.getPeriods(),
                a_weight=0.5,
                mtype=1,
            )
            self.dir_results.append((dir_out, self.dx_out))
            # Precompute directivity for the attenuation curves
            dir_out = Rowshandel2013(
                self.origin,
                self.rupture_obj,
                self.atten_coords["lats"].reshape((1, -1)),
                self.atten_coords["lons"].reshape((1, -1)),
                np.zeros_like((len(self.atten_coords["lats"]), 1)),
                dx=1.0,
                T=Rowshandel2013.getPeriods(),
                a_weight=0.5,
                mtype=1,
            )
            self.dir_results.append((dir_out, self.atten_dx))
        else:
            self.directivity = None

    def _compute_mvn(self, imtstr, ddict):
        """
        Do the MVN computations
        """
        self.logger.debug("compute_mvn: doing IMT %s", imtstr)
        #
        # Get the index of the (pesudo-) period of the output IMT
        #
        outperiod_ix = self.imt_per_ix[imtstr]
        #
        # Get the predictions at the output points
        #
        pout_mean = ddict["mean"]
        pout_sd = [
            ddict[oqconst.StdDev.TOTAL],
        ]
        if oqconst.StdDev.INTER_EVENT in ddict:
            pout_sd.append(ddict[oqconst.StdDev.INTER_EVENT])
            pout_sd.append(ddict[oqconst.StdDev.INTRA_EVENT])
        if not self.do_grid:
            self.pred_out[imtstr] = pout_mean
            self.pred_out_sd[imtstr] = pout_sd[0]

        if self.use_simulations:
            if imtstr == "MMI":
                pout_mean = self.gmice.getPreferredMI(
                    self.sim_df, dists=self.dx_out.rrup, mag=self.rx.mag
                )
            else:
                pout_mean = self.sim_df[imtstr]
        #
        # Get an array of the within-event standard deviations for the
        # output IMT at the output points
        #
        if imtstr != "MMI":
            total_only = self.gmpe_total_sd_only
            tau_guess = SM_CONSTS["default_stddev_inter"]
        else:
            total_only = self.ipe_total_sd_only
            tau_guess = SM_CONSTS["default_stddev_inter_mmi"]
        if total_only:
            self.tsd[imtstr] = tau_guess * pout_sd[0]
            self.psd[imtstr] = np.sqrt(pout_sd[0] ** 2 - self.tsd[imtstr] ** 2)
            self.psd_raw[imtstr] = np.sqrt(
                pout_sd[0] ** 2 - self.tsd[imtstr] ** 2
            )
        else:
            self.tsd[imtstr] = pout_sd[1]
            self.psd[imtstr] = pout_sd[2]
            self.psd_raw[imtstr] = pout_sd[2]
        #
        # If there are no data, just use the unbiased prediction
        # and the stddev
        #
        nsta = np.size(self.sta_lons_rad[imtstr])
        if nsta == 0:
            self.outgrid[imtstr] = pout_mean
            self.outsd[imtstr] = pout_sd[0]
            self.outphi[imtstr] = self.psd[imtstr]
            self.outtau[imtstr] = self.tsd[imtstr]
            # Special stuff for the IMT priors.
            self.rez_add_uncertainty[imtstr] = np.array([])
            self.rez_sigma_hh_yd[imtstr] = np.array([])
            self.rez_c[imtstr] = np.array([])
            self.rez_sta_per_ix[imtstr] = np.array([])
            return

        pout_sd2_phi = np.power(self.psd[imtstr], 2.0)

        sta_per_ix = self.sta_per_ix[imtstr]
        sta_phi = self.sta_phi[imtstr]
        sta_lons_rad = self.sta_lons_rad[imtstr]
        sta_lats_rad = self.sta_lats_rad[imtstr]

        len_output = np.size(self.tsd[imtstr])
        if self.no_native_flag[imtstr] is False:
            t_y0 = np.zeros((len_output, self.len_types[imtstr]))
            t_y0[:, np.where(outperiod_ix == self.imt_types[imtstr])[0][0]] = (
                self.tsd[imtstr].ravel()
            )
        else:
            t_y0 = np.zeros((len_output, self.len_types[imtstr] + 1))
            t_y0[:, self.imt_y_ind[imtstr]] = self.tsd[imtstr].ravel()

        t_d = self.t_d[imtstr]
        cov_wd_wd_inv = self.cov_wd_wd_inv[imtstr]
        #
        # Now do the MVN itself...
        #
        big_c = np.empty_like(t_y0[0 : self.smnx, :])
        c_tmp1 = np.empty_like(big_c)
        c_tmp2 = np.empty_like(big_c)
        s_tmp1 = np.empty((self.smnx), dtype=np.float64).reshape((-1, 1))
        s_tmp2 = np.empty((self.smnx), dtype=np.float64).reshape((-1, 1))
        s_tmp3 = np.empty((self.smnx), dtype=np.float64)
        ampgrid = np.zeros_like(pout_mean)
        cov_wy_wy_wd = np.zeros_like(pout_mean)
        sdgrid_tau = np.zeros_like(pout_mean)
        # Stuff that doesn't change within the loop:
        lons_out_rad = self.lons_out_rad
        lats_out_rad = self.lats_out_rad
        d12_cols = self.smnx
        ones = np.ones(d12_cols, dtype=np.int_).reshape((-1, 1))
        t1_12 = sta_per_ix.reshape((1, -1)) * ones
        t2_12 = np.full((d12_cols, nsta), outperiod_ix, dtype=np.int_)
        # sdsta is the standard deviation of the stations
        sdsta_phi = sta_phi.flatten()
        matrix12_phi = np.empty(t2_12.shape, dtype=np.double)
        rcmatrix_phi = np.empty(t2_12.shape, dtype=np.double)
        # Allocate the full big_c matrix only for the desired IMTs
        c_complete = np.empty_like(t_y0)
        for iy in range(self.smny):
            ss = iy * self.smnx
            se = (iy + 1) * self.smnx
            geodetic_distance_fast(
                sta_lons_rad,
                sta_lats_rad,
                lons_out_rad[ss:se],
                lats_out_rad[ss:se],
                matrix12_phi,
            )
            self.ccf.getCorrelation(t1_12, t2_12, matrix12_phi)
            # sdarr_phi is the standard deviation of the within-event
            # residuals at the output sites
            sdarr_phi = self.psd[imtstr][iy, :]
            make_sigma_matrix(matrix12_phi, sdsta_phi, sdarr_phi)
            #
            # Sigma12 * Sigma22^-1 is known as the 'regression
            # coefficient' matrix (rcmatrix)
            #
            np.dot(matrix12_phi, cov_wd_wd_inv, out=rcmatrix_phi)
            #
            # We only want the diagonal elements of the conditional
            # covariance matrix, so there is no point in doing the
            # full solution with the dot product, e.g.:
            # sdgrid[ss:se] = pout_sd2[ss:se] -
            #       np.diag(rcmatrix.dot(sigma21))
            #
            # make_sd_array is a Cython function that is optimized to find
            # the diagonal of the covariance matrix.
            #
            make_sd_array(
                cov_wy_wy_wd, pout_sd2_phi, iy, rcmatrix_phi, matrix12_phi
            )
            #
            # Equation B32 of Engler et al. (2021)
            #
            np.subtract(
                t_y0[ss:se, :],
                np.dot(rcmatrix_phi, t_d, out=c_tmp1),
                out=big_c,
            )
            #
            # This is the MVN solution for the conditional mean
            # It is an implementation of the equation just below
            # equation B25 in Engler et al. (2021):
            #
            # mu_Y_yD = mu_Y + big_c mu_h_yd + cov_WY_WD cov_WD_WD^-1 zeta
            #
            # but we break it up for efficiency.
            #
            s_tmp1r = np.dot(big_c, self.mu_h_yd[imtstr], out=s_tmp1).reshape(
                (-1,)
            )
            s_tmp2r = np.dot(
                rcmatrix_phi, self.sta_resids[imtstr], out=s_tmp2
            ).reshape((-1,))
            ampgrid[iy, :] = np.add(
                np.add(pout_mean[iy, :], s_tmp1r, out=s_tmp1r),
                s_tmp2r,
                out=s_tmp2r,
            )
            #
            # We're doing this:
            #
            # sdgrid_tau[iy, :] = np.diag(
            #     big_c.dot(self.cov_hh_yd[imtstr].dot(big_c.T)))
            #
            # to find the between-event part of the diagonal of the conditional
            # covariance.  This is the second term of equation B27 of Engler
            # et al. (2021). The code below is faster and uses less memory than
            # actually implementing the above equation.
            #
            np.dot(big_c, self.cov_hh_yd[imtstr], c_tmp1)
            sdgrid_tau[iy, :] = np.sum(
                np.multiply(c_tmp1, big_c, out=c_tmp2), out=s_tmp3, axis=1
            )
            # Save big_c to complete full size big_c
            c_complete[ss:se, :] = big_c

        #
        # This processing can result in MMI values that go beyond
        # the 1 to 10 bounds of MMI, so we apply that constraint again
        # here
        #
        if imtstr == "MMI":
            ampgrid = np.clip(ampgrid, 1.0, 10.0)
        #
        # The conditional mean
        #
        self.outgrid[imtstr] = ampgrid
        #
        # The outputs are the conditional total stddev, the conditional
        # between-event stddev (tau), and the prior within-event stddev (phi)
        #
        self.outsd[imtstr] = np.sqrt(
            np.add(cov_wy_wy_wd, sdgrid_tau, out=cov_wy_wy_wd),
            out=cov_wy_wy_wd,
        )
        # self.outphi[imtstr] = np.sqrt(cov_wy_wy_wd)
        self.outphi[imtstr] = self.psd[imtstr]
        self.outtau[imtstr] = np.sqrt(sdgrid_tau, out=sdgrid_tau)

        # Special stuff for the IMT priors.
        self.rez_add_uncertainty[imtstr] = self.sta_sig_extra[imtstr]
        self.rez_sigma_hh_yd[imtstr] = self.cov_hh_yd[imtstr]
        self.rez_c[imtstr] = c_complete
        self.rez_sta_per_ix[imtstr] = sta_per_ix

    def _apply_custom_mask(self):
        """Apply custom masks to IMT grid outputs."""
        if self.mask_file:
            mask = self._get_mask(self.mask_file)
            for grid in self.outgrid.values():
                grid[~mask] = np.nan

    def _get_land_mask(self):
        """
        Get the landmask for this map. Land will be False, water will
        be True (because of the way masked arrays work).
        """
        if "CALLED_FROM_PYTEST" in os.environ:
            oceans = None
        else:
            oceans = shpreader.natural_earth(
                category="physical", name="ocean", resolution="10m"
            )
        return self._get_mask(oceans)

    def _get_mask(self, vector=None):
        """
        Get a masked array for this map corresponding to the given vector
        feature.
        """
        if not self.do_grid:
            return np.array([])
        gd = GeoDict.createDictFromBox(
            self.west, self.east, self.south, self.north, self.smdx, self.smdy
        )
        bbox = (gd.xmin, gd.ymin, gd.xmax, gd.ymax)
        if vector is None:
            return np.zeros((gd.ny, gd.nx), dtype=bool)

        with fiona.open(vector) as c:
            tshapes = list(c.items(bbox=bbox))
            shapes = []
            for tshp in tshapes:
                shapes.append(shape(tshp[1]["geometry"]))
            if len(shapes) > 0:
                grid = Grid2D.rasterizeFromGeometry(shapes, gd, fillValue=0.0)
                return grid.getData().astype(bool)
            else:
                return np.zeros((gd.ny, gd.nx), dtype=bool)

    def _get_masked_grids(self, bmask):
        """
        For each grid in the output, generate a grid with the water areas
        masked out.
        """
        moutgrid = {}
        if not self.do_grid:
            for imtout in self.full_out_set:
                moutgrid[imtout] = self.outgrid[imtout]
            return moutgrid
        for imtout in self.full_out_set:
            moutgrid[imtout] = ma.masked_array(
                self.outgrid[imtout], mask=bmask
            )
        return moutgrid

    def _get_info(self, moutgrid):
        """
        Create an info dictionary that can be made into the info.json file.
        """
        #
        # Get the map grade
        #
        mean_rat, mygrade = _get_map_grade(
            self.do_grid, self.outsd, self.psd_raw, moutgrid
        )
        # ---------------------------------------------------------------------
        # This is the metadata for creating info.json
        # ---------------------------------------------------------------------
        st = "strec"
        ip = "input"
        ei = "event_information"
        op = "output"
        gm = "ground_motions"
        mi = "map_information"
        un = "uncertainty"
        pp = "processing"
        gmm = "ground_motion_modules"
        ms = "miscellaneous"
        mf = "model_flags"
        sv = "shakemap_versions"
        sr = "site_response"
        info = self.info
        info[ip] = {}
        info[ip][ei] = {}
        info[ip][ei]["depth"] = str(self.rx.hypo_depth)
        info[ip][ei]["event_id"] = self._eventid

        # look for the presence of a strec_results load them
        try:
            strecdata = self.ic.getStrecJson()
        except AttributeError:
            pass
        else:
            info[st] = json.loads(strecdata)

        # the following items are primarily useful for PDL
        origin = self.origin
        info[ip][ei]["eventsource"] = origin.netid
        info[ip][ei]["netid"] = origin.netid
        # The netid could be a valid part of the eventsourcecode, so we have
        # to check here if it ***starts with*** the netid
        if origin.id.startswith(origin.netid):
            eventsourcecode = origin.id.replace(origin.netid, "", 1)
        else:
            eventsourcecode = origin.id
        info[ip][ei]["eventsourcecode"] = eventsourcecode
        info[ip][ei]["id"] = origin.id
        info[ip][ei]["productcode"] = origin.productcode
        info[ip][ei]["productsource"] = self.config["system"]["source_network"]
        info[ip][ei]["producttype"] = self.config["system"]["product_type"]

        info[ip][ei]["event_ref"] = getattr(origin, "reference", None)
        info[ip][ei]["fault_ref"] = self.rupture_obj.getReference()
        if "df2" in self.dataframes:
            df2 = getattr(self, "df2")
            info[ip][ei]["intensity_observations"] = str(
                np.size(df2.df["lon"])
            )
        else:
            info[ip][ei]["intensity_observations"] = "0"
        info[ip][ei]["latitude"] = str(self.rx.hypo_lat)
        info[ip][ei]["longitude"] = str(self.rx.hypo_lon)
        info[ip][ei]["location"] = origin.locstring
        info[ip][ei]["magnitude"] = str(self.rx.mag)
        info[ip][ei]["origin_time"] = origin.time.strftime(constants.TIMEFMT)
        if "df1" in self.dataframes:
            df1 = getattr(self, "df1", None)
            info[ip][ei]["seismic_stations"] = str(np.size(df1.df["lon"]))
        else:
            info[ip][ei]["seismic_stations"] = "0"
        info[ip][ei]["src_mech"] = origin.mech
        if self.config["system"]["source_description"] != "":
            info[ip][ei]["event_description"] = self.config["system"][
                "source_description"
            ]
        else:
            info[ip][ei]["event_description"] = origin.locstring
        # This AND src_mech?
        # look at the origin information for indications that this
        # event is a scenario
        condition1 = (
            hasattr(origin, "event_type")
            and origin.event_type.lower() == "scenario"
        )
        condition2 = origin.id.endswith("_se")
        if condition1 or condition2:
            info[ip][ei]["event_type"] = "SCENARIO"
        else:
            info[ip][ei]["event_type"] = "ACTUAL"
        if getattr(origin, "reviewed", None) is not None:
            info[ip][ei]["origin_reviewed"] = origin.reviewed
        else:
            info[ip][ei]["origin_reviewed"] = "unknown"

        info[op] = {}
        info[op][gm] = {}
        for myimt in self.full_out_set:
            info[op][gm][myimt] = {}
            if myimt == "MMI":
                units = "intensity"
            elif myimt == "PGV":
                units = "cms"
            else:
                units = "g"
            info[op][gm][myimt]["units"] = units
            if myimt in self.nominal_bias:
                info[op][gm][myimt]["bias"] = _string_round(
                    self.nominal_bias[myimt], 3
                )
            else:
                info[op][gm][myimt]["bias"] = None
            if myimt == "MMI":
                info[op][gm][myimt]["max_grid"] = _string_round(
                    np.max(self.outgrid[myimt]), 3
                )
                info[op][gm][myimt]["max"] = _string_round(
                    np.max(moutgrid[myimt]), 3
                )
            else:
                info[op][gm][myimt]["max_grid"] = _string_round(
                    np.exp(np.max(self.outgrid[myimt])), 3
                )
                info[op][gm][myimt]["max"] = _string_round(
                    np.exp(np.max(moutgrid[myimt])), 3
                )

        info[op][mi] = {}
        info[op][mi]["grid_points"] = {}
        info[op][mi]["grid_points"]["longitude"] = str(self.smnx)
        info[op][mi]["grid_points"]["latitude"] = str(self.smny)
        info[op][mi]["grid_points"]["units"] = ""
        info[op][mi]["grid_spacing"] = {}
        info[op][mi]["grid_spacing"]["longitude"] = _string_round(self.smdx, 7)
        info[op][mi]["grid_spacing"]["latitude"] = _string_round(self.smdy, 7)
        info[op][mi]["grid_spacing"]["units"] = "degrees"
        info[op][mi]["grid_span"] = {}
        if self.east <= 0 and self.west >= 0:
            info[op][mi]["grid_span"]["longitude"] = _string_round(
                self.east + 360.0 - self.west, 3
            )
        else:
            info[op][mi]["grid_span"]["longitude"] = _string_round(
                self.east - self.west, 3
            )
        info[op][mi]["grid_span"]["latitude"] = _string_round(
            self.north - self.south, 3
        )
        info[op][mi]["grid_span"]["units"] = "degrees"
        info[op][mi]["min"] = {}
        info[op][mi]["max"] = {}
        min_long = self.west
        max_long = self.east
        if self.rx.hypo_lon < 0:
            if min_long > 0:  # Crossing the 180 from the negative side
                min_long = min_long - 360
        else:
            if max_long < 0:  # Crossing the 180 from the positive side
                max_long = max_long + 360
        info[op][mi]["min"]["longitude"] = _string_round(min_long, 3)
        info[op][mi]["max"]["longitude"] = _string_round(max_long, 3)
        info[op][mi]["min"]["latitude"] = _string_round(self.south, 3)
        info[op][mi]["max"]["latitude"] = _string_round(self.north, 3)
        info[op][mi]["min"]["units"] = "degrees"
        info[op][mi]["max"]["units"] = "degrees"
        info[op][un] = {}
        info[op][un]["grade"] = mygrade
        info[op][un]["mean_uncertainty_ratio"] = _string_round(mean_rat, 3)
        if "df2" in self.dataframes:
            df2 = getattr(self, "df2")
            info[op][un]["total_flagged_mi"] = str(
                np.sum(df2.df["MMI_outliers"] | np.isnan(df2.df["MMI"]))
            )
        else:
            info[op][un]["total_flagged_mi"] = "0"
        if "df1" in self.dataframes:
            df1 = getattr(self, "df1", None)
            all_flagged = np.full(df1.df["lon"].shape, False, dtype=bool)
            for imtstr in df1.imts:
                if not imtstr + "_outliers" in df1.df:
                    continue
                if "MMI" in imtstr:
                    continue
                all_flagged |= df1.df[imtstr + "_outliers"] | np.isnan(
                    df1.df[imtstr]
                )
            all_flagged |= df1.df["flagged"]
            info[op][un]["total_flagged_pgm"] = str(np.sum(all_flagged))
        else:
            info[op][un]["total_flagged_pgm"] = "0"
        info[pp] = {}
        info[pp][gmm] = {}
        info[pp][gmm]["gmpe"] = {}
        info[pp][gmm]["gmpe"]["module"] = str(self.config["modeling"]["gmpe"])
        info[pp][gmm]["gmpe"]["reference"] = ""
        info[pp][gmm]["ipe"] = {}
        info[pp][gmm]["ipe"]["module"] = str(
            self.config["ipe_modules"][self.config["modeling"]["ipe"]][0]
        )
        info[pp][gmm]["ipe"]["reference"] = ""
        info[pp][gmm]["gmice"] = {}
        info[pp][gmm]["gmice"]["module"] = str(
            self.config["gmice_modules"][self.config["modeling"]["gmice"]][0]
        )
        info[pp][gmm]["gmice"]["reference"] = ""
        info[pp][gmm]["ccf"] = {}
        info[pp][gmm]["ccf"]["module"] = str(
            self.config["ccf_modules"][self.config["modeling"]["ccf"]][0]
        )
        info[pp][gmm]["ccf"]["reference"] = ""
        info[pp][gmm]["basin_correction"] = {}
        info[pp][gmm]["basin_correction"]["module"] = "None"
        info[pp][gmm]["basin_correction"]["reference"] = ""
        info[pp][gmm]["directivity"] = {}
        info[pp][gmm]["directivity"]["module"] = "None"
        info[pp][gmm]["directivity"]["reference"] = ""

        info[pp][mf] = {}
        info[pp][mf]["no_macroseismic"] = self.no_macroseismic
        info[pp][mf]["no_seismic"] = self.no_seismic
        info[pp][mf]["no_rupture"] = self.no_rupture

        info[pp][ms] = {}
        info[pp][ms]["bias_max_dsigma"] = str(self.bias_max_dsigma)
        info[pp][ms]["bias_max_mag"] = str(self.bias_max_mag)
        info[pp][ms]["bias_max_range"] = str(self.bias_max_range)
        info[pp][ms]["median_dist"] = "False"
        info[pp][ms]["do_outliers"] = self.do_outliers
        info[pp][ms]["outlier_deviation_level"] = str(
            self.outlier_deviation_level
        )
        info[pp][ms]["outlier_max_mag"] = str(self.outlier_max_mag)
        info[pp][sv] = {}
        info[pp][sv]["shakemap_revision"] = self.shakemap_version
        info[pp][sv]["shakemap_revision_id"] = self.shakemap_version
        info[pp][sv]["shakemap_modules_revision"] = importlib.metadata.version(
            "shakemap_modules"
        )
        info[pp][sv]["esi_shakelib_revision"] = get_shakelib_version()
        info[pp][sv]["process_time"] = strftime(
            constants.ALT_TIMEFMT, gmtime()
        )
        info[pp][sv]["map_version"] = self.ic.getVersionHistory()["history"][
            -1
        ][2]
        info[pp][sv]["map_comment"] = self.ic.getVersionHistory()["history"][
            -1
        ][3]
        info[pp][sv]["map_data_history"] = self.ic.getVersionHistory()[
            "history"
        ]
        info[pp][sv]["map_status"] = self.config["system"]["map_status"]
        info[pp][sr] = {}
        info[pp][sr]["vs30default"] = str(self.vs30default)
        info[pp][sr]["site_correction"] = "GMPE native"
        return info

    def _fill_station_json(self):
        """
        Get the station JSON dictionary and then add a bunch of stuff to it.
        """
        if not hasattr(self, "stations") or self.stations is None:
            return {"eventid": self._eventid, "features": []}
        sjdict = {}
        # ---------------------------------------------------------------------
        # Compute a bias for all the output IMTs in the data frames
        # ---------------------------------------------------------------------
        for ndf in self.dataframes:
            sdf = getattr(self, ndf).df
            for myimt in self.full_out_set:
                if isinstance(self.mu_h_yd[myimt], float):
                    mybias = sdf[myimt + "_pred_tau"] * self.mu_h_yd[myimt]
                    mybias_sig = np.sqrt(
                        sdf[myimt + "_pred_tau"] ** 2 * self.cov_hh_yd[myimt]
                    )
                else:
                    mybias = sdf[myimt + "_pred_tau"] * self.mu_h_yd[myimt][0]
                    mybias_sig = np.sqrt(
                        sdf[myimt + "_pred_tau"] ** 2
                        * self.cov_hh_yd[myimt][0, 0]
                    )
                sdf[myimt + "_bias"] = mybias.flatten()
                sdf[myimt + "_bias_sigma"] = mybias_sig.flatten()

        # ---------------------------------------------------------------------
        # Add the station data. The stationlist object has the original
        # data and produces a GeoJSON object (a dictionary, really), but
        # we need to add peak values and flagging that has been done here.
        # ---------------------------------------------------------------------
        #
        # First make a dictionary of distances
        #
        dist_dict = {"df1": {}, "df2": {}}
        for ndf in self.dataframes:
            dx = getattr(self, ndf).dx
            if isinstance(self.rupture_obj, PointRupture):
                for dm in get_distance_measures():
                    if dm == "rjb":
                        dm_arr = getattr(dx, "repi", None)
                    elif dm == "rrup":
                        dm_arr = getattr(dx, "rhypo", None)
                    else:
                        dm_arr = getattr(dx, dm, None)
                    if dm_arr is not None:
                        dist_dict[ndf][dm] = dm_arr
            else:
                for dm in get_distance_measures():
                    dm_arr = getattr(dx, dm, None)
                    if dm_arr is not None:
                        dist_dict[ndf][dm] = dm_arr
        #
        # Get the index for each station ID
        #
        sjdict = self.stations.getGeoJson()
        sta_ix = {"df1": {}, "df2": {}}
        for ndf in self.dataframes:
            sdf = getattr(self, ndf).df
            sta_ix[ndf] = dict(zip(sdf["id"], range(len(sdf["id"]))))
        #
        # Now go through the GeoJSON and add various properties and
        # amps from the df_dict dictionaries
        #
        sjdict_copy = copy.copy(sjdict["features"])
        for station in sjdict_copy:
            if station["id"] in sta_ix["df1"]:
                ndf = "df1"
                station["properties"]["station_type"] = "seismic"
            elif station["id"] in sta_ix["df2"]:
                ndf = "df2"
                station["properties"]["station_type"] = "macroseismic"
            else:
                # We're probably using --no_seismic or --no_macroseismic
                if self.no_seismic or self.no_macroseismic:
                    sjdict["features"].remove(station)
                    continue
                else:
                    raise ValueError(
                        f"Unknown station {station['id']} in stationlist"
                    )
            dfx = getattr(self, ndf)
            sdf = dfx.df
            six = sta_ix[ndf][station["id"]]
            #
            # Set the 'intensity', 'pga', and 'pgv' peak properties
            #
            if (
                "MMI" in sdf
                and not sdf["MMI_outliers"][six]
                and not np.isnan(sdf["MMI"][six])
            ):
                station["properties"]["intensity"] = float(
                    f"{sdf['MMI'][six]:.1f}"
                )
                station["properties"]["intensity_stddev"] = sdf["MMI_sd"][six]
                if "MMI_nresp" in sdf:
                    station["properties"]["nresp"] = int(sdf["MMI_nresp"][six])
                else:
                    station["properties"]["nresp"] = "null"
            else:
                station["properties"]["intensity"] = "null"
                station["properties"]["intensity_stddev"] = "null"
                station["properties"]["nresp"] = "null"

            if (
                "PGA" in sdf
                and not sdf["PGA_outliers"][six]
                and not np.isnan(sdf["PGA"][six])
                and (ndf != "df1" or not sdf["flagged"][six])
            ):
                station["properties"]["pga"] = _round_float(
                    np.exp(sdf["PGA"][six]) * 100, 4
                )
            else:
                station["properties"]["pga"] = "null"

            if (
                "PGV" in sdf
                and not sdf["PGV_outliers"][six]
                and not np.isnan(sdf["PGV"][six])
                and (ndf != "df1" or not sdf["flagged"][six])
            ):
                station["properties"]["pgv"] = _round_float(
                    np.exp(sdf["PGV"][six]), 4
                )
            else:
                station["properties"]["pgv"] = "null"
            #
            # Add vs30
            #
            station["properties"]["vs30"] = _round_float(dfx.sx.vs30[six], 2)
            #
            # Add the predictions so we can plot residuals
            #
            station["properties"]["predictions"] = []
            for key in sdf.keys():
                if not key.endswith("_pred"):
                    continue
                myamp = sdf[key][six]
                myamp_rock = sdf[key + "_rock"][six]
                myamp_soil = sdf[key + "_soil"][six]
                tau_str = "ln_tau"
                phi_str = "ln_phi"
                sigma_str = "ln_sigma"
                sigma_str_rock = "ln_sigma_rock"
                sigma_str_soil = "ln_sigma_soil"
                bias_str = "ln_bias"
                bias_sigma_str = "ln_bias_sigma"
                if key.startswith("PGV"):
                    value = np.exp(myamp)
                    value_rock = np.exp(myamp_rock)
                    value_soil = np.exp(myamp_soil)
                    units = "cm/s"
                elif key.startswith("MMI"):
                    value = myamp
                    value_rock = myamp_rock
                    value_soil = myamp_soil
                    units = "intensity"
                    tau_str = "tau"
                    phi_str = "phi"
                    sigma_str = "sigma"
                    sigma_str_rock = "sigma_rock"
                    sigma_str_soil = "sigma_soil"
                    bias_str = "bias"
                    bias_sigma_str = "bias_sigma"
                else:
                    value = np.exp(myamp) * 100
                    value_rock = np.exp(myamp_rock) * 100
                    value_soil = np.exp(myamp_soil) * 100
                    units = "%g"
                if self.gmpe_total_sd_only:
                    mytau = 0
                else:
                    mytau = sdf[key + "_tau"][six]
                myphi = sdf[key + "_phi"][six]
                mysigma = np.sqrt(mytau**2 + myphi**2)
                mysigma_rock = sdf[key + "_sigma_rock"][six]
                mysigma_soil = sdf[key + "_sigma_soil"][six]
                imt_name = key.lower().replace("_pred", "")
                if imt_name.upper() in self.full_out_set:
                    mybias = sdf[imt_name.upper() + "_bias"][six]
                    mybias_sigma = sdf[imt_name.upper() + "_bias_sigma"][six]
                else:
                    mybias = "null"
                    mybias_sigma = "null"
                station["properties"]["predictions"].append(
                    {
                        "name": imt_name,
                        "value": _round_float(value, 4),
                        "value_rock": _round_float(value_rock, 4),
                        "value_soil": _round_float(value_soil, 4),
                        "units": units,
                        tau_str: _round_float(mytau, 4),
                        phi_str: _round_float(myphi, 4),
                        sigma_str: _round_float(mysigma, 4),
                        sigma_str_rock: _round_float(mysigma_rock, 4),
                        sigma_str_soil: _round_float(mysigma_soil, 4),
                        bias_str: _round_float(mybias, 4),
                        bias_sigma_str: _round_float(mybias_sigma, 4),
                    }
                )
            #
            # For df1 stations, add the MMIs comverted from PGM
            #
            if ndf == "df1":
                station["properties"]["mmi_from_pgm"] = []
                for myimt in getattr(self, ndf).imts:
                    if myimt == "MMI":
                        continue
                    dimtstr = "derived_MMI_from_" + myimt
                    if dimtstr not in sdf:
                        continue
                    imt_name = myimt.lower()
                    myamp = sdf[dimtstr][six]
                    mysd = sdf[dimtstr + "_sd"][six]
                    if np.isnan(myamp):
                        myamp = "null"
                        mysd = "null"
                        flag = "0"
                    else:
                        if sdf[myimt + "_outliers"][six] == 1:
                            flag = "Outlier"
                        else:
                            flag = "0"
                    station["properties"]["mmi_from_pgm"].append(
                        {
                            "name": imt_name,
                            "value": _round_float(myamp, 2),
                            "sigma": _round_float(mysd, 2),
                            "flag": flag,
                        }
                    )

            #
            # For df2 stations, add the PGMs converted from MMI
            #
            if ndf == "df2":
                station["properties"]["pgm_from_mmi"] = []
                for myimt in getattr(self, ndf).imts:
                    if myimt == "MMI":
                        continue
                    imt_name = myimt.lower()
                    myamp = sdf[myimt][six]
                    mysd = sdf[myimt + "_sd"][six]
                    if myimt == "PGV":
                        value = np.exp(myamp)
                        units = "cm/s"
                    else:
                        value = np.exp(myamp) * 100
                        units = "%g"
                    if np.isnan(value):
                        value = "null"
                        mysd = "null"
                        flag = "0"
                    else:
                        if sdf[myimt + "_outliers"][six] == 1:
                            flag = "Outlier"
                        else:
                            flag = "0"
                    station["properties"]["pgm_from_mmi"].append(
                        {
                            "name": imt_name,
                            "value": _round_float(value, 4),
                            "units": units,
                            "ln_sigma": _round_float(mysd, 4),
                            "flag": flag,
                        }
                    )
            #
            # Set the generic distance property (this is rrup)
            #
            station["properties"]["distance"] = _round_float(
                sdf["rrup"][six], 3
            )
            #
            # Set the specific distances properties
            #
            station["properties"]["distances"] = {}
            for dm, dm_arr in dist_dict[ndf].items():
                station["properties"]["distances"][dm] = _round_float(
                    dm_arr[six], 3
                )
            #
            # Set the outlier flags
            #
            mflag = "0"
            if ndf == "df1" and sdf["flagged"][six]:
                mflag = "ManuallyFlagged"
            for channel in station["properties"]["channels"]:
                for amp in channel["amplitudes"]:
                    if amp["flag"] != "0":
                        amp["flag"] += "," + mflag
                    else:
                        amp["flag"] = mflag
                    amp_name = amp["name"].upper()
                    if (
                        amp_name + "_outliers" in sdf
                        and sdf[amp_name + "_outliers"][six]
                    ):
                        if amp["flag"] == "0":
                            amp["flag"] = "Outlier"
                        elif "Outlier" in amp["flag"]:
                            pass
                        else:
                            amp["flag"] += ",Outlier"
        sjdict["metadata"] = {"eventid": self._eventid}
        return sjdict

    def _store_gridded_data(self, oc):
        """
        Store gridded data in the output container.
        """
        metadata = {}
        min_long = self.west
        max_long = self.east
        if self.rx.hypo_lon < 0:
            if min_long > 0:  # Crossing the 180 from the negative side
                min_long = min_long - 360
        else:
            if max_long < 0:  # Crossing the 180 from the positive side
                max_long = max_long + 360
        metadata["xmin"] = min_long
        metadata["xmax"] = max_long
        metadata["ymin"] = self.south
        metadata["ymax"] = self.north
        metadata["nx"] = self.smnx
        metadata["ny"] = self.smny
        metadata["dx"] = self.smdx
        metadata["dy"] = self.smdy
        #
        # Put the Vs30 grid in the output container
        #
        _, units, digits = _get_layer_info("vs30")
        metadata["units"] = units
        metadata["digits"] = digits
        oc.setArray([], "vs30", self.sx_out.vs30, metadata=metadata)
        #
        # Now do the distance grids
        #
        metadata["units"] = "km"
        metadata["digits"] = 4
        if isinstance(self.rupture_obj, PointRupture):
            for dm in get_distance_measures():
                if dm == "rrup":
                    dm_arr = getattr(self.dx_out, "rhypo", None)
                elif dm == "rjb":
                    dm_arr = getattr(self.dx_out, "repi", None)
                else:
                    dm_arr = getattr(self.dx_out, dm, None)
                if dm_arr is not None:
                    oc.setArray(["distances"], dm, dm_arr, metadata=metadata)
        else:
            for dm in get_distance_measures():
                dm_arr = getattr(self.dx_out, dm, None)
                if dm_arr is not None:
                    oc.setArray(["distances"], dm, dm_arr, metadata=metadata)
        metadata["units"] = "seconds"
        metadata["digits"] = 1
        oc.setArray([], "imt_periods", self.imt_per, metadata=metadata)
        oc.setDictionary([], "imt_per_ix", self.imt_per_ix)

        #
        # Output the data and uncertainty grids
        #
        component = self.config["interp"]["component"]
        std_metadata = copy.copy(metadata)
        for key, value in self.outgrid.items():
            # set the data grid
            _, units, digits = _get_layer_info(key)
            metadata["units"] = units
            metadata["digits"] = digits

            # set the mean and uncertainty grids
            _, units, digits = _get_layer_info(key + "_sd")
            std_metadata["units"] = units
            std_metadata["digits"] = digits
            oc.setIMTGrids(
                key,
                component,
                value,
                metadata,
                self.outsd[key],
                std_metadata,
                self.outphi[key],
                self.outtau[key],
            )
            # Realizations stuff
            sub_groups = ["imts", component, key]
            oc.setArray(
                sub_groups, "add_uncertainty", self.rez_add_uncertainty[key]
            )
            oc.setArray(sub_groups, "Sigma_HH_YD", self.rez_sigma_hh_yd[key])
            oc.setArray(sub_groups, "C", self.rez_c[key])
            oc.setArray(sub_groups, "sta_per_ix", self.rez_sta_per_ix[key])
            oc.setArray(sub_groups, "sta_phi", self.sta_phi[key])
            oc.setArray(sub_groups, "sta_lons_rad", self.sta_lons_rad[key])
            oc.setArray(sub_groups, "sta_lats_rad", self.sta_lats_rad[key])
        #
        # Directivity
        #
        del metadata["units"]
        del metadata["digits"]
        if self.do_directivity is True:
            for k, v in self.dir_output.items():
                imtstr, _, _ = _get_layer_info(k)
                oc.setArray(["directivity"], imtstr, v, metadata=metadata)

    def _store_point_data(self, oc):
        """
        Store point data in the output container.
        """
        #
        # Store the Vs30
        #
        vs30_metadata = {"units": "m/s", "digits": 4}
        oc.setArray(
            [], "vs30", self.sx_out.vs30.flatten(), metadata=vs30_metadata
        )
        #
        # Store the distances
        #
        distance_metadata = {"units": "km", "digits": 4}
        if isinstance(self.rupture_obj, PointRupture):
            for dm in get_distance_measures():
                if dm == "rrup":
                    dm_arr = getattr(self.dx_out, "rhypo", None)
                elif dm == "rjb":
                    dm_arr = getattr(self.dx_out, "repi", None)
                else:
                    dm_arr = getattr(self.dx_out, dm, None)
                if dm_arr is not None:
                    oc.setArray(
                        ["distances"],
                        dm,
                        dm_arr.flatten(),
                        metadata=distance_metadata,
                    )
        else:
            for dm in get_distance_measures():
                dm_arr = getattr(self.dx_out, dm, None)
                if dm_arr is not None:
                    oc.setArray(
                        ["distances"],
                        dm,
                        dm_arr.flatten(),
                        metadata=distance_metadata,
                    )
        #
        # Store the IMTs
        #
        period_metadata = {"units": "seconds", "digits": 1}
        oc.setArray([], "imt_periods", self.imt_per, metadata=period_metadata)
        oc.setDictionary([], "imt_per_ix", self.imt_per_ix)
        ascii_ids = np.array(
            [np.char.encode(x, encoding="ascii") for x in self.idents]
        ).flatten()
        component = self.config["interp"]["component"]
        for key, value in self.outgrid.items():
            # set the data grid
            _, units, digits = _get_layer_info(key)
            mean_metadata = {"units": units, "digits": digits}
            # set the uncertainty grid
            _, units, digits = _get_layer_info(key + "_sd")
            std_metadata = {"units": units, "digits": digits}
            oc.setIMTArrays(
                key,
                component,
                self.dx_out.lons.flatten(),
                self.dx_out.lats.flatten(),
                ascii_ids,
                value.flatten(),
                mean_metadata,
                self.outsd[key].flatten(),
                std_metadata,
                self.outphi[key].flatten(),
                self.outtau[key].flatten(),
            )
            # Store the predictions
            oc.setIMTArrays(
                key + "_predictions",
                component,
                self.dx_out.lons.flatten(),
                self.dx_out.lats.flatten(),
                ascii_ids,
                self.pred_out[key].flatten(),
                mean_metadata,
                self.pred_out_sd[key].flatten(),
                std_metadata,
            )
            sub_groups = ["imts", component, key]
            oc.setArray(
                sub_groups, "add_uncertainty", self.rez_add_uncertainty[key]
            )
            oc.setArray(sub_groups, "Sigma_HH_YD", self.rez_sigma_hh_yd[key])
            oc.setArray(sub_groups, "C", self.rez_c[key])
            oc.setArray(sub_groups, "sta_per_ix", self.rez_sta_per_ix[key])
            oc.setArray(sub_groups, "sta_phi", self.sta_phi[key])
            oc.setArray(sub_groups, "sta_lons_rad", self.sta_lons_rad[key])
            oc.setArray(sub_groups, "sta_lats_rad", self.sta_lats_rad[key])

    def _store_attenuation_data(self, oc):
        """
        Output arrays of rock and soil attenuation curves
        """

        if isinstance(self.rupture_obj, PointRupture):
            for dist_type in ["repi", "rhypo", "rrup", "rjb"]:
                if dist_type == "rjb":
                    oc.setArray(
                        ["attenuation", "distances"],
                        dist_type,
                        getattr(self.atten_dx, "repi", None),
                    )
                elif dist_type == "rrup":
                    oc.setArray(
                        ["attenuation", "distances"],
                        dist_type,
                        getattr(self.atten_dx, "rhypo", None),
                    )
                else:
                    oc.setArray(
                        ["attenuation", "distances"],
                        dist_type,
                        getattr(self.atten_dx, dist_type, None),
                    )
        else:
            for dist_type in ["repi", "rhypo", "rrup", "rjb"]:
                oc.setArray(
                    ["attenuation", "distances"],
                    dist_type,
                    getattr(self.atten_dx, dist_type, None),
                )

        imtstrs = self.atten_rock_mean.keys()
        for imtstr in imtstrs:
            oc.setArray(
                ["attenuation", "rock", imtstr],
                "mean",
                self.atten_rock_mean[imtstr],
            )
            oc.setArray(
                ["attenuation", "soil", imtstr],
                "mean",
                self.atten_soil_mean[imtstr],
            )
            oc.setArray(
                ["attenuation", "rock", imtstr],
                "std",
                self.atten_rock_sd[imtstr],
            )
            oc.setArray(
                ["attenuation", "soil", imtstr],
                "std",
                self.atten_soil_sd[imtstr],
            )
        return

    #
    # Helper function to call get_mean_and_stddevs for the
    # appropriate object given the IMT and describe the
    # MultiGMPE structure.
    #
    def _gmas(self, gmpe, sx, dx, oqimt, apply_gafs):
        """
        This is a helper function to call get_mean_and_stddevs for the
        appropriate object given the IMT.

        Args:
            gmpe:
                A GMPE instance.
            sx:
                Sites context.
            dx:
                Distance context.
            oqimt:
                List of OpenQuake IMTs.
            apply_gafs (boolean):
                Whether or not to apply the generic
                amplification factors to the GMPE output.

        Returns:
            tuple: Tuple of two items:

                - Numpy array of means,
                - List of numpy array of standard deviations corresponding to
                  therequested stddev_types.

        """
        if "MMI" in oqimt:
            pe = self.ipe
            sd_types = self.ipe_stddev_types

            if self.use_simulations:
                self.info = {}
        else:
            pe = gmpe
            sd_types = self.gmpe_stddev_types

            if not self.use_simulations:
                # --------------------------------------------------------------------
                # Describe the MultiGMPE
                # --------------------------------------------------------------------
                self.info["multigmpe"][str(oqimt)] = gmpe.__describe__()
            else:
                self.info = {}

        mean, stddevs = pe.get_mean_and_stddevs(
            copy.deepcopy(sx),
            copy.deepcopy(self.rx),
            copy.deepcopy(dx),
            [oqimt],
            sd_types,
        )

        # Include generic amp factors?
        if apply_gafs:
            gafs = get_generic_amp_factors(dx, str(oqimt))
            if gafs is not None:
                mean += gafs.flatten()

        # Does directivity apply to this imt?
        row_pers = Rowshandel2013.getPeriods()

        if oqimt.string == "PGA":
            imt_ok = False
        elif oqimt.string in ["PGV", "MMI"]:
            tper = 1.0
            imt_ok = True
        elif "SA" in oqimt.string:
            tper = oqimt.period
            min_per = np.min(row_pers)
            max_per = np.max(row_pers)
            imt_ok = min_per <= tper <= max_per
        else:
            imt_ok = False

        # Did we calculate directivity?
        calc_dir = self.do_directivity

        if calc_dir and imt_ok:
            # Use distance context to figure out which directivity result
            # we need to use.
            all_fd = None
            for dirdf, tmpdx in self.dir_results:
                if dx == tmpdx:
                    all_fd = dirdf.getFd()
                    break
            if all_fd is None:
                raise RuntimeError(
                    "Failed to detect dataframe for directivity calculation."
                )

            # Does oqimt match any of those periods?
            if tper in row_pers:
                fd = all_fd[row_pers.index(tper)]
            else:
                # Log(period) interpolation.
                apers = np.array(row_pers)
                per_below = np.max(apers[apers < tper])
                per_above = np.min(apers[apers > tper])
                fd_below = all_fd[row_pers.index(per_below)]
                fd_above = all_fd[row_pers.index(per_above)]
                x1 = np.log(per_below)
                x2 = np.log(per_above)
                fd = fd_below + (np.log(tper) - x1) * (fd_above - fd_below) / (
                    x2 - x1
                )
            # Reshape to match the mean
            fd = fd.reshape(mean.shape)
            # Store the interpolated grid
            imtstr = str(oqimt)
            self.dir_output[imtstr] = fd
            if oqimt.string == "MMI":
                mean *= np.exp(fd)
            else:
                mean += fd

        return mean[0], stddevs

    def _adjust_resolution(self):
        """
        This is a helper function to adjust the resolution to be under
        the maximum value specified in the config.
        """
        # We want to only use resolutions that are multiples of 1 minute or
        # an integer division of 1 minute.
        one_minute = 1 / 60
        multiples = np.arange(1, 11)
        divisions = 1 / multiples
        factors = np.sort(np.unique(np.concatenate((divisions, multiples))))
        ok_res = one_minute * factors
        latspan = self.north - self.south

        # Deal with possible 180 longitude disontinuity
        if self.east > self.west:
            lonspan = self.east - self.west
        else:
            xmax = self.east + 360
            lonspan = xmax - self.west
        nx = np.floor(lonspan / self.smdx) + 1
        ny = np.floor(latspan / self.smdy) + 1
        ngrid = nx * ny
        nmax = self.nmax
        if ngrid > nmax:
            self.logger.info(
                "Extent and resolution of shakemap results in "
                "too many grid points. Adjusting resolution..."
            )
            self.logger.info("Longitude span: %f", lonspan)
            self.logger.info("Latitude span: %f", latspan)
            self.logger.info("Current dx: %f", self.smdx)
            self.logger.info("Current dy: %f", self.smdy)
            self.logger.info("Current number of grid points: %i", ngrid)
            self.logger.info("Max grid points allowed: %i", nmax)
            target_res = (
                -(latspan + lonspan)
                - np.sqrt(
                    latspan**2
                    + lonspan**2
                    + 2 * latspan * lonspan * (2 * nmax - 1)
                )
            ) / (2 * (1 - nmax))

            if np.any(ok_res > target_res):
                sel_res = np.min(ok_res[ok_res > target_res])
            else:
                sel_res = np.max(ok_res)
            self.smdx = sel_res
            self.smdy = sel_res
            self.logger.info("Updated dx: %f", self.smdx)
            self.logger.info("Updatd dy: %f", self.smdy)
            nx = np.floor(lonspan / self.smdx) + 1
            ny = np.floor(latspan / self.smdy) + 1
            self.logger.info("Updated number of grid points: %i", nx * ny)


def _round_float(val, digits):
    if ma.is_masked(val) or val == "--" or val == "null" or np.isnan(val):
        return None
    return float(("%." + str(digits) + "f") % val)


def _string_round(val, digits):
    if ma.is_masked(val) or val == "--" or val == "null" or np.isnan(val):
        return None
    return str(_round_float(val, digits))


def _get_period_arrays(*args):
    """
    Return 1) a sorted array of the periods represented by the IMT list(s)
    in the input, and 2) a dictionary of the IMTs and their indices.

    Args:
        *args (list): One or more lists of IMTs.

    Returns:
        array, dict: Numpy array of the (sorted) periods represented by the
        IMTs in the input list(s), and a dictionary of the IMTs and their
        indices into the period array.
    """
    imt_per = set()
    imt_per_ix = {}
    for imt_list in args:
        if imt_list is None:
            continue
        for imtstr in imt_list:
            if imtstr == "PGA":
                period = 0.01
            elif imtstr in ("PGV", "MMI"):
                period = 1.0
            else:
                period = _get_period_from_imt(imtstr)
            imt_per.add(period)
            imt_per_ix[imtstr] = period
    imt_per = sorted(imt_per)
    for imtstr, period in imt_per_ix.items():
        imt_per_ix[imtstr] = imt_per.index(period)
    return np.array(imt_per), imt_per_ix


def _get_period_from_imt(imtstr):
    """
    Return a float representing the period of the SA IMT in the input.

    Args:
        imtstr (str): A string representing an SA IMT.

    Returns:
        float: The period of the SA IMT as a float.
    """
    return float(imtstr.replace("SA(", "").replace(")", ""))


def _get_nearest_imts(imtstr, imtset, saset):
    """
    Return the input IMT, or it's closest surrogarte (or bracket) found
    in imtset.

    Args:
        imtstr (str): An (OQ-style) IMT string.
        imtset (list): A list of IMTs to search for imtstr or its closest
            surrogate (or bracket).
        saset (list): The SA IMTs found in imtset.

    Returns:
        tuple: The IMT, it's closest surrogate, or a bracket of SAs with
        periods on either side of the IMT's period, from the IMTs in intset.
    """
    if imtstr in imtset:
        return (imtstr,)
    #
    # If we're here, then we know that IMT isn't in the inputs. Try
    # some alternatives.
    #
    if imtstr == "PGA":
        #
        # Use the highest frequency in the inputs
        #
        if len(saset):
            return (sorted(saset, key=_get_period_from_imt)[0],)
        else:
            return ()
    elif imtstr == "PGV":
        #
        # PGV has no surrogate
        #
        return ()
    elif imtstr == "MMI":
        #
        # MMI has no surrogate
        #
        return ()
    elif imtstr.startswith("SA("):
        #
        # We know the actual IMT isn't here, so get the bracket
        #
        return _get_sa_bracket(imtstr, saset)
    else:
        raise ValueError(f"Unknown IMT {imtstr} in get_imt_bracket")


def _get_sa_bracket(myimt, saset):
    """
    For a given SA IMT, look through the input SAs and return a tuple of
    a) a pair of IMT strings representing the periods bracketing the given
    period; or b) the single IMT representing the first or last period in
    the input list if the given period is off the end of the list.

    Args:
        myper (float): The period to search for in the input lists.
        saset (list): A list of SA IMTs.

    Returns:
        tuple: One or two strings representing the IMTs closest to or
        bracketing the input IMT.

    """
    if len(saset) == 0:
        return ()
    #
    # Stick the target IMT into a copy of the list of SAs, then sort
    # the list by period.
    #
    ss = saset.copy()
    ss.append(myimt)
    tmplist = sorted(ss, key=_get_period_from_imt)
    nimt = len(tmplist)
    #
    # Get the index of the target IMT in the sorted list
    #
    myix = tmplist.index(myimt)
    #
    # If the target IMT is off the end of the list, return the
    # appropriate endpoint; else return the pair of IMTs that
    # bracket the target.
    #
    if myix == 0:
        return (tmplist[1],)
    elif myix == nimt - 1:
        return (tmplist[-2],)
    else:
        return (tmplist[myix - 1], tmplist[myix + 1])


def _get_imt_lists(df):
    """
    Given a data frame, return a list of lists of valid IMTS for
    each station in the dataframe; also return a list of the valid
    SA IMTs for each station.

    Args:
        df (DataFrame): A DataFrame.

    Returns:
        list, list: Two lists of lists: each list contains lists
        corresponding to the stations in the data frame: the first
        list contains all of the valid IMTs for that station, the
        second list contains just the valid SA IMTs for the station.
    """
    imtlist = []
    salist = []
    nlist = np.size(df.df["lon"])
    for ix in range(nlist):
        valid_imts = []
        sa_imts = []
        if "flagged" not in df.df or not df.df["flagged"][ix]:
            for this_imt in df.imts:
                if (
                    this_imt + "_residual" in df.df
                    and not np.isnan(df.df[this_imt + "_residual"][ix])
                    and this_imt + "_outliers" in df.df
                    and not df.df[this_imt + "_outliers"][ix]
                ):
                    valid_imts.append(this_imt)
                    if this_imt.startswith("SA("):
                        sa_imts.append(this_imt)
        imtlist.append(valid_imts)
        salist.append(sa_imts)
    return imtlist, salist


def _get_map_grade(do_grid, outsd, psd, moutgrid):
    """
    Computes a 'grade' for the map. Essentially looks at the ratio of
    the computed PGA uncertainty to the predicted PGA uncertainty for
    the area inside the MMI 6 contour. If the maximum MMI is less than
    6, or the map is not a grid, the grade and mean ratio are set to '--'.

    Args:
        do_grid (bool): Is the map a grid (True) or a list of points
            (False)?

        outsd (dict): A dictionary of computed uncertainty arrays.

        psd (dict): A dictionary of predicted uncertainty arrays.

        moutgrid (dict): A dictionary of landmasked output ground
            motion arrays.

    Returns:
        tuple: The mean uncertainty ratio and the letter grade.
    """
    mean_rat = "--"
    mygrade = "--"
    if (
        not do_grid
        or "PGA" not in outsd
        or "PGA" not in psd
        or "MMI" not in moutgrid
    ):
        return mean_rat, mygrade
    sd_rat = outsd["PGA"] / psd["PGA"]
    mmimasked = ma.masked_less(moutgrid["MMI"], 6.0)
    mpgasd_rat = ma.masked_array(sd_rat, mask=ma.getmaskarray(mmimasked))
    if not np.all(mpgasd_rat.mask):
        gvals = [0.96, 0.98, 1.05, 1.25]
        grades = ["A", "B", "C", "D", "F"]
        mean_rat = mpgasd_rat.mean()
        for ix, val in enumerate(gvals):
            if mean_rat <= val:
                mygrade = grades[ix]
                break
        if mygrade == "--":
            mygrade = "F"
    return mean_rat, mygrade


def _get_layer_info(layer):
    """
    We need a way to get units information about intensity measure types
    and translate between OpenQuake naming convention and ShakeMap grid naming
    convention.

    Args:
        layer (str): ShakeMap grid name.

    Returns:
        tuple: Tuple including:

            - OpenQuake naming convention,
            - units,
            - significant digits.

    """
    layer_out = layer
    layer_units = ""
    layer_digits = 4  # number of significant digits

    if layer.endswith("_sd"):
        layer_out = oq_to_file(layer.replace("_sd", ""))
        layer_out = layer_out + "_sd"
    else:
        layer_out = oq_to_file(layer)
    if layer.startswith("SA"):
        layer_units = "ln(g)"
    elif layer.startswith("PGA"):
        layer_units = "ln(g)"
    elif layer.startswith("PGV"):
        layer_units = "ln(cm/s)"
    elif layer.startswith("MMI"):
        layer_units = "intensity"
        layer_digits = 2
    elif layer.startswith("vs30"):
        layer_units = "m/s"
    else:
        raise ValueError(f"Unknown layer type: {layer}")

    return (layer_out, layer_units, layer_digits)


def main():
    """
    The main function for cases where this function is called in standalone
    mode.
    """
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Process ShakeMap input data to create output grids or points.
    """
    evid, datadir, outdir, logdir, _, vhash = get_module_args(
        description,
        True,
        False,
        "--no_seismic",
        "-s",
        "store_true",
        "Do not process any instrumental seismic data in the input directory.",
        "--no_macroseismic",
        "-m",
        "store_true",
        "Do not process any macroseismic data in the input directory.",
        "--no_rupture",
        "-r",
        "store_true",
        "Do not process any finite fault data in the input directory.",
    )

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "shape.log")
    logger = get_generic_logger(logfile=logfile)

    mod = ModelModule(
        evid,
        process="main",
        logger=logger,
        no_seismic=vhash["no_seismic"],
        no_macroseismic=vhash["no_macroseismic"],
        no_rupture=vhash["no_rupture"],
    )
    mod.execute(indir=datadir, outdir=outdir)


if __name__ == "__main__":
    main()
