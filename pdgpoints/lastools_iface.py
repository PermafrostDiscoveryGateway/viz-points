from pathlib import Path
from typing import Union, Tuple
from subprocess import Popen, PIPE, STDOUT, CalledProcessError, check_output
from datetime import datetime
import pandas as pd
from logging import getLogger

from .defs import LAS2LAS_LOC, LASINFO_LOC
from . import utils

def log_subprocess_output(pipe: PIPE):
    """
    Log the output from a lastools subprocess.

    :param subprocess.PIPE pipe: The pipe to listen to
    :param bool verbose: Whether to log more messages 
    """
    L = getLogger(__name__)
    try:
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            L.info('subprocess output: %r', line.decode('utf-8').strip())
    except CalledProcessError as e:
        L.error("Subprocess Error> %s: %s" % (repr(e), str(e)))

def run_proc(command: list[str],
             get_wkt: bool=False) -> Union[str, None]:
    """
    Start a subprocess with a given command.

    :param list command: List of command arguments
    :param bool get_wkt: Whether to grep the well-known text (WKT) string from lasinfo output
    :param bool verbose: Whether to log more messages

    :return: Well-known text (WKT) of the file's coordinate reference system (CRS)
    :rtype: str
    """
    L = getLogger(__name__)
    L.debug('Command args: %s' % (command))
    process = Popen(command,
                    stdout=PIPE,
                    stderr=STDOUT)
    if get_wkt:
        wktstr = check_output(('grep', 'EPSG'), stdin=process.stdout).decode().strip().strip('\n')
    # pass pipe to be parsed
    with process.stdout:
        log_subprocess_output(process.stdout)
    # start subprocess
    exitcode = process.wait()
    if exitcode != 0:
        L.error('las2las rewrite subprocess exited with nonzero exit code--check log output')
        exit(1)
    if get_wkt:
        return wktstr

def lasinfo(f: Path) -> Tuple[str, str, str, Path]:
    """
    Use lasinfo to extract CRS info (in EPSG format) from a LAS or LAZ point cloud file.

    :param f: The input file
    :type f: pathlib.Path

    :return: The EPSG code of the CRS, and CRS info as WKT
    :rtype: str, str, str, pathlib.Path
    """
    L = getLogger(__name__)
    lasinfostart = utils.timer()
    command = [
        LASINFO_LOC,
        '-i', f,
        '-nc', # shaves a lot of time off large jobs by telling lasinfo not to compute min/maxes
        '-stdout',
    ]
    wkt = run_proc(command=command, get_wkt=True)
    L.debug('WKT string: %s' % (wkt))
    crs, epsg_h, epsg_v, h_name, v_name = utils.get_epsgs_from_wkt(wkt)
    cpd = 'Compound ' if crs.is_compound else ''
    L.info('%sCRS: %s' % (cpd, h_name))
    L.info('%sVRS: %s' % (cpd, v_name))
    L.debug('%sCRS object: \n%s' % (cpd, repr(crs)))
    wktf = Path(str(f) + '-wkt.txt')
    L.info('Writing WKT to %s' % (wktf))
    utils.write_wkt_to_file(f=wktf, wkt=wkt)
    L.info('Finished lasinfo (%s sec / %.1f min)' % utils.timer(lasinfostart))
    return epsg_h, epsg_v, wkt, wktf, h_name, v_name

def lasmean(f: Path,
            name: str="none"):
    """
    Use las2txt to output values of X and Y for a dataset,
    then return the mean of those points. To save resources,
    only every 10,000th point will be sampled.

    :param f: The input file
    :type f: str or pathlib.Path
    :param str name: The name of the coordinate reference system in use
    :return: Mean X and Y of the dataset, and the location of the ascii file used to calculate these
    :rtype: float, float, str
    """
    L = getLogger(__name__)
    lasmeanstart = utils.timer()
    xyf = Path(str(f) + '-xy.txt')
    L.info("Writing abridged XY file to %s" % (xyf))
    command = [
        LAS2LAS_LOC,
        '-i', f,
        '-keep_every_nth', '10000',
        '-o', str(xyf),
        '-oparse', 'xy'
    ]
    run_proc(command=command)
    df = pd.read_csv(xyf, sep=' ', header=None, names=['x', 'y'])
    mean = df.mean()
    L.info('X mean: %.3f Y mean: %.3f (%s)' % (mean.x, mean.y, name))
    lasmeantime = (datetime.now() - lasmeanstart).seconds
    L.info('Finished las2las (%s sec / %.1f min)' % (lasmeantime, lasmeantime/60))
    return mean.x, mean.y, xyf

