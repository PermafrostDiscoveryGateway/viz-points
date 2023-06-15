from pathlib import Path
from typing import Union, Literal

from . import L
from . import defs
from . import utils
from . import geoid
from . import lastools_iface
from . import py3dtiles_iface

class Pipeline():
    '''
    The LiDAR processing pipeline.
    Takes input point cloud files of any type supported by lastools
    and outputs 3dtiles files.

    Variables:
    :param f: The LAS file to process
    :type f: str or pathlib.Path
    :param bool merge: Whether to use py3dtiles.merger.merge() to incorporate the processed dataset into an existing set of 3dtiles datasets
    :param bool intensity_to_RGB: Whether to copy intensity values to RGB (straight copy I->R I->G I->B, so will show up as greyscale)
    :param bool archive: Archive the input dataset to `./archive` directory
    :param bool verbose: Whether to log more messages
    '''

    def __init__(self,
                 f: Path,
                 merge: bool=True,
                 intensity_to_RGB: bool=False,
                 rgb_scale: Union[float, int, Literal[False]]=False,
                 translate_z: Union[float, int, Literal[False]]=False,
                 from_geoid: Union[str, Literal[None]]=None,
                 geoid_region: str=defs.REGIONS[0],
                 archive: bool=False,
                 verbose: bool=True):
        '''
        Initialize the processing pipeline.

        :param self self:
        :param f: The LAS file to process
        :type f: pathlib.Path
        :param bool merge: Whether to use py3dtiles.merger.merge() to incorporate the processed dataset into an existing set of 3dtiles datasets
        :param bool intensity_to_RGB: Whether to copy intensity values to RGB (straight copy I->R I->G I->B, so will show up as greyscale)
        :param rgb_scale: Scale multiplier for RGB values
        :type rgb_scale: float or int or False
        :param translate_z: Float translation for z values
        :type translate_z: float or int or False
        :param bool archive: Archive the input dataset to `./archive` directory
        :param bool verbose: Whether to log more messages
        '''
        super().__init__()
        global L
        self.starttime = utils.timer()
        if verbose:
            L.setLevel('DEBUG')
        L.propagate = verbose
        self.verbose = verbose
        self.L = L
        self.L.debug('Initializing pipeline.')
        self.f = Path(f).absolute()
        self.base_dir = self.f.parent.absolute()
        self.bn = self.f.name
        self.given_name = self.f.stem
        self.ext = self.f.suffix
        self.ogcwkt_name = self.base_dir / ('%s-wkt.laz' % (self.given_name))
        self.rewrite_dir = self.base_dir / 'rewrite'
        self.archive_dir = self.base_dir / 'archive'
        self.out_dir = self.base_dir / '3dtiles'
        self.las_name = self.rewrite_dir / ('%s.las' % (self.given_name))
        self.intensity_to_RGB = intensity_to_RGB
        try:
            self.rgb_scale = float(rgb_scale) if rgb_scale else 1.
        except ValueError:
            self.L.warning('Could not convert RGB scale value to float. Not scaling RGB values.')
            self.rgb_scale = 1.
        try:
            self.translate_z = float(translate_z) if translate_z else 0.
        except ValueError:
            self.L.warning('Could not convert Z-translation value to float. Not translating Z values.')
            self.translate_z = 0.
        self.from_geoid = from_geoid
        self.geoid_adj = 0
        self.geoid_region = geoid_region
        self.archive = archive
        self.merge = merge
        self.steps = 4
        self.steps = self.steps + 1 if merge else self.steps
        self.steps = self.steps + 1 if from_geoid else self.steps
        self.step = 1
        utils.log_init_stats(self)


    def run(self) -> Path:
        '''
        Process the input LAS file.

        Variables:
        :param self self:
        :return: The path of the output directory
        :rtype: pathlib.Path
        '''

        for d in [self.rewrite_dir, self.archive_dir, self.out_dir]:
            self.L.info('Creating dir %s' % (d))
            utils.make_dirs(d)

        L.info('Rewriting file with new OGC WKT... (step %s of %s)' % (self.step, self.steps))
        lastools_iface.las2las_ogc_wkt(f=self.f,
                                       output_file=self.ogcwkt_name,
                                       verbose=self.verbose)

        self.step += 1
        L.info('Doing lasinfo dump... (step %s of %s)' % (self.step, self.steps))
        las_crs, las_vrs, lat, lon, wkt, wktf = lastools_iface.lasinfo(f=self.ogcwkt_name,
                                              verbose=self.verbose)
        
        if self.from_geoid:
            self.step += 1
            L.info('Looking up %s to WGS84 conversion... (step %s of %s)' % (self.from_geoid, self.step, self.steps))
            geoid.adjustment(user_vrs=self.from_geoid,
                             las_vrs=las_vrs,
                             lat=lat, lon=lon,
                             region=self.geoid_region)

        self.step += 1
        L.info('Starting las2las rewrite... (step %s of %s)' % (self.step, self.steps))
        lastools_iface.las2las(f=self.ogcwkt_name,
                               output_file=self.las_name,
                               archive_dir=self.archive_dir,
                               intensity_to_RGB=self.intensity_to_RGB,
                               archive=self.archive,
                               rgb_scale=self.rgb_scale,
                               translate_z=self.translate_z,
                               verbose=self.verbose)

        self.step += 1
        L.info('Starting tiling process... (step %s of %s)' % (self.step, self.steps))
        py3dtiles_iface.tile(f=self.las_name,
                             out_dir=self.out_dir,
                             las_crs=las_crs,
                             out_crs='4978',
                             verbose=self.verbose)

        if self.merge:
            self.step += 1
            L.info('Starting merge process... (step %s of %s)' % (self.step, self.steps))
            py3dtiles_iface.merge(dir=self.out_dir,
                                  overwrite=True,
                                  verbose=self.verbose)

        L.info('Cleaning up processing artifacts.')
        files = [self.ogcwkt_name, wktf]
        if not self.archive:
            files.append(self.las_name)
        L.debug('Removing files: %s' % (files))
        utils.rm_files(files=files)

        s, m = utils.timer(self.starttime)
        L.info('Finished processing %s (%s sec / %.1f min)' % (self.bn, s, m))

        return str(self.out_dir)
