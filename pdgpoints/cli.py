from pathlib import Path
import argparse

from . import L
from . import defs
from .pipeline import Pipeline

def cli():
    """
    Parse the command options and arguments.
    """
    parser = argparse.ArgumentParser(prog='pdgpoints', description='Convert LiDAR files (LAS, LAZ) to Cesium tilesets.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Whether to log more messages')
    parser.add_argument('-c', '--copy_I_to_RGB', action='store_true', help='Whether to copy intensity values to RGB')
    parser.add_argument('-m', '--merge', action='store_true', help='Whether to use merge function')
    parser.add_argument('-a', '--archive', action='store_true', help='Whether to archive the input dataset')
    parser.add_argument('-s', '--rgb_scale', type=float, default=1.0, help='Scale multiplier for RGB values')
    parser.add_argument('-z', '--translate_z', type=float, default=0.0, help='Float translation for z values')
    parser.add_argument('-g', '--from_geoid', choices=defs.MODEL_LIST, default=None, help='The geoid, tidal, or geopotential model to translate from')
    parser.add_argument('-r', '--geoid_region', choices=defs.REGIONS, default=defs.REGIONS[0], help='The NGS region (https://vdatum.noaa.gov/docs/services.html#step140)')
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
                 from_vdatum=args.from_vdatum,
                 geoid_region=args.geoid_region,
                 verbose=args.verbose)
    p.run()