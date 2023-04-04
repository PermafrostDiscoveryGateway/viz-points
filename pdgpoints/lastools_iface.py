import os
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
from datetime import datetime

from . import L

def log_subprocess_output(pipe, verbose=False):
    L.propagate = verbose
    try:
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            L.info('subprocess output: %r', line.decode('utf-8'.strip()))
    except CalledProcessError as e:
        L.error("Subprocess Error> %s: %s" % (repr(e), str(e)))

def las2las(f,
            output_file,
            archive_dir='',
            archive: bool=False,
            verbose=False):
    L.propagate = verbose
    las2lasstart = datetime.now()
    L.info('Using las2las to rewrite malformed VLR (e.g. from QT Modeler)... (step 1 of 3)')
    # construct command
    process = Popen([
        '../bin/las2las',
        '-i',
        f,
        '-target_ecef',
        '-target_epsg', '4326',
        '-o',
        output_file
    ],
    stdout=PIPE, stderr=STDOUT)
    # pass pipe to be parsed
    with process.stdout:
        log_subprocess_output(process.stdout, verbose=verbose)
    # start process
    exitcode = process.wait()
    if exitcode != 0:
        L.error('las2las subprocess exited with nonzero exit code--check log output')
        exit(1)
    if archive:
        # move the file to the archive
        try:
            assert (archive_dir != '')
            an = os.path.join(archive_dir, bn)
            L.info('Archiving to %s' % (an))
            os.replace(src=f, dst=an)
        except AssertionError as e:
            L.error('Archiving is on but no archive directory set! Cannot archive files!')
        except Exception as e:
            L.error('%s: %s' % (repr(e), e))
    las2lastime = (datetime.now() - las2lasstart).seconds/60
    L.info('Finished (%.1f min)' % (las2lastime))