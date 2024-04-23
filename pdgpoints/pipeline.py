from pathlib import Path
from typing import Union, Literal
from pyegt.defs import REGIONS
from logging import getLogger

from . import utils
from . import geoid
from . import lastools_iface
from . import py3dtiles_iface
from . import llvs2laz

class Pipeline():
    """
    The LiDAR processing pipeline.
    Takes input point cloud files of any type supported by lastools
    and outputs 3dtiles files.

    :param f: The LAS file to process
    :type f: str or pathlib.Path
    :param bool merge: Whether to use py3dtiles.merger.merge() to incorporate the processed dataset into an existing set of 3dtiles datasets
    :param bool intensity_to_RGB: Whether to copy intensity values to RGB (straight copy I->R I->G I->B, so will show up as greyscale)
    :param bool archive: Archive the input dataset to `./archive` directory
    :param bool verbose: Whether to log more messages
    """
    def __init__(self,
                 f: Path,
                 merge: bool=True,
                 intensity_to_RGB: bool=False,
                 rgb_scale: Union[float, int, Literal[False]]=False,
                 translate_z: Union[float, int, Literal[False]]=False,
                 from_geoid: Union[str, Literal[None]]=None,
                 geoid_region: str=REGIONS[0],
                 archive: bool=False,
                 llvs: Union[str, bool]=False):
        """
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
        """
        super().__init__()
        self.starttime = utils.timer()
        self.auto = False # if auto-processing
        self.L = getLogger(__name__)
        self.L.debug('Initializing pipeline.')
        self.set_paths(f)
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
        self.las_crs = None
        self.x = None
        self.y = None
        self.from_geoid = from_geoid
        self.geoid_region = geoid_region
        self.ellips_lkup = None
        self.geoid_adj = 0
        self.archive = archive
        self.llvs = False
        self.quantile = False
        if llvs:
            if llvs == True:
                self.llvs = True
                self.quantile = False
            elif (llvs.lower() in 'linear'):
                self.llvs = True
                self.quantile = False
            elif (llvs.lower() in 'quantile'):
                self.llvs = True
                self.quantile = True
            else:
                self.L.warning(f'Could not understand value given for LLVS CSV processing ({llvs}). Valid values are "linear" and "quantile".')
                self.llvs = False
        self.merge = merge
        self.steps = 4
        self.steps = self.steps + 1 if llvs else self.steps
        self.steps = self.steps + 1 if merge else self.steps
        self.steps = self.steps + 1 if from_geoid else self.steps
        self.step = 1
        utils.log_init_stats(self)

    def set_paths(self, f):
        """
        Set paths based on an input file ``f``.
        """
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

    def run(self) -> Path:
        """
        Process the input LAS file.

        :param self self:
        :return: The path of the output directory
        :rtype: pathlib.Path
        """
        L = getLogger(__name__)
        for d in [self.rewrite_dir, self.archive_dir, self.out_dir]:
            self.L.info('Creating dir %s' % (d))
            utils.make_dirs(d)

        if self.llvs:
            L.info('Converting CSV with LLVS format (lat, lon, displacement, stdev) to LAZ... (step %s of %s)' % (self.step, self.steps))
            self.f = llvs2laz.insar_pipeline(f=self.f, quantile=self.quantile)
            self.set_paths(self.f)

        L.info('Rewriting file with new OGC WKT... (step %s of %s)' % (self.step, self.steps))
        lastools_iface.las2las_ogc_wkt(f=self.f,
                                       output_file=self.ogcwkt_name)

        self.step += 1
        L.info('Doing lasinfo dump... (step %s of %s)' % (self.step, self.steps))
        self.las_crs, las_vrs, self.wkt, wktf, h_name, v_name = lastools_iface.lasinfo(f=self.ogcwkt_name)
        
        if self.from_geoid or las_vrs:
            L.info('self.from_geoid="%s", las_vrs="%s"' % (self.from_geoid, las_vrs))
            self.step += 1
            L.info('Getting mean lat/lon from las file... (step %s of %s)' % (self.step, self.steps))
            self.x, self.y, xyf = lastools_iface.lasmean(f=self.ogcwkt_name, name=h_name)
            self.lat, self.lon = geoid.crs_to_wgs84(x=self.x, y=self.y,
                                                    from_crs=self.las_crs)
            L.info('Resolving geoid/tidal model... (step %s of %s)' % (self.step, self.steps))
            self.from_geoid = geoid.use_model(user_vrs=self.from_geoid,
                                              las_vrs=las_vrs)
            L.info('Looking up ellipsoid height of %s at (%.3f, %.3f)... (step %s of %s)' % (self.from_geoid,
                                                                                             self.lat, self.lon,
                                                                                             self.step,
                                                                                             self.steps))
            self.ellips_lkup = geoid.get_adjustment(lat=self.lat,
                                                    lon=self.lon,
                                                    model=self.from_geoid,
                                                    region=self.geoid_region)
            self.geoid_adj = float(self.ellips_lkup)
            L.info('Manual Z transformation: %.3f' % (self.translate_z))
            L.info('Geoid height adjustment: %.3f' % (self.geoid_adj))
            if self.ellips_lkup:
                self.translate_z = self.translate_z + self.geoid_adj
                L.info('Translating Z values by %.3f' % (self.translate_z))
            else:
                raise LookupError('Could not get ellipsoid height of %s. Query URL: %s' % (self.from_geoid,
                                                                                           self.lat,
                                                                                           self.lon))

        self.step += 1
        L.info('Starting las2las rewrite... (step %s of %s)' % (self.step, self.steps))
        lastools_iface.las2las(f=self.ogcwkt_name,
                               output_file=self.las_name,
                               archive_dir=self.archive_dir,
                               intensity_to_RGB=self.intensity_to_RGB,
                               archive=self.archive,
                               rgb_scale=self.rgb_scale,
                               translate_z=self.translate_z)

        self.step += 1
        L.info('Starting tiling process... (step %s of %s)' % (self.step, self.steps))
        py3dtiles_iface.tile(f=self.las_name,
                             out_dir=self.out_dir,
                             las_crs=self.las_crs,
                             out_crs='4978')

        if self.merge:
            self.step += 1
            L.info('Starting merge process... (step %s of %s)' % (self.step, self.steps))
            py3dtiles_iface.merge(dir=self.out_dir,
                                  overwrite=True)

        L.info('Cleaning up processing artifacts.')
        files = [self.ogcwkt_name, wktf, xyf]
        if not self.archive:
            files.append(self.las_name)
        L.debug('Removing files: %s' % (files))
        utils.rm_files(files=files)

        s, m = utils.timer(self.starttime)
        L.info('Finished processing %s (%s sec / %.1f min)' % (self.bn, s, m))

        return self.out_dir
