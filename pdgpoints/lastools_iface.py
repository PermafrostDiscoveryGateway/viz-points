import os
from subprocess import Popen, PIPE, STDOUT, CalledProcessError, check_output
from datetime import datetime
from logging import StreamHandler

from .defs import LAS2LAS_LOC, LASINFO_LOC
from . import L

def log_subprocess_output(pipe, verbose=False):
    L.propagate = verbose
    try:
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            L.info('subprocess output: %r', line.decode('utf-8'.strip()))
    except CalledProcessError as e:
        L.error("Subprocess Error> %s: %s" % (repr(e), str(e)))

def lasinfo(f, verbose=False):
    '''
    Use lasinfo to extract CRS info (in EPSG format) from a LAS or LAZ point cloud file.

    Variables:
    :param f: The input file
    :type f: str or pathlib.Path
    :return: The EPSG code of the CRS, and CRS info as WKT
    :rtype: list[str, str]
    '''
    command = [
        LASINFO_LOC,
        '-i', f,
        '-stdout',
        #'-target_epsg', out_crs,
    ]

    process = Popen(command,
                    stdout=PIPE,
                    stderr=STDOUT)

    wkt = check_output(('grep', 'AUTHORITY'), stdin=process.stdout)
    with process.stdout:
        log_subprocess_output(process.stdout, verbose=verbose)
    exitcode = process.wait()
    if exitcode != 0:
        L.error('lasinfo subprocess exited with nonzero exit code--check log output')
        exit(1)
    epsg = wkt.split('"')[-2]

    return epsg, wkt

def las2las(f,
            output_file,
            #out_crs: str='4326',
            archive_dir='',
            archive: bool=False,
            intensity_to_RGB: bool=False,
            verbose=False):
    '''
    Simple wrapper around las2las to repair and rework LAS files.
    LAS is rewritten with valid VLRs to correct errors propagated by processing suites
    e.g. QT Modeler, to be read by software that is picky about LAS format, e.g. PDAL.
    Output is converted to WGS84 earth-centered earth-fixed (ECEF) CRS, EPSG 4326
    by default, to prepare for display in Cesium.
    Also, an option exists to copy intensity values into RGB for viewing.
    Commands are written to log output and STDOUT from las2las should be as well.

    Variables:
    :param f: The input file
    :type f: str or pathlib.Path
    :param output_file: The output file
    :type output_file: str or pathlib.Path
    :param archive_dir: Location to archive input file, if applicable
    :type output_file: str or pathlib.Path
    :param bool archive: Whether or not to archive input files
    :param bool intensity_to_RGB: Whether or not to copy intensity values to RGB
    :param bool verbose: Whether or not to write STDOUT (output will always be written to log file)
    '''
    if verbose:
        L.propagate = verbose
    las2lasstart = datetime.now()
    L.info('Using las2las to rewrite malformed VLR (e.g. from QT Modeler)... (step 1 of 3)')
    # construct command
    command = [
        LAS2LAS_LOC,
        '-i', f,
        '-set_ogc_wkt', '0',
        #'-target_epsg', out_crs,
    ]
    if intensity_to_RGB:
        # add args to copy I into attrib 0
        command.append('-copy_intensity_into_register')
        command.append('0')
    # add args defining output file location
    command.append('-o')
    command.append(output_file)
    L.debug('Command args: %s' % (command))
    # construct subprocess
    process = Popen(command,
                    stdout=PIPE,
                    stderr=STDOUT)
    # pass pipe to be parsed
    with process.stdout:
        log_subprocess_output(process.stdout, verbose=verbose)
    # start subprocess
    exitcode = process.wait()
    if exitcode != 0:
        L.error('las2las rewrite subprocess exited with nonzero exit code--check log output')
        exit(1)
    if archive:
        # move the file to the archive
        try:
            assert (archive_dir != '')
            bn = os.path.split(f)[1]
            an = os.path.join(archive_dir, bn)
            L.info('Archiving to %s' % (an))
            os.replace(src=f, dst=an)
        except AssertionError as e:
            L.error('Archiving is on but no archive directory set! Cannot archive files!')
        except Exception as e:
            L.error('%s: %s' % (repr(e), e))
    if intensity_to_RGB:
        command = [
            LAS2LAS_LOC,
            '-i', output_file,
            '-copy_register_into_R', '0',
            '-copy_register_into_G', '0',
            '-copy_register_into_B', '0',
            '-set_register', '0', '0'
        ]
        L.info('Copying intensity to register...')
        L.debug('Command args: %s' % (command))
        # new subprocess
        process = Popen(command,
                        stdout=PIPE,
                        stderr=STDOUT)
        # pass pipe to be parsed
        with process.stdout:
            log_subprocess_output(process.stdout, verbose=verbose)
        # start subprocess
        exitcode = process.wait()
        if exitcode != 0:
            L.error('las2las inplace attribute copy subprocess exited with nonzero exit code--check log output')
            exit(1)

    las2lastime = (datetime.now() - las2lasstart).seconds/60
    L.info('Finished (%.1f min)' % (las2lastime))
