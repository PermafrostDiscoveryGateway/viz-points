import os
from py3dtiles.tileset.utils import TileContentReader
from datetime import datetime, timedelta

from . import L

def tile(f, out_dir):
    L.info('Starting tiling process for %s' % (f))
    tilestart = datetime.now()
    L.info('Creating tile directory')
    fndir = os.path.join(out_dir, os.path.splitext(os.path.basename(f))[0])

    # processing happens

    tiletime = (datetime.now() - tilestart).seconds/60
    L.info('Finished tiling (%.1f min)' % (tiletime))


def merge(dir):
    L.info('Starting merge process in %s' % (dir))
    mergestart = datetime.now()

    # processing happens

    mergetime = (datetime.now() - mergestart).seconds/60
    L.info('Finished merge (%.1f min)' % (mergetime))
