#!/usr/bin/env python3
"""Bochord cli arg parsing."""

import argparse
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from bochord.bochord import run

ICLOUD_BOOK_DIR = "Library/Mobile Documents/iCloud~com~apple~iBooks/Documents"
PROGRAM_NAME = "bochord"

try:
    __version__ = version(PROGRAM_NAME)
except PackageNotFoundError:
    __version__ = "test"


def get_arguments():
    """Get arguments with argparser."""
    usage = "%(prog)s [options] <backup_path>"
    desc = "Backup books from macOS Books to usable ePubs"
    source_default = Path.home() / ICLOUD_BOOK_DIR
    parser = argparse.ArgumentParser(usage=usage, description=desc)
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="force",
        default=0,
        help="force re-archive even if no file updates",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=0,
        help="be verbose",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-p",
        "--prune",
        action="store_true",
        dest="prune",
        default=0,
        help="prune documents from destination if missing from source.",
    )
    parser.add_argument(
        "-s",
        "--source",
        action="store",
        dest="source",
        type=Path,
        default=source_default,
        help="source directory (default: %(default)s)",
    )
    parser.add_argument(
        "dest",
        metavar="backup_path",
        type=Path,
        help="backup destination path",
        default=None,
    )

    return parser.parse_args()


def main():
    """Get cli arguments and run bochord."""
    args = get_arguments()
    run(args)
