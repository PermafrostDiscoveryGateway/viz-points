import os
from py3dtiles import convert, merger
from py3dtiles.utils import str_to_CRS
from datetime import datetime

from . import L

def tile(f, out_dir, las_crs, out_crs='4978', verbose=False):
    '''
    '''
    L.info('Starting tiling process for %s' % (f))
    tilestart = datetime.now()
    L.info('Creating tile directory')
    fndir = os.path.join(out_dir, os.path.splitext(os.path.basename(f))[0])
    CRSi = str_to_CRS(las_crs)
    CRSo = str_to_CRS(out_crs)
    L.info('CRS to convert from: %s' % (CRSi))
    L.info('CRS to convert to:   %s' % (CRSo))

    converter = convert._Convert(files=f,
                                 outfolder=fndir,
                                 overwrite=True,
                                 crs_in=CRSi,
                                 crs_out=CRSo,
                                 force_crs_in=True,
                                 rgb=True,
                                 benchmark=True,
                                 verbose=verbose)
    converter.convert()

    tiletime = (datetime.now() - tilestart).seconds
    L.info('Finished tiling (%s sec / %.1f min)' % (tiletime,tiletime/60))


def merge(dir, overwrite: bool=False, verbose=False):
    '''
    '''
    verbosity = 2 if verbose else 0
    L.info('Starting merge process in %s' % (dir))
    mergestart = datetime.now()

    try:
        merger.merge(folder=dir,
                     overwrite=overwrite,
                     verbose=verbosity)
    except ValueError as e:
        L.error('Got "%s" error from py3dtiles.merger.merge' % (repr(e)))
        L.warning('This likely means the merged tileset did not get created.')

    mergetime = (datetime.now() - mergestart).seconds
    L.info('Finished merge (%s sec / %.1f min)' % (mergetime,mergetime/60))
