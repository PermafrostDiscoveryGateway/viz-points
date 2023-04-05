import logging
import os

from ._version import version

def start_logging(console: bool=False):
    '''
    Start the logger.

    Variables:
    :param bool console: Print log messages to the console in addition to logfile (default: True)
    :return: Logger to use
    :rtype: logging.logger
    '''
    DATE_FMT = '%Y-%m-%dT%H:%M:%S'
    LOG_FMT = "%(asctime)s:%(levelname)s: %(message)s" # overrides import
    L = logging.getLogger('DRPWorkflow')
    if not console:
        # turn off logger propagation (messages will not print to stdout)
        L.propagate = False
    L.setLevel("INFO")
    handler = logging.FileHandler(os.path.expanduser("~/bin/drpworkflow/log/log.log"))
    formatter = logging.Formatter(fmt=LOG_FMT, datefmt=DATE_FMT)
    handler.setFormatter(formatter)
    L.addHandler(handler)
    L.info("~~ pdgpoints version %s ~~" % (version))
    return L

L = start_logging()