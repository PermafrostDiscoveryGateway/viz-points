from pathlib import Path
import os
from logging import StreamHandler
from threading import Thread

from . import L
from . import utils
from . import lastools_iface
from . import py3dtiles_iface

class Pipeline(Thread):
    '''
    The LiDAR processing pipeline.
    Takes input point cloud files of any type supported by lastools
    and outputs 3dtiles files.

    Variables:
    :param f: The file to process
    :type f: str or pathlib.Path
    :param bool merge: Whether or not to merge with existing datasets in the output location (default: True)
    :return: Processed data location
    :rtype: str
    '''

    def __init__(self,
                 f,
                 merge: bool=True,
                 intensity_to_RGB: bool=False,
                 archive: bool=False,
                 verbose=True):
        '''
        Initialize the processing pipeline.
        '''
        super().__init__()
        global L
        L.propagate = verbose
        self.verbose = verbose
        self.L = L
        self.L.debug('Initializing pipeline.')
        self.f = Path(f)
        self.base_dir, self.bn = os.path.split(self.f)
        self.given_name, self.ext = os.path.splitext(self.bn)
        self.rewrite_dir = os.path.join(self.base_dir, 'rewrite')
        self.archive_dir = os.path.join(self.base_dir, 'archive')
        self.out_dir = os.path.join(self.base_dir, '3dtiles')
        self.las_name = os.path.join(self.rewrite_dir, '%s.las' % (self.given_name))
        self.intensity_to_RGB = intensity_to_RGB
        self.archive = archive
        self.merge = merge
        utils.log_init_stats(self)


    def run(self):
        '''
        Process the input LAS file.
        '''

        for d in [self.rewrite_dir, self.archive_dir, self.out_dir]:
            self.L.info('Creating dir %s' % (d))
            utils.make_dirs(d)

        lastools_iface.las2las(f=self.f,
                               output_file=self.las_name,
                               archive_dir=self.archive_dir,
                               intensity_to_RGB=self.intensity_to_RGB,
                               archive=self.archive,
                               verbose=self.verbose)
        
        py3dtiles_iface.tile(f=self.las_name,
                             out_dir=self.out_dir,
                             verbose=self.verbose)

        if self.merge:
            py3dtiles_iface.merge(dir=self.out_dir,
                                  overwrite=True,
                                  verbose=self.verbose)

        return str(self.out_dir)
