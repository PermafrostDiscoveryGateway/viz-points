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

def log_init_stats(self):
    '''
    Log initialization values.

    Variables:
    :param self self: The `self` object from which to extract values.
    '''
    self.L.info('File:            %s' % (self.f))
    self.L.info('Merge on:        %s' % (self.merge))
    self.L.info('Intensity > RGB: %s' % (self.intensity_to_RGB))
    self.L.info('Archive input:   %s' % (self.intensity_to_RGB))
    self.L.info('Given name:      %s' % (self.given_name))
    self.L.info('File extension:  %s' % (self.ext))
    self.L.info('Verbose:         %s' % (self.L.propagate))
    self.L.debug('base_dir:        %s' % (self.base_dir))
    self.L.debug('bn:              %s' % (self.bn))
    self.L.debug('rewrite_dir:     %s' % (self.rewrite_dir))
    self.L.debug('archive_dir:     %s' % (self.archive_dir))
    self.L.debug('out_dir:         %s' % (self.out_dir))
    self.L.debug('las_name:        %s' % (self.las_name))

