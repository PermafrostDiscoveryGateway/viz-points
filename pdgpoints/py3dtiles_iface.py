import os
from py3dtiles import convert, merger
from py3dtiles.utils import str_to_CRS
from datetime import datetime

from . import L

def tile(f, out_dir, crs='4978', verbose=False):
    '''
    '''
    L.info('Starting tiling process for %s' % (f))
    tilestart = datetime.now()
    L.info('Creating tile directory')
    fndir = os.path.join(out_dir, os.path.splitext(os.path.basename(f))[0])
    CRSi = str_to_CRS('4326')
    CRSo = str_to_CRS(crs)
    #L.info('CRS to convert from: %s' % (CRSi))
    L.info('CRS to convert to:   %s' % (CRSo))

    converter = convert._Convert(files=f,
                                 outfolder=fndir,
                                 overwrite=True,
                                 #crs_in=CRSi,
                                 crs_out=CRSo,
                                 force_crs_in=True,
                                 rgb=True,
                                 benchmark=True)
    converter.convert()

    tiletime = (datetime.now() - tilestart).seconds/60
    L.info('Finished tiling (%.1f min)' % (tiletime))


def merge(dir, overwrite: bool=False, verbose=False):
    '''
    '''
    verbosity = 2 if verbose else 0
    L.info('Starting merge process in %s' % (dir))
    mergestart = datetime.now()

    merger.merge(folder=dir,
                 overwrite=overwrite,
                 verbose=verbosity)

    mergetime = (datetime.now() - mergestart).seconds/60
    L.info('Finished merge (%.1f min)' % (mergetime))
