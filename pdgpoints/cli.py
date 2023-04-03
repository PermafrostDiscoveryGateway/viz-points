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

    try:
        opts = getopt.getopt(sys.argv[1:], 'hmf:',
            ['help', 'merge', 'file=']
            )[0]
    except Exception as e:
        L.error('%s: %s' % (repr(e), e))
    
    for o, a in opts:
        if o in ('-h', '--help'):
            print(defs.HELP_TXT)
            exit(0)
        if o in ('-m', '--merge'):
            merge = True
        else:
            merge = False
        if o in ('-f', '--file'):
            if os.path.exists(a):
                f = a
            else:
                L.error('No file at %s' % (a))
                exit(1)

    Pipeline(f, merge)