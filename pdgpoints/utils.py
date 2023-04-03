import os
import subprocess
from pathlib import Path
from datetime import datetime

from py3dtiles.tileset.utils import TileContentReader
from . import L

def make_dirs(d, exist_ok=True):
    '''
    Simple wrapper to create directory using os.makedirs().
    Included is a logging command.

    Variables:
    :param pathlib.Path d: The directory to create
    :param bool exist_ok: Whether to gracefully accept an existing directory (default: True)
    '''
    L.info('Creating dir %s' % (d))
    os.makedirs(d, exist_ok=exist_ok)


def merge(in_dir: Path, out_dir: Path):
    '''
    Merge the output 3dtiles files into a single dataset.

    Variables:
    :param pathlib.Path in_dir: The directory in which to look for files
    :param pathlib.Path out_dir: The directory in which to place output
    '''
    L.info('Starting merge process in %s (step 3 of 3)' % (out_dir))
    mergestart = datetime.now()
    subprocess.run([
        'py3dtiles',
        'merge',
        '--overwrite',
        '--verbose',
        out_dir
    ])
    mergetime = (datetime.now() - mergestart).seconds/60
    L.info('Finished merge (%.1f min)' % (mergetime))

def get_flist(base_dir):
    filename = '*.las'
    # To define each .las file within each subdir as a string representation with forward slashes, use as_posix()
    # ** represents that any subdir string can be present between the base_dir and the filename (not using this because we don't want to include subdirs)
    flist = [p.as_posix() for p in base_dir.glob('./' + filename)]
    L.info('File list: %s' % (flist))
    return flist

