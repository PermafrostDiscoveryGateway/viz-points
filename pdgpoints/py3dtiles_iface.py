import os
from py3dtiles import convert, merger
from datetime import datetime, timedelta

from . import L

def tile(f, out_dir):
    '''
    '''
    L.info('Starting tiling process for %s' % (f))
    tilestart = datetime.now()
    L.info('Creating tile directory')
    fndir = os.path.join(out_dir, os.path.splitext(os.path.basename(f))[0])

    converter = convert._Convert(files=f,
                                 outfolder=out_dir,
                                 overwrite=True,
                                 benchmark=True)
    converter.convert()

    tiletime = (datetime.now() - tilestart).seconds/60
    L.info('Finished tiling (%.1f min)' % (tiletime))


def merge(dir, overwrite: bool=False):
    '''
    '''
    L.info('Starting merge process in %s' % (dir))
    mergestart = datetime.now()

    merger.merge(folder=dir,
                 overwrite=overwrite,
                 verbose=1)

    mergetime = (datetime.now() - mergestart).seconds/60
    L.info('Finished merge (%.1f min)' % (mergetime))
