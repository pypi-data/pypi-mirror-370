# stdlib imports
import logging
import os.path
from datetime import datetime
import configobj

# third party imports

# local imports
from esi_utils_transfer.emailsender import EmailSender
from shakemap_modules.base.transfer_base import TransferBaseModule
from shakemap_modules.utils.macros import get_macros
from shakemap_modules.utils.logging import get_generic_logger
from shakemap_modules.base.cli import get_transfer_args


class EmailTransfer(TransferBaseModule):
    """
    transfer_email - Transfer content via Email.
    """

    command_name = "transfer_email"
    dependencies = [("products/*", False)]

    def __init__(self, eventid, cancel=False, process="shakemap", logger=None):
        # call the parent constructor
        super(EmailTransfer, self).__init__(
            eventid, cancel=cancel, process=process, logger=logger
        )

    def execute(self, datadir=None, outdir=None, config=None):
        # call parent execute() method
        # this will set the self.info and self.config
        # dictionaries, and self.datadir
        super(EmailTransfer, self).execute(
            datadir=datadir, outdir=outdir, config=config
        )

        # check to see if email is a configured method
        if "email" not in self.config:
            logging.info("No email transfer has been configured. Returning.")
            return

        # see what the user set for the mail_once setting for all destinations
        mail_once = self.config["email"]["mail_once"]

        # then check for the mail flag file
        mailfile = os.path.join(self.datadir, ".mailed")
        if os.path.isfile(mailfile) and not self.cancel:
            msg = "Mail has already been generated for this event. Returning."
            logging.info(msg)
            return

        # get the properties needed for the sender
        properties, product_properties = self.getProperties(self.info)

        # get the products directory path
        if self.process == "shakemap":
            product_dir = os.path.join(self.datadir, "products")
        else:
            product_dir = os.path.join(datadir, "products")

        # get the macros that may be in the email sender config
        macros = get_macros(self.info)

        # loop over all possible email destinations, send products to
        # each one
        for destination, params in self.config["email"].items():
            if not isinstance(params, configobj.Section):
                continue
            params.update(properties)
            fmt = f"Doing email transfer to {destination}..."
            logging.debug(fmt)

            # replace macro strings with actual strings
            for pkey, param in params.items():
                for macro, replacement in macros.items():
                    if isinstance(param, str):
                        try:
                            param = param.replace(f"[{macro}]", replacement)
                            params[pkey] = param
                        except Exception as e:
                            pass

            # get full path to all file attachments
            attachments = []
            for lfile in params["attachments"]:
                fullfile = os.path.join(product_dir, lfile)
                if not os.path.isfile(fullfile):
                    logging.warn(f"{fullfile} does not exist.")
                attachments.append(fullfile)

            sender = EmailSender(properties=params, local_files=attachments)
            if self.cancel:
                msg = sender.cancel()
            else:
                try:
                    nfiles, msg = sender.send()
                    with open(mailfile, "wt") as f:
                        f.write(f"Mailed at {str(datetime.utcnow())} UTC")
                except Exception as e:
                    logging.warning(str(e))
                    raise (e)
                fmt = '%i files sent.  Message from sender: \n"%s"'
                tpl = (nfiles, msg)
                logging.info(fmt % tpl)


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Send an email to configured users.
    """
    datadir, outdir, logdir, config, _ = get_transfer_args(description)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "transfer_email.log")
    logger = get_generic_logger(logfile=logfile)

    mod = EmailTransfer("noid", cancel=False, process="main", logger=logger)
    mod.execute(datadir=datadir, outdir=outdir, config=config)


if __name__ == "__main__":
    main()
