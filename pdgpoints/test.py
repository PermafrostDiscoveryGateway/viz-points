from .pipeline import Pipeline

def test(f=['pdgpoints/testdata/lp_jumps_e.laz',
            'pdgpoints/testdata/lp_jumps_w.laz'],
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
