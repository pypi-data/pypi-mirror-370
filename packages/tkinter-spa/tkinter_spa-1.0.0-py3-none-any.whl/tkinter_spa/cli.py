import argparse
import sys

from tkinter_spa._version import __version__


def main_cli():
    parser = argparse.ArgumentParser(
        prog = 'tkinter_spa',
        description = 'Tkinter (as a) Single Page Application'
    )
    parser.add_argument(
        '-v', '--version',
        action = 'version',
        version = f'%(prog)s {__version__}',
        help = 'print the version of tkinter_spa and exit'
    )

    parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
