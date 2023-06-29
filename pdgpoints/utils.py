from pathlib import Path
from datetime import datetime
from typing import Union
from pyproj import CRS

def timer(time: Union[datetime, bool]=False) -> Union[datetime, int, float]:
    """
    Start a timer if no argument is supplied, otherwise stop it and report the seconds and minutes elapsed.

    :param time: The directory to create
    :type time: bool or datetime.datetime
    :return: If no time is supplied, return start time; else return elapsed time in seconds and decimal minutes
    :rtype: datetime.datetime or (int, float)
    """
    if not time:
        return datetime.now()
    else:
        time = (datetime.now() - time).seconds
        return time, time/60

def make_dirs(d: Path, exist_ok: bool=True):
    """
    Simple wrapper to create directory using os.makedirs().
    Included is a logging command.

    :param pathlib.Path d: The directory to create
    :param bool exist_ok: Whether to gracefully accept an existing directory (default: True)
    """
    d.mkdir(exist_ok=exist_ok)

def rm_files(files: list[Path]=[]):
    """
    Remove a list of intermediate processing files.

    :param list files: A list `pathlib.Path`s to remove
    """
    for f in files:
        if f.is_file():
            f.unlink()

def write_wkt_to_file(f: Path, wkt: str):
    """
    Write well-known text (WKT) string to file. Will overwrite existing file.

    :param f: File path to write to (wil)
    :type f: pathlib.Path
    :param str wkt: String to write
    """
    if f.is_file():
        f.unlink()
    with open(f, 'w') as fw:
        fw.write(str(wkt))

def read_wkt_from_file(f: Path) -> str:
    """
    Read the WKT string from a file

    :param f: The file to read
    :type f: pathlib.Path
    :return: The well-known text of the CRS in use
    :rtype: str
    """
    with open(f, 'r') as fr:
        return fr.read()

def get_epsgs_from_wkt(wkt: str) -> list:
    """
    Use pyproj to parse a well-known text string to CRS. Returns a list of
    `[CRS, horizontal EPSG, vertical EPSG]` where the EPSG fields could be
    an integer representing an EPSG code or `None`.

    :param str wkt: The well-known text string to parse to pyproj.crs.CRS
    :return: List of [pyproj.crs.CRS object, epsg_h (int or None), epsg_v (int or None)])
    :rtype: list
    """
    epsg_h, epsg_v = None, None
    crs = CRS.from_wkt(wkt)
    if crs.is_compound:
        L.info('Found compound coordinate system (COMPD_CS): %s entries' % (len(crs.sub_crs_list)))
        if len(crs.sub_crs_list) > 2: # not sure if this case exists, but should be warned anyway
            L.warning('More than 2 entries in a compound coordinate system may cause an unwanted override!')
        for c in crs:
            if c.is_vertical:
                epsg_v = c.to_epsg()
            else:
                epsg_h = c.to_epsg()
    else:
        if crs.is_vertical:
            epsg_v = crs.to_epsg()
        else:
            epsg_h = crs.to_epsg()
    if epsg_h:
        L.info('Found horizontal EPSG: %s' % (epsg_h))
    if epsg_v:
        L.info('Found vertical EPSG: %s' % (epsg_v))
    return crs, epsg_h, epsg_v


def log_init_stats(self):
    """
    Log initialization values.

    :param self self: The `self` object from which to extract values.
    """
    self.L.info('File:            %s' % (self.f))
    self.L.info('Merge:           %s' % (self.merge))
    self.L.info('Intensity > RGB: %s' % (self.intensity_to_RGB))
    self.L.info('Intens. scalar:  %sx' % (self.rgb_scale))
    self.L.info('Translate Z:     %+.1f' % (self.translate_z))
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

