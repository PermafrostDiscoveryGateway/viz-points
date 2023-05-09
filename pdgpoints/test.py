import os

from .pipeline import Pipeline
from .defs import MOD_LOC

E = os.path.join(MOD_LOC, 'testdata/lp_jumps_e.laz')
W = os.path.join(MOD_LOC, 'testdata/lp_jumps_w.laz')

def test(f=[E, W],
         verbose=True):
    '''
    Run both halves of the test dataset through the library to test functionality.

    Variables:
    :param list f: Two halves of the test dataset to be processed
    :param bool verbose: Whether to log more messages
    '''
    merge = False
    for l in f:
        p = Pipeline(f=l,
                     intensity_to_RGB=True,
                     merge=merge,
                     archive=True,
                     rgb_scale=2.0,
                     verbose=verbose)
        p.run()
        merge = True
