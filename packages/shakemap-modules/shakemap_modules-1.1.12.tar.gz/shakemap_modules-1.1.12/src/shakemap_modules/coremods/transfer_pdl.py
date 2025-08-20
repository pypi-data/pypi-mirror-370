# stdlib imports
import logging
import os.path
import shutil

# third party imports

# local imports
from esi_utils_transfer.pdlsender import PDLSender
from shakemap_modules.base.transfer_base import TransferBaseModule
from shakemap_modules.utils.logging import get_generic_logger
from shakemap_modules.base.cli import get_transfer_args


class PDLTransfer(TransferBaseModule):
    """
    transfer_pdl - Transfer content via PDL to a remote server.
    """

    command_name = "transfer_pdl"
    dependencies = [("products/*", False)]

    def __init__(
        self, eventid, cancel=False, devconfig=False, process="shakemap", logger=None
    ):
        # call the parent constructor
        super(PDLTransfer, self).__init__(
            eventid, cancel=cancel, devconfig=devconfig, process=process, logger=logger
        )

    def execute(self, datadir=None, outdir=None, config=None):
        # call parent execute() method
        # this will set the self.info and self.config
        # dictionaries, and self.datadir
        super(PDLTransfer, self).execute(datadir=datadir, outdir=outdir, config=config)

        # check to see if PDL is a configured method
        if "pdl" not in self.config:
            logging.info("No PDL transfer has been configured. Returning.")
            return

        # do PDL specific stuff

        if self.process == "shakemap":
            products_dir = os.path.join(self.datadir, "products")
            pdl_dir = os.path.join(self.datadir, "pdl")
        else:
            products_dir = os.path.join(datadir, "products")
            pdl_dir = os.path.join(datadir, "pdl")
        if not os.path.isdir(pdl_dir):
            raise NotADirectoryError(f"{pdl_dir} does not exist.")

        # get the properties needed for the sender
        properties, product_properties = self.getProperties(self.info)

        downloads_dir = os.path.join(pdl_dir, "download")
        if os.path.isdir(downloads_dir):
            shutil.rmtree(downloads_dir, ignore_errors=True)
        shutil.copytree(products_dir, downloads_dir)

        # loop over all possible pdl destinations, send products to
        # each one
        for destination, params in self.config["pdl"].items():
            cmdline_args = {}
            if "cmdline_args" in params:
                cmdline_args = params["cmdline_args"].copy()
                del params["cmdline_args"]

            params.update(properties)

            if "properties" in params:
                product_properties.update(params["properties"])
                del params["properties"]

            if self.usedevconfig is True:
                if params["devconfig"] is None or not os.path.isfile(
                    params["devconfig"]
                ):
                    raise FileNotFoundError(
                        f"Dev config file \"{params['devconfig']}\" does not exist"
                    )
                # Swap the config file for the devconfig file
                params["configfile"] = params["devconfig"]
                fmt = f"Doing PDL transfer to {destination} DEV..."
                logging.debug(fmt)
            else:
                fmt = f"Doing PDL transfer to {destination}..."
                logging.debug(fmt)

            sender = PDLSender(
                properties=params,
                local_directory=pdl_dir,
                product_properties=product_properties,
                cmdline_args=cmdline_args,
            )
            logging.debug(f"Properties: {params}")
            logging.debug(f"Product Properties: {product_properties}")
            logging.debug(f"Cmdline Args: {cmdline_args}")
            if self.cancel:
                msg = sender.cancel()
            else:
                nfiles, msg = sender.send()
                fmt = '%i files sent.  Message from sender: \n"%s"'
                tpl = (nfiles, msg)
                logging.info(fmt % tpl)

        if not self.cancel:
            shutil.rmtree(downloads_dir, ignore_errors=True)


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Transfer products to PDL.
    """
    datadir, outdir, logdir, config, vargs = get_transfer_args(
        description,
        "--cancel",
        "-c",
        "store_true",
        "Cancel this event",
        "--devconfig",
        "-v",
        "store_true",
        "Send products to the PDL server configured in 'devconfig' rather than the "
        "default 'configfile'.",
    )

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "transfer_pdl.log")
    logger = get_generic_logger(logfile=logfile)

    mod = PDLTransfer(
        "noid",
        cancel=vargs["cancel"],
        devconfig=vargs["devconfig"],
        process="main",
        logger=logger,
    )
    mod.execute(datadir=datadir, outdir=outdir, config=config)


if __name__ == "__main__":
    main()
