import os
import sys
import getopt

from . import L
from . import defs
from .pipeline import Pipeline

def cli():
    '''
    Parse the command options and arguments.
    '''

    verbose, i_to_rgb, merge, archive = False, False, False, False
    try:
        opts = getopt.getopt(sys.argv[1:], 'hvcmas:f:',
            ['help', 'verbose', 'copy_I_to_RGB', 'merge', 'archive', 'rgb_scale=', 'file=']
            )[0]
    except Exception as e:
        L.error('%s: %s' % (repr(e), e))
    
    for o, a in opts:
        if o in ('-h', '--help'):
            print(defs.HELP_TXT)
            exit(0)
        verbose = True if o in ('-v', '--verbose') else verbose
        i_to_rgb = True if o in ('-c', '--copy_I_to_RGB') else i_to_rgb
        rgb_scale = float(a) if o in ('-s', '--rgb_scale') else False
        merge = True if o in ('-m', '--merge') else merge
        archive = True if o in ('-a', '--archive') else archive
        if o in ('-f', '--file'):
            if os.path.exists(a):
                f = a
            else:
                L.error('No file at %s' % (a))
                exit(1)

    p = Pipeline(f=f,
                 intensity_to_RGB=i_to_rgb,
                 merge=merge,
                 archive=archive,
                 rgb_scale=rgb_scale,
                 verbose=verbose)
    p.run()