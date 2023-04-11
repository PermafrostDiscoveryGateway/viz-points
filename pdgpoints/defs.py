import os
from ._version import __version__
from datetime import datetime

Y = datetime.now().year
HELP_TXT = '''
~~ pdgpoints version %s ~~
 Ian Nesbitt / NCEAS %s
Usage:
tilepoints [ OPTIONS ] -f /path/to/file.las
where OPTIONS := {
    -h | --help
            display this help message
    -v | --verbose
            display more informational messages
    -c | --copy_I_to_RGB
            copy intensity values to RGB channels
    -m | --merge
            merge all tilesets in the output folder (./3dtiles)
    -a | --archive
            copy original LAS files to a ./archive folder
} REQUIRED ARG := {
    -f | --file=/path/to/file.las
            specify the path to a LAS or LAZ point cloud file
}
''' % (__version__, Y)

MOD_LOC = os.path.dirname(os.path.abspath(__file__))
BIN_LOC = os.path.join(MOD_LOC, 'bin')
LAS2LAS_LOC = os.path.join(BIN_LOC, 'las2las')
LASINFO_LOC = os.path.join(BIN_LOC, 'lasinfo')
