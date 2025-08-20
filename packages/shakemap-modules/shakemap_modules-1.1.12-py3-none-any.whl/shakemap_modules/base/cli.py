# stdlib imports
import argparse
import os
import os.path
import sys

# third party imports

# local imports


def get_cli_args(description, config=False):
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Path to the shake_result.hdf file. If none is specified, the current "
        "directory will be searched.",
        default="./shake_result.hdf",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        help="Directory in which to place the output files. If none is given, the "
        "current directory will be used.",
        default=".",
    )
    parser.add_argument(
        "-l",
        "--logdir",
        help="Path to directory in which logfile(s) will be written. If none is given, "
        "output will be written to the terminal.",
        default=None,
    )
    if config is True:
        parser.add_argument(
            "-n",
            "--config",
            help="Path to the config file(s). If unspecified, the current directory "
            "will be searched for configuration files.",
            default=".",
        )
    args = parser.parse_args()

    if args.file is None:
        datafile = "./shake_result.hdf"
        if not os.path.isfile(datafile):
            print("")
            print("No shake_results.hdf file found in the current directory.")
            print(
                "Use the --file argument to specify a path to a shake_results.hdf file."
            )
            print("")
            parser.print_help()
            sys.exit(1)
    elif os.path.isdir(args.file):
        datafile = os.path.join(args.file, "shake_result.hdf")
        if not os.path.isfile(datafile):
            print("")
            print(f"No shake_results.hdf file found in {args.file}.")
            print("")
            parser.print_help()
            sys.exit(1)
    elif not os.path.isfile(args.file):
        print("")
        print(f"No file at {args.file}.")
        print("")
        parser.print_help()
        sys.exit(1)
    else:
        datafile = args.file
    if args.outdir is None:
        outdir = "."
    elif not os.path.isdir(args.outdir):
        print("")
        print("The --outdir argument must be a valid directory.")
        print("")
        parser.print_help()
        sys.exit(1)
    else:
        outdir = args.outdir
    if args.logdir is None or not os.path.isdir(args.logdir):
        print("")
        print("The --logdir argument must be a valid directory.")
        print("")
        parser.print_help()
        sys.exit(1)
    else:
        logdir = args.logdir
    if config is True:
        if args.config is None:
            config = os.path.abspath(".")
        elif not os.path.isdir(args.config):
            print("")
            print("The --config argument must be the path to a config file.")
            print("")
            parser.print_help()
            sys.exit(1)
        else:
            config = os.path.abspath(args.config)
    else:
        config = None

    return (
        os.path.abspath(datafile),
        os.path.abspath(outdir),
        os.path.abspath(logdir),
        config,
    )


def get_transfer_args(description, *varargs):
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--datadir",
        help="Path to the directory containing the 'products' directory for the "
        "event. If none is specified, the current directory will be searched.",
        default=".",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        help="Path where the backup directory will be written. "
        "If none is specified, no backup will be created.",
        default=None,
    )
    parser.add_argument(
        "-l",
        "--logdir",
        help="Path to directory in which logfile(s) will be written. If none is given, "
        "output will be written to the terminal.",
        default=None,
    )
    parser.add_argument(
        "-n",
        "--config",
        help="Path to the transfer.conf config file. If unspecified, the current "
        "directory will be searched.",
        default="./transfer.conf",
    )
    nvar = len(varargs)
    if nvar % 4 != 0:
        raise ValueError("Varargs must be: long-flag, short-flag, action, help")
    varlist = []
    varact = []
    for i in range(0, nvar, 4):
        if varargs[i + 2] == "store_true":
            parser.add_argument(
                varargs[i],
                varargs[i + 1],
                action=varargs[i + 2],
                help=varargs[i + 3],
            )
        else:
            parser.add_argument(
                varargs[i],
                varargs[i + 1],
                help=varargs[i + 3],
            )
        varg = varargs[i].replace("--", "")
        varlist.append(varg)
        varact.append(varargs[i + 2])
    args = parser.parse_args()

    datadir = os.path.join(args.datadir, "products")
    if not os.path.isdir(datadir):
        print("")
        print(f"No 'products' directory found in '{args.datadir}'.")
        print("Use the --datadir argument to specify a path to a products directory.")
        print("")
        parser.print_help()
        sys.exit(1)
    else:
        datadir = args.datadir

    if args.outdir is None or not os.path.isdir(args.outdir):
        print("")
        print("The --outdir argument must be a valid directory.")
        print("")
        parser.print_help()
        sys.exit(1)
    else:
        outdir = args.outdir

    if args.logdir is None or not os.path.isdir(args.logdir):
        print("")
        print("The --logdir argument must be a valid directory.")
        print("")
        parser.print_help()
        sys.exit(1)
    else:
        logdir = args.logdir

    if not os.path.isfile(args.config):
        print("")
        print(
            "Use the --config argument to specify the path to a 'transfer.conf' "
            "config file."
        )
        print("")
        parser.print_help()
        sys.exit(1)

    if nvar == 0:
        vdict = {}
    else:
        vdict = args.__dict__
    return (
        os.path.abspath(datadir),
        os.path.abspath(outdir),
        os.path.abspath(logdir),
        os.path.abspath(args.config),
        vdict,
    )


