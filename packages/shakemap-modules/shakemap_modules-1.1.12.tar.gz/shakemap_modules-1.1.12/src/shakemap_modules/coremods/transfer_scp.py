# stdlib imports
import logging
import os.path

# third party imports

# local imports
from esi_utils_transfer.securesender import SecureSender
from shakemap_modules.base.transfer_base import TransferBaseModule
from shakemap_modules.utils.logging import get_generic_logger
from shakemap_modules.base.cli import get_transfer_args


class SCPTransfer(TransferBaseModule):
    """
    transfer_pdl - Transfer content via SCP to a remote server.
    """

    command_name = "transfer_scp"
    dependencies = [("products/*", False)]

    def __init__(self, eventid, cancel=False, process="shakemap", logger=None):
        # call the parent constructor
        super(SCPTransfer, self).__init__(
            eventid, cancel=cancel, process=process, logger=logger
        )

    def execute(self, datadir=None, outdir=None, config=None):
        # call parent execute() method
        # this will set the self.info and self.config
        # dictionaries, and self.datadir
        super(SCPTransfer, self).execute(datadir=datadir, outdir=outdir, config=config)

        # check to see if SCP is a configured method
        if "scp" not in self.config:
            logging.info("No SCP transfer has been configured. Returning.")
            return

        # get the properties needed for the sender
        properties, product_properties = self.getProperties(self.info)

        # get the products directory
        if self.process == "shakemap":
            product_dir = os.path.join(self.datadir, "products")
        else:
            product_dir = os.path.join(datadir, "products")

        # loop over all possible scp destinations, send products to
        # each one
        for destination, params in self.config["scp"].items():
            # append the event ID to the remote_directory
            pdir = params["remote_directory"]
            params["remote_directory"] = os.path.join(pdir, self._eventid)

            params.update(properties)
            fmt = f"Doing SCP transfer to {destination}..."
            logging.debug(fmt)

            sender = SecureSender(properties=params, local_directory=product_dir)
            if self.cancel:
                msg = sender.cancel()
            else:
                try:
                    nfiles, msg = sender.send()
                except Exception as e:
                    logging.warning(str(e))
                    raise (e)
                fmt = '%i files sent.  Message from sender: \n"%s"'
                tpl = (nfiles, msg)
                logging.info(fmt % tpl)


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    scp products to remote machines per configuration.
    """
    datadir, outdir, logdir, config, _ = get_transfer_args(description)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "transfer_scp.log")
    logger = get_generic_logger(logfile=logfile)

    mod = SCPTransfer("noid", cancel=False, process="main", logger=logger)
    mod.execute(datadir=datadir, outdir=outdir, config=config)


if __name__ == "__main__":
    main()
