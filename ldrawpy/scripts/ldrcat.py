#!/usr/bin/env python3

import math, os.path
import sys
import argparse

from ldrawpy import *


def main():
    parser = argparse.ArgumentParser(
        description="Display the contents of a LDraw file.",
    )
    parser.add_argument(
        "filename", metavar="filename", type=str, nargs="?", help="LDraw filename"
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        default=False,
        help="Clean up coordinate values",
    )
    parser.add_argument(
        "-n",
        "--nocolour",
        action="store_true",
        default=False,
        help="Do not show file with colour syntax highlighting",
    )
    parser.add_argument(
        "-l",
        "--lineno",
        action="store_true",
        default=False,
        help="Show line numbers",
    )
    args = parser.parse_args()
    argsd = vars(args)

    if len(argsd) < 1 or "filename" not in argsd or argsd["filename"] is None:
        parser.print_help()
        exit()
    if argsd["clean"]:
        lines = clean_file(argsd["filename"], as_str=True)
    else:
        with open(argsd["filename"], "r") as f:
            lines = f.readlines()
    for i, line in enumerate(lines):
        lineno = (i + 1) if argsd["lineno"] else None
        pprint_line(line, lineno, nocolour=argsd["nocolour"])


if __name__ == "__main__":
    main()
