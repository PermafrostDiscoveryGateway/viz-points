import os
import glob
from pathlib import Path
from py3dtiles import convert, merger
from py3dtiles.utils import str_to_CRS
from datetime import datetime

from . import L

def log_tileset_error(e):
    '''
    '''
    L.error('Got "%s" error from py3dtiles.merger.merge' % (repr(e)))
    L.warning('The above error means that there was only one tileset directory '
              'in the output folder. The merged tileset could not be created.'
              'Add another tileset to allow the merge to work.')

def rm_file(f):
    '''
    '''
    try:
        L.info('Cleaning up previous merge artifact %s' % (f))
        Path(f).unlink(missing_ok=True)
    except FileNotFoundError as e:
        L.warning('FileNotFoundError caught when deleting %s. This might mean nothing.' % (f))

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
    L.info('Starting merge process in %s' % (dir))
    mergestart = datetime.now()

    paths = [Path(path) for path in glob.glob(os.path.join(dir, '*', 'tileset.json'))]
    ts_path = Path(os.path.join(dir, 'tileset.json'))
    r_path = Path(os.path.join(dir, 'r.pnts'))

    if overwrite:
        for f in [ts_path, r_path]:
            rm_file(f)

    try:
        merger.merge_from_files(tileset_paths=paths,
                                output_tileset_path=ts_path,
                                overwrite=overwrite,
                                force_universal_merger=True)
    except ValueError as e:
        log_tileset_error(e)
    except RuntimeError as e:
        log_tileset_error(e)

    mergetime = (datetime.now() - mergestart).seconds
    L.info('Finished merge (%s sec / %.1f min)' % (mergetime,mergetime/60))
