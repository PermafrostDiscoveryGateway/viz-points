import os

from .pipeline import Pipeline
from .defs import MOD_LOC

E = os.path.join(MOD_LOC, 'testdata/lp_jumps_e.laz')
W = os.path.join(MOD_LOC, 'testdata/lp_jumps_w.laz')

def test(f=[E, W],
         verbose=True):
    merge = False
    for l in f:
        p = Pipeline(f=l,
                     intensity_to_RGB=True,
                     merge=merge,
                     archive=True,
                     verbose=verbose)
        p.run()
        merge = True
