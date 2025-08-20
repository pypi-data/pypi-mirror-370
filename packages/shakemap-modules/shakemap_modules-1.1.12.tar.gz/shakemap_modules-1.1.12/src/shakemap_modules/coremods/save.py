import os

# local imports
from shakemap_modules.base.transfer_base import TransferBaseModule
from shakemap_modules.utils.logging import get_generic_logger
from shakemap_modules.base.cli import get_transfer_args


class SaveTransfer(TransferBaseModule):
    """
    save - Create backup directory and prep for next ShakeMap map version.
    """

    command_name = "save"
    dependencies = [("products/*", False)]

    def __init__(self, eventid, process="shakemap", logger=None):
        # call the parent constructor
        super(SaveTransfer, self).__init__(eventid, process=process, logger=logger)

    def execute(self, datadir=None, outdir=None, config=None):
        # Calling parent class execute method, which serves to
        # perform backup functionality for us.
        super(SaveTransfer, self).execute(datadir=datadir, outdir=outdir, config=config)


def main():
    os.environ["CALLED_FROM_MAIN"] = "True"

    description = """
    Save current products and rev version of event.
    """
    datadir, outdir, logdir, config, _ = get_transfer_args(description)

    if logdir is None:
        logfile = None
    else:
        logfile = os.path.join(logdir, "save.log")
    logger = get_generic_logger(logfile=logfile)

    mod = SaveTransfer("noid", process="main", logger=logger)
    mod.execute(datadir=datadir, outdir=outdir, config=config)


if __name__ == "__main__":
    main()