def get_module_args(description, get_datadir=True, get_config=True, *varargs):
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    if get_datadir is True:
        parser.add_argument(
            "-d",
            "--datadir",
            help="Path to the directory containing the input files for the "
            "event. If none is specified, the current directory will be searched.",
            default=".",
        )
    parser.add_argument(
        "evid",
        help="Event ID of the event being processed.",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        help="Path where the output will be written. If none is specified, the current "
        "directory will be used.",
        default=".",
    )
    parser.add_argument(
        "-l",
        "--logdir",
        help="Path to directory in which logfile(s) will be written. If none is given, "
        "output will be written to the terminal.",
        default=None,
    )
    if get_config is True:
        parser.add_argument(
            "-n",
            "--config",
            help="Path to the module's config file(s). If unspecified, the current "
            "directory will be searched.",
            default="./model.conf",
        )
    nvar = len(varargs)
    if nvar % 4 != 0:
        raise ValueError("Varargs must be: long-flag, short-flag, action, help")
    varlist = []
    varact = []
    for i in range(0, nvar, 4):
        if varargs[i + 2] == "store_true":
            parser.add_argument(
                varargs[i],
                varargs[i + 1],
                action=varargs[i + 2],
                help=varargs[i + 3],
            )
        else:
            parser.add_argument(
                varargs[i],
                varargs[i + 1],
                help=varargs[i + 3],
            )
        varg = varargs[i].replace("--", "")
        varlist.append(varg)
        varact.append(varargs[i + 2])
    args = parser.parse_args()

    if get_datadir is True:
        if not os.path.isdir(args.datadir):
            print("")
            print("Use the --datadir argument to specify a path to a data directory.")
            print("")
            parser.print_help()
            sys.exit(1)
        else:
            datadir = os.path.abspath(args.datadir)
    else:
        datadir = None

    if args.outdir is None or not os.path.isdir(args.outdir):
        print("")
        print("The --outdir argument must be a valid directory.")
        print("")
        parser.print_help()
        sys.exit(1)
    else:
        outdir = args.outdir

    if args.logdir is None or not os.path.isdir(args.logdir):
        print("")
        print("The --logdir argument must be a valid directory.")
        print("")
        parser.print_help()
        sys.exit(1)
    else:
        logdir = args.logdir

    if get_config is True:
        if not os.path.isfile(args.config) and not os.path.isdir(args.config):
            print("")
            print(
                "Use the --config argument to specify the path to a "
                "config file or files."
            )
            print("")
            parser.print_help()
            sys.exit(1)
        else:
            config = os.path.abspath(args.config)
    else:
        config = None

    if nvar == 0:
        vdict = {}
    else:
        vdict = args.__dict__
    return (
        args.evid,
        datadir,
        os.path.abspath(outdir),
        os.path.abspath(logdir),
        config,
        vdict,
    )
