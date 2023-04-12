import os

def make_dirs(d, exist_ok=True):
    '''
    Simple wrapper to create directory using os.makedirs().
    Included is a logging command.

    Variables:
    :param pathlib.Path d: The directory to create
    :param bool exist_ok: Whether to gracefully accept an existing directory (default: True)
    '''
    os.makedirs(d, exist_ok=exist_ok)

def write_wkt_to_file(f, wkt):
    '''
    '''
    if os.path.exists(f):
        os.remove(f)
    with open(f, 'w') as fw:
        fw.write(str(wkt))

def read_wkt_from_file(f):
    with open(f, 'r') as fr:
        return fr.read()

def log_init_stats(self, **kwargs):
    '''
    Log initialization values.

    Variables:
    :param self self: The `self` object from which to extract values.
    '''
    self.L.info('File:            %s' % (self.f))
    self.L.info('Merge:           %s' % (self.merge))
    self.L.info('Intensity > RGB: %s' % (self.intensity_to_RGB))
    self.L.info('Archive input:   %s' % (self.archive))
    self.L.info('Given name:      %s' % (self.given_name))
    self.L.info('File extension:  %s' % (self.ext))
    self.L.info('Verbose:         %s' % (self.L.propagate))
    self.L.debug('base_dir:        %s' % (self.base_dir))
    self.L.debug('bn:              %s' % (self.bn))
    self.L.debug('rewrite_dir:     %s' % (self.rewrite_dir))
    self.L.debug('archive_dir:     %s' % (self.archive_dir))
    self.L.debug('out_dir:         %s' % (self.out_dir))
    self.L.debug('las_name:        %s' % (self.las_name))

