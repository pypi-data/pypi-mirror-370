# stdlib imports
import argparse
import glob
import inspect
import logging
import os.path
import re
import shutil
import sys
from datetime import datetime
from configobj import ConfigObj

# third party imports
from validate import Validator

# local imports
from esi_utils_io.smcontainers import ShakeMapOutputContainer
from esi_utils_rupture import constants
from shakemap_modules.base.base import CoreModule
from shakemap_modules.utils.config import config_error, get_config_paths, get_data_path

NO_TRANSFER = "NO_TRANSFER"
SAVE_FILE = ".saved"


class TransferBaseModule(CoreModule):
    """
    Base class for transfer modules.
    """

    def __init__(
        self,
        eventid,
        cancel=False,
        devconfig=False,
        process="shakemap",
        logger=None,
    ):
        """
        Instantiate a CoreModule class with an event ID.
        """
        super(TransferBaseModule, self).__init__(eventid, logger=logger)
        self.process = process
        self.cancel = cancel
        self.usedevconfig = devconfig

    def execute(self, datadir=None, outdir=None, config=None):
        if self.process == "shakemap":
            install_path, data_path = get_config_paths()
            self.datadir = os.path.join(data_path, self._eventid, "current")
        else:
            if datadir is None:
                raise FileNotFoundError(f"datadir must be provided.")
            self.datadir = datadir

        if not os.path.isdir(self.datadir):
            raise NotADirectoryError(f"{self.datadir} is not a valid directory.")

        # look for the presence of a NO_TRANSFER file in the datadir.
        notransfer = os.path.join(self.datadir, NO_TRANSFER)
        if os.path.isfile(notransfer):
            self.logger.info(f"Event has a {NO_TRANSFER} file blocking transfer.")
            return

        # get the path to the transfer.conf spec file
        configspec = get_data_path() / "transferspec.conf"

        # Get the system transfer.conf file
        if self.process == "shakemap":
            transfer_conf = os.path.join(install_path, "config", "transfer.conf")
        else:
            transfer_conf = config
        if not os.path.isfile(transfer_conf):
            raise FileNotFoundError(f"{transfer_conf} does not exist.")
        # get the config information for transfer
        config_global = ConfigObj(transfer_conf, configspec=f"{configspec}")

        # Validate the resulting config dict
        results = config_global.validate(Validator())
        if not isinstance(results, bool) or not results:
            config_error(config_global, results)

        # look for an event-specific transfer.conf file
        transfer_event_conf = os.path.join(self.datadir, "transfer.conf")
        if os.path.isfile(transfer_event_conf):
            config_event_global = ConfigObj(transfer_event_conf)
            # Add the event-specific stuff to the global stuff
            config_global.merge(config_event_global)

        self.config = config_global

        # get the output container with all the things in it
        products_dir = os.path.join(self.datadir, "products")
        datafile = os.path.join(products_dir, "shake_result.hdf")
        if not os.path.isfile(datafile):
            raise FileNotFoundError(f"{datafile} does not exist.")

        # Open the ShakeMapOutputContainer and extract the data
        container = ShakeMapOutputContainer.load(datafile)
        # extract the info.json object from the container
        self.info = container.getMetadata()
        container.close()

        if self.process == "shakemap" or (outdir is not None):
            # check for the presence of a .saved file. If found, do nothing.
            # Otherwise, create the backup directory.
            save_file = os.path.join(self.datadir, SAVE_FILE)
            if not os.path.isfile(save_file):
                logging.info("Making backup directory...")
                if self.process == "shakemap":
                    self._make_backup(data_path, outdir)
                else:
                    self._make_backup(self.datadir, outdir)
                with open(save_file, "wt") as f:
                    tnow = datetime.utcnow().strftime(constants.TIMEFMT)
                    f.write(f"Saved {tnow} by {self.command_name}\n")
                logging.info("...done.")

    def getProperties(self, info, props=None):
        properties = {}
        product_properties = {}
        # origin info
        origin = info["input"]["event_information"]
        properties["eventsource"] = origin["netid"]
        # The netid could be a valid part of the eventsourcecode, so we have to
        # check here if it ***starts with*** the netid
        # This fix should already be done by the time we get here, but this
        # is just an insurance check
        if origin["eventsourcecode"].startswith(origin["netid"]):
            eventsourcecode = origin["eventsourcecode"].replace(origin["netid"], "", 1)
        else:
            eventsourcecode = origin["eventsourcecode"]
        properties["eventsourcecode"] = eventsourcecode
        properties["code"] = (
            origin["productcode"] +
            self.config["pdl"]["comcat"]["system_id"]
        )
        properties["source"] = origin["productsource"]
        properties["type"] = origin["producttype"]

        properties["magnitude"] = float(origin["magnitude"])
        properties["latitude"] = float(origin["latitude"])
        properties["longitude"] = float(origin["longitude"])
        properties["depth"] = float(origin["depth"])
        try:
            properties["eventtime"] = datetime.strptime(
                origin["origin_time"], constants.TIMEFMT
            )
        except ValueError:
            properties["eventtime"] = datetime.strptime(
                origin["origin_time"], constants.ALT_TIMEFMT
            )

        product_properties["event-type"] = origin["event_type"]
        product_properties["event-description"] = origin["event_description"]

        # other metadata
        if "MMI" in info["output"]["ground_motions"]:
            mmi_info = info["output"]["ground_motions"]["MMI"]
            product_properties["maxmmi"] = mmi_info["max"]
            product_properties["maxmmi-grid"] = mmi_info["max_grid"]

        if "PGV" in info["output"]["ground_motions"]:
            pgv_info = info["output"]["ground_motions"]["PGV"]
            product_properties["maxpgv"] = pgv_info["max"]
            product_properties["maxpgv-grid"] = pgv_info["max_grid"]

        if "PGA" in info["output"]["ground_motions"]:
            pga_info = info["output"]["ground_motions"]["PGA"]
            product_properties["maxpga"] = pga_info["max"]
            product_properties["maxpga-grid"] = pga_info["max_grid"]

        if "SA(0.3)" in info["output"]["ground_motions"]:
            psa03_info = info["output"]["ground_motions"]["SA(0.3)"]
            product_properties["maxpsa03"] = psa03_info["max"]
            product_properties["maxpsa03-grid"] = psa03_info["max_grid"]

        if "SA(1.0)" in info["output"]["ground_motions"]:
            psa10_info = info["output"]["ground_motions"]["SA(1.0)"]
            product_properties["maxpsa10"] = psa10_info["max"]
            product_properties["maxpsa10-grid"] = psa10_info["max_grid"]

        if "SA(3.0)" in info["output"]["ground_motions"]:
            psa30_info = info["output"]["ground_motions"]["SA(3.0)"]
            product_properties["maxpsa30"] = psa30_info["max"]
            product_properties["maxpsa30-grid"] = psa30_info["max_grid"]

        mapinfo = info["output"]["map_information"]
        product_properties["minimum-longitude"] = mapinfo["min"]["longitude"]
        product_properties["minimum-latitude"] = mapinfo["min"]["latitude"]
        product_properties["maximum-longitude"] = mapinfo["max"]["longitude"]
        product_properties["maximum-latitude"] = mapinfo["max"]["latitude"]

        vinfo = info["processing"]["shakemap_versions"]
        product_properties["process-timestamp"] = vinfo["process_time"]
        product_properties["version"] = vinfo["map_version"]
        product_properties["map-status"] = vinfo["map_status"]
        product_properties["shakemap-code-version"] = vinfo["shakemap_revision"]

        # if this process is being run manually, set the review-status property
        # to "reviewed". If automatic, then set to "automatic".
        if props is None or "review-status" not in props:
            product_properties["review-status"] = "automatic"
            if sys.stdout is not None and sys.stdout.isatty():
                product_properties["review-status"] = "reviewed"

        # what gmice was used for the model calculations
        gmice = info["processing"]["ground_motion_modules"]["gmice"]["module"]
        product_properties["gmice"] = gmice

        if props:
            for this_prop, value in props.items():
                product_properties[this_prop] = value

        return (properties, product_properties)

    def _make_backup(self, data_path, outdir=None):
        if self.process == "shakemap":
            data_dir = os.path.join(data_path, self._eventid)
            outdir = data_dir
            current_dir = os.path.join(data_dir, "current")
            backup_dirs = glob.glob(os.path.join(data_dir, "backup*"))
        else:
            current_dir = data_path
            backup_dirs = glob.glob(os.path.join(outdir, "backup*"))

        latest_version = 0

        # and get the most recent version number
        for backup_dir in backup_dirs:
            if not os.path.isdir(backup_dir):
                continue
            match = re.search("[0-9]*$", backup_dir)
            if match is not None:
                version = int(match.group())
                if version > latest_version:
                    latest_version = version

        new_version = latest_version + 1
        backup = os.path.join(outdir, "backup%04i" % new_version)
        shutil.copytree(current_dir, backup)
        logging.debug(f"Created backup directory {backup}")

    def parseArgs(self, arglist):
        """
        Set up the object to accept the --cancel flag.
        """
        parser = argparse.ArgumentParser(
            prog=self.__class__.command_name, description=inspect.getdoc(self.__class__)
        )
        helpstr = "Cancel this event."
        parser.add_argument(
            "-c", "--cancel", help=helpstr, action="store_true", default=False
        )
        helpstr = (
            'Send products to the PDL server configured in "devconfig" '
            "in the transfer.conf configuration file rather than the "
            'default "configfile".'
        )
        parser.add_argument(
            "-d", "--dev", help=helpstr, action="store_true", default=False
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
        self.cancel = args.cancel
        self.usedevconfig = args.dev
        return args.rem
