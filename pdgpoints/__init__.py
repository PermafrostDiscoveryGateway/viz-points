from pathlib import Path
import logging
import sys

from ._version import __version__

def start_logging(console: bool=True):
    '''
    Start the logger.

    Variables:
    :param bool console: Print log messages to the console in addition to logfile (default: True)
    :return: Logger to use
    :rtype: logging.logger
    '''
    DATE_FMT = '%Y-%m-%dT%H:%M:%S'
    LOG_FMT = "%(asctime)s:%(levelname)s: %(message)s" # overrides import
    L = logging.getLogger('pdgpoints')
    L.setLevel("INFO")
    home = Path.home()
    log_dir = home / 'viz-points' / 'log'
    log_loc = log_dir / 'pdgpoints.log'
    log_dir.mkdir(exist_ok=True)
    fh = logging.FileHandler(log_loc)
    formatter = logging.Formatter(fmt=LOG_FMT, datefmt=DATE_FMT)
    fh.setFormatter(formatter)
    L.addHandler(fh)
    if console:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        L.addHandler(sh)
    L.info("~~ pdgpoints version %s ~~" % (__version__))
    return L

L = start_logging()