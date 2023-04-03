import os
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
from datetime import datetime

from . import L

def log_subprocess_output(pipe):
    try:
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            L.info('subprocess output: %r', line.decode('utf-8'.strip()))
    except CalledProcessError as e:
        L.error("Subprocess Error> %s: %s" % (repr(e), str(e)))

def las2las(flist, output_dir, archive_dir='', archive: bool=True):
    las2lasstart = datetime.now()
    L.info('Using las2las to rewrite malformed VLR (e.g. from QT Modeler)... (step 1 of 3)')
    i = 0
    for f in flist:
        i += 1
        L.info('Processing %s (%s of %s)' % (f, i, len(flist)))
        bn = os.path.basename(f)
        vlrcn = os.path.join(output_dir, bn)
        # construct command
        process = Popen([
            '../bin/las2las',
            '-i',
            f,
            '-target_ecef',
            '-target_epsg', '4326',
            '-o',
            vlrcn
        ],
        stdout=PIPE, stderr=STDOUT)
        # pass pipe to be parsed
        with process.stdout:
            log_subprocess_output(process.stdout)
        # start process
        exitcode = process.wait()
        if exitcode != 0:
            L.error('Subprocess exited with nonzero exit code--check log output')
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