# stdlib imports
import os.path

# third party imports

# local imports
from esi_utils_rupture import constants
from esi_utils_rupture.origin import read_event_file
from shakemap_modules.base.base import CoreModule
from shakemap_modules.utils.amps import AmplitudeHandler
from shakemap_modules.utils.config import get_config_paths
from shakemap_modules.base.cli import get_module_args
from shakemap_modules.utils.logging import get_generic_logger


class AssociateModule(CoreModule):
    """
    associate -- Associate amps in the database with the event, and write
                 XML data file to the event's current directory.
    """

    command_name = "associate"

    def __init__(self, eventid, process="shakemap", logger=None):
        """
        Instantiate an AssociateModule class with an event ID.
        """
        super(AssociateModule, self).__init__(eventid, logger=logger)
        self.process = process

    def execute(self, config=None, indir=None, outdir=None):
        """
        Associate amps and write unassoc_<datetime>_dat.xml.
        """
        if self.process == "shakemap":
            install_path, data_path = get_config_paths()
        else:
            install_path = os.path.dirname(config.rstrip("/"))
            data_path = os.path.join(outdir, "..", "..")

        amp_handler = AmplitudeHandler(install_path, data_path)

        event = amp_handler.getEvent(self._eventid)
        if event is None:
            #
            # This shouldn't ever happen, but the code is here just
            # in case it does
            #
            if self.process == "shakemap":
                datadir = os.path.join(data_path, self._eventid, "current")
            else:
                datadir = indir
            if not os.path.isdir(datadir):
                raise NotADirectoryError(f"{datadir} is not a valid directory.")
            eventxml = os.path.join(datadir, "event.xml")
            if not os.path.isfile(eventxml):
                raise FileNotFoundError(f"{eventxml} does not exist.")
            origin = read_event_file(eventxml)

            event = {
                "id": self._eventid,
                "netid": origin["netid"],
                "network": origin["network"],
                "time": origin["time"].strftime(constants.TIMEFMT),
                "lat": origin["lat"],
                "lon": origin["lon"],
                "depth": origin["depth"],
                "mag": origin["mag"],
                "locstring": origin["locstring"],
            }
            amp_handler.insertEvent(event)

        amp_handler.associateOne(self._eventid, pretty_print=True)


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Associate amps from the database with an event and write the XML input file.
    """
    evid, datadir, outdir, logdir, config, _ = get_module_args(description, True, True)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "shape.log")
    logger = get_generic_logger(logfile=logfile)

    mod = AssociateModule(evid, process="main", logger=logger)
    mod.execute(config=config, indir=datadir, outdir=outdir)


if __name__ == "__main__":
    main()
