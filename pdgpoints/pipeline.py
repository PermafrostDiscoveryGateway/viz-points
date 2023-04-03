from pathlib import Path
import os
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

    def __init__(self, f, merge: bool=True):
        '''
        Initialize the processing pipeline.
        '''
        L.info('Initializing pipeline.')
        self.f = Path(f)
        self.base_dir, self.bn = os.path.split(self.f)
        self.given_name, self.ext = os.path.splitext(self.bn)
        self.vlrcorrect_dir = os.path.join(self.base_dir, 'vlrcorrect')
        self.archive_dir = os.path.join(self.base_dir, 'archive')
        self.out_dir = os.path.join(self.base_dir, '3dtiles')
        self.las_name = os.path.join(self.vlrcorrect_dir, '%s.las' % (self.given_name))
        self.merge = merge
        utils.log_init_stats(self)


    def process(self):
        '''
        Process the input LAS file.
        '''

        for d in [self.vlrcorrect_dir, self.archive_dir, self.out_dir]:
            L.info('Creating dir %s' % (d))
            utils.make_dirs(d)

        lastools_iface.las2las(self.f,
                            self.vlrcorrect_dir,
                            archive_dir=self.archive_dir,
                            archive=True)
        
        py3dtiles_iface.tile(self.f)
        
        py3dtiles_iface.merge(self.out_dir)

        if self.merge:
            utils.merge(in_dir=self.vlrcorrect_dir, out_dir=self.out_dir)
        return str(self.out_dir)

