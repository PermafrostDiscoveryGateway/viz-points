from pathlib import Path
from ._version import __version__
from datetime import datetime

Y = datetime.now().year
HELP_TXT = '''
~~ pdgpoints version %s ~~
 Ian Nesbitt / NCEAS %s
''' % (__version__, Y)

MOD_LOC = Path(__file__).parent.absolute()
BIN_LOC = MOD_LOC.joinpath('bin')
LAS2LAS_LOC = BIN_LOC.joinpath('las2las')
LASINFO_LOC = BIN_LOC.joinpath('lasinfo')
