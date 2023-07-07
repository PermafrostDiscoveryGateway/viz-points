import glob
from pathlib import Path
from typing import Union
from py3dtiles import convert, merger
from py3dtiles.utils import str_to_CRS
from logging import getLogger

from . import utils

def log_tileset_error(e: Union[ValueError, RuntimeError]):
    """
    Log the error py3dtiles throws when the user tries to merge a single dataset.

    Variables:
    :param e: Error object
    :type e: ValueError or RuntimeError
    """
    L = getLogger(__name__)
    L.error('Got "%s" error from py3dtiles.merger.merge' % (repr(e)))
    L.warning('The above error means that there was only one tileset directory '
              'in the output folder. The merged tileset could not be created. '
              'Add another tileset to allow the merge to work.')

def rm_file(f: Path):
    """
    Remove a file.

    Variables:
    :param f: File to remove
    :type f: pathlib.Path
    """
    L = getLogger(__name__)
    try:
        L.info('Cleaning up previous merge artifact %s' % (f))
        f.unlink()
    except FileNotFoundError as e:
        L.warning('FileNotFoundError caught when deleting %s. This might mean nothing.' % (f))

def tile(f: Path,
         out_dir: Path,
         las_crs: str,
         out_crs: str='4978'):
    """
    Use py3dtiles.converter.convert() to create 3dtiles from a LAS or LAZ file.

    Variables:
    :param f: LAS or LAZ file to convert to 3dtiles
    :type f: pathlib.Path
    :param out_dir: The output directory to store 3dtiles subdirectory in
    :type out_dir: pathlib.Path
    :param str las_crs: Coordinate reference system (CRS) of the input LAS file
    :param str out_crs: CRS of the output tileset
    :param bool verbose: Whether to log more messages
    """
    L = getLogger(__name__)
    tilestart = utils.timer()
    L.info('File: %s' % (f))
    L.info('Creating tile directory')
    fndir = out_dir / f.stem
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
                                 verbose=False)
    converter.convert()

    L.info('Finished tiling (%s sec / %.1f min)' % utils.timer(tilestart))


def merge(dir: Path,
          overwrite: bool=False):
    """
    Use py3dtiles.merger.merge() to merge more than one 3dtiles dataset.
    This function will search for `tileset.json` files in subdirectories
    of the input directory (e.g. `input_dir/ds1/tileset.json`,
    `input_dir/ds2/tileset.json`)

    Variables:
    :param dir: Directory to search for tileset subdirectories in
    :type dir: pathlib.Path
    :param bool overwrite: Whether to overwrite existing mergers in the output directory (default: False)
    :param bool verbose: Whether to log more messages
    """
    L = getLogger(__name__)
    L.info('Output dir: %s' % dir)
    mergestart = utils.timer()

    paths = [Path(path) for path in glob.glob(str(dir.joinpath('*', 'tileset.json')))]
    ts_path = Path(dir.joinpath('tileset.json'))
    r_path = Path(dir.joinpath('r.pnts'))

    if overwrite:
        for f in [ts_path, r_path]:
            if f.is_file():
                rm_file(f)

    try:
        merger.merge_from_files(tileset_paths=paths,
                                output_tileset_path=ts_path,
                                overwrite=overwrite,
                                force_universal_merger=True)
    except (RuntimeError, ValueError) as e:
        log_tileset_error(e)

    L.info('Finished merge (%s sec / %.1f min)' % utils.timer(mergestart))
