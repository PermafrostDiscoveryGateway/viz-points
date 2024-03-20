from pathlib import Path
import argparse
from pyegt.defs import MODEL_LIST, REGIONS

import logging as L
from .pipeline import Pipeline

def cli():
    """
    Parse the command options and arguments.
    """
    parser = argparse.ArgumentParser(prog='pdgpoints', description='Convert LiDAR files (LAS, LAZ) to Cesium tilesets.')
    parser.add_argument('-c', '--copy_i_to_rgb', action='store_true', help='Whether to copy intensity values to RGB')
    parser.add_argument('-m', '--merge', action='store_true', help='Whether to use merge function')
    parser.add_argument('-a', '--archive', action='store_true', help='Whether to archive the input dataset')
    parser.add_argument('-s', '--rgb_scale', type=float, default=1.0, help='Scale multiplier for RGB values')
    parser.add_argument('-z', '--translate_z', type=float, default=0.0, help='Float translation for z values')
    parser.add_argument('-g', '--from_geoid', choices=MODEL_LIST, default=None, help='The geoid, tidal, or geopotential model to translate from')
    parser.add_argument('-r', '--geoid_region', choices=REGIONS, default=REGIONS[0], help='The NGS region (https://vdatum.noaa.gov/docs/services.html#step140)')
    parser.add_argument('-f', '--file', type=str, required=True, help='The file to process')

    args = parser.parse_args()
    p = Path(args.file)
    if not p.is_file():
        L.error('No file at %s' % (p))
        exit(1)

    p = Pipeline(f=args.file,
                 intensity_to_RGB=args.copy_i_to_rgb,
                 merge=args.merge,
                 archive=args.archive,
                 rgb_scale=args.rgb_scale,
                 translate_z=args.translate_z,
                 from_geoid=args.from_geoid,
                 geoid_region=args.geoid_region)
    p.run()