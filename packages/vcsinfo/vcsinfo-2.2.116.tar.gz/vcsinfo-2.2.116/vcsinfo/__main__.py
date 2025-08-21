#!/usr/bin/env python3
"""
Copyright 2023 Adobe
All Rights Reserved.

NOTICE: Adobe permits you to use, modify, and distribute this file in accordance
with the terms of the Adobe license agreement accompanying it.
"""

import argparse
from collections import OrderedDict
import json
import logging
import os
import sys

# pylint: disable=W0406
import vcsinfo


PROC_NAME = "vcsinfo"
LOG_NAME = PROC_NAME


LOGLEVEL_NAMES = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOGLEVEL_LOOKUP = OrderedDict()
for _ll_name, _ll_val in zip(LOGLEVEL_NAMES, range(len(LOGLEVEL_NAMES))):
    LOGLEVEL_LOOKUP[str(_ll_val)] = _ll_name
    LOGLEVEL_LOOKUP[_ll_name] = _ll_name


def get_logger(loglevel):
    formatter = logging.Formatter("%(asctime)s %(name)-30s %(levelname)-8s %(message)s")
    logger = logging.getLogger(LOG_NAME)
    logger.setLevel(loglevel)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def loglevel_type(string):
    ll_name = string.upper()
    if ll_name not in LOGLEVEL_LOOKUP:
        llevel_values = ", ".join(LOGLEVEL_LOOKUP.keys())
        raise argparse.ArgumentTypeError(
            f'Value "{string}" is not a valid loglevel: {llevel_values}'
        )
    return LOGLEVEL_LOOKUP[ll_name]


def parse_args(argv):
    """
    Setup command line argument parsing and help.
    """
    parser = argparse.ArgumentParser(
        # pylint: disable=C0301
        description="vcsinfo returns version control information for the given directory"
    )

    llevel_values = ", ".join(LOGLEVEL_LOOKUP.keys())
    parser.add_argument(
        "-l",
        "--loglevel",
        dest="loglevel",
        help=f"Verbosity of output:  Allowed values are {llevel_values}",
        type=loglevel_type,
        default="WARNING",
    )

    parser.add_argument(
        "-d",
        "--directory",
        default=os.getcwd(),
        dest="directory",
        # pylint: disable=C0301
        help="directory to get info for (defaults to current working directory)",
    )

    parser.add_argument(
        "-f",
        "--file-info",
        action="store_true",
        default=False,
        dest="include_files",
        help="include detailed file information",
    )

    return parser.parse_args(argv)


def main(argv=None):
    """
    Gets version control information for the given directory and outputs as a
    JSON document.
    """
    if argv is None:
        argv = sys.argv
    args = parse_args(argv[1:])
    logger = get_logger(args.loglevel)
    logger.debug("Startup")

    # pylint: disable=I1101
    vcs = vcsinfo.detect_vcs(args.directory)
    print(
        json.dumps(
            vcs.info(include_files=args.include_files),
            sort_keys=True,
            indent=2,
        )
    )

    return os.EX_OK


if "__main__" == __name__:
    sys.exit(main(sys.argv))


# Local Variables:
# fill-column: 100
# End:
