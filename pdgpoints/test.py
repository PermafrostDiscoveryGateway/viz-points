from pathlib import Path

from .pipeline import Pipeline
from .defs import MOD_LOC

E = MOD_LOC.joinpath(MOD_LOC, 'testdata/lp_jumps_e.laz')
W = MOD_LOC.joinpath(MOD_LOC, 'testdata/lp_jumps_w.laz')

def test(f: list[Path]=[E, W],
         verbose: bool=True):
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
                     translate_z=-28.143, # geoid height at https://geodesy.noaa.gov/api/geoid/ght?lat=44.25&lon=-73.96
                     verbose=verbose)
        p.run()
        merge = True