def las2las_ogc_wkt(f: Path,
                    output_file: Path):
    """
    Use las2las to write CRS info in OGC WKT format to the output file.

    :param f: The input file
    :type f: str or pathlib.Path
    :param output_file: The output file
    :type output_file: str or pathlib.Path
    :param bool verbose: Whether or not to write STDOUT (output will always be written to log file)
    """
    L = getLogger(__name__)
    las2lasstart = datetime.now()
    # construct command
    command = [
            LAS2LAS_LOC,
            '-i', f,
            '-set_ogc_wkt',
            '-o', output_file
        ]
    run_proc(command=command)
    las2lastime = (datetime.now() - las2lasstart).seconds
    L.info('Finished las2las (%s sec / %.1f min)' % (las2lastime, las2lastime/60))

def las2las(f: Path,
            output_file: Path,
            #out_crs: str='4326',
            archive_dir: Path=Path(''),
            archive: bool=False,
            intensity_to_RGB: bool=False,
            rgb_scale: float=1.0,
            translate_z: float=0.0,
            llvrgb: bool=False):
    """
    Simple wrapper around las2las to repair and rework LAS files.
    LAS is rewritten with valid VLRs to correct errors propagated by processing suites
    e.g. QT Modeler, to be read by software that is picky about LAS format, e.g. PDAL.
    Output is converted to WGS84 earth-centered earth-fixed (ECEF) CRS, EPSG 4326
    by default, to prepare for display in Cesium.
    Also, an option exists to copy intensity values into RGB for viewing.
    Commands are written to log output and STDOUT from las2las should be as well.

    :param f: The input file
    :type f: str or pathlib.Path
    :param output_file: The output file
    :type output_file: str or pathlib.Path
    :param archive_dir: Location to archive input file, if applicable
    :type output_file: str or pathlib.Path
    :param bool archive: Whether or not to archive input files
    :param bool intensity_to_RGB: Whether or not to copy intensity values to RGB
    :param float rgb_scale: RGB scale multiplier
    :param float translate_z: Z translation value
    :param bool verbose: Whether or not to write STDOUT (output will always be written to log file)
    """
    L = getLogger(__name__)
    las2lasstart = datetime.now()
    # construct command
    wktf = str(f) + '-wkt.txt'

    if intensity_to_RGB:
        L.info('Copying intensity to RGB by exploding and reforming LAS fields')
        read_command = [
            LAS2LAS_LOC,
            '-i', f,
            '-scale_intensity', '%s' % (rgb_scale),
            '-otxt',
            '-oparse', 'xyziiiitanr',
            '-stdout'
        ]
        write_command = [
            LAS2LAS_LOC,
            '-stdin',
            '-itxt',
            '-iparse', 'xyziRGBtanr',
            '-scale_rgb_up',
            '-load_ogc_wkt', wktf,
            '-o', output_file
        ]
        L.debug('Cmd L of pipe: %s' % read_command)
        L.debug('Cmd R of pipe: %s' % write_command)
        r_process = Popen(read_command, stdout=PIPE)
        w_process = Popen(write_command, stdin=r_process.stdout, stdout=PIPE)
        r_process.stdout.close()
        output = w_process.communicate()[0]
        L.info('Translating Z values')
        command = [
            LAS2LAS_LOC,
            '-i', output_file,
            '-translate_z', '%s' % (translate_z),
            '-olaz'
        ]
        run_proc(command=command)
        L.debug('Piped cmd output: %s' % output)
    elif llvrgb:
        L.info("Rewriting input CSV from 'xyzRGB' to LAZ")
        command = [
            LAS2LAS_LOC,
            '-itxt',
            '-i', f,
            '-set_ogc_wkt',
            '-iparse', 'xyzRGB',
            '-epsg', '4326',
            '-s', '256',
            '-o', output_file
        ]
        run_proc(command=command)
    else:
        L.info('Rewriting LAS to avoid VLR size errors (e.g. PDAL reading QTModeler files)')
        command = [
            LAS2LAS_LOC,
            '-i', f,
            '-load_ogc_wkt', wktf,
            '-translate_z', '%s' % (translate_z),
            '-o', output_file
        ]
        run_proc(command=command)

    if archive:
        # move the file to the archive
        try:
            assert (str(archive_dir) != '')
            an = archive_dir.joinpath(f.name)
            L.info('Archiving to %s' % (an))
            f.rename(an)
        except AssertionError as e:
            L.error('Archiving is on but no archive directory set! Cannot archive files!')
        except Exception as e:
            L.error('%s: %s' % (repr(e), e))

    las2lastime = (datetime.now() - las2lasstart).seconds
    L.info('Finished las2las (%s sec / %.1f min)' % (las2lastime, las2lastime/60))
