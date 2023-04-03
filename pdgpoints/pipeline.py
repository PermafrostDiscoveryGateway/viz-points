from pathlib import Path
import getopt
import os
import sys

from . import L
from . import utils
from . import lastools_iface
from . import defs

def process(f, merge: bool=True):
    '''
    Process the input LAS file.

    Variables:
    :param f: The file to process
    :type f: str or pathlib.Path
    :param bool merge: Whether or not to merge with existing datasets in the output location (default: True)
    :return: Processed data location
    :rtype: str
    '''
    f = Path(f)
    base_dir = os.path.split(f)
    vlrcorrect_dir = os.path.join(base_dir, 'vlrcorrect')
    archive_dir = os.path.join(base_dir, 'archive')
    out_dir = os.path.join(base_dir, '3dtiles')

    for d in [vlrcorrect_dir, archive_dir, out_dir]:
        L.info('Creating dir %s' % (d))
        utils.make_dirs(d)

    flist = utils.get_flist()

    lastools_iface.las2las(flist,
                           vlrcorrect_dir,
                           archive_dir=archive_dir,
                           archive=True)
    

    if merge:
        utils.merge(in_dir=vlrcorrect_dir, out_dir=out_dir)
    return str(out_dir)

def cli():
    '''
    Parse the command options and arguments.
    '''

    try:
        opts = getopt.getopt(sys.argv[1:], 'hf:',
            ['help', 'file=',]
            )[0]
    except Exception as e:
        L.error('%s: %s' % (repr(e), e))
    
    for o, a in opts:
        if o in ('-h', '--help'):
            print(defs.HELP_TXT)
            exit(0)
        if o in ('-f', '--file'):
            if os.path.exists(a):
                f = a
            else:
                L.error('No file at %s' % (a))
                exit(1)
    process(f)