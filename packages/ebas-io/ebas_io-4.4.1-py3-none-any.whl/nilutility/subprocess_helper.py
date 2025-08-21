"""
nilu/subprocess_helper.py
$Id: subprocess_helper.py 2824 2024-04-19 10:46:32Z pe $

Convenience functions for subprocess

History:
V.1.0.0  2012-12-11  pe  initial version

"""

import os
import shlex
import subprocess
import threading
import logging
import time
import six

class LogPipe(threading.Thread):
    """"
    Logger pipe class for connecting pythons subprocess module to the logging
    module. This is a helper for subprocess_log_streams().
    Povides a pipe that is constantly read in a new thread and written to a
    target logger.
    """
    def __init__(self, logger=None, level=None, stream=None, result=None):
        """
        Setup the LogPipe object, connect it to a given logger and a loglevel
        and start the thread to wait for pipe input.
        Parameters:
            logger    target logger to write the pipe's data to
            level     loglevel to be used
            result    additionally pass back the pipe's data as list of strings
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.logger = logger
        self.level = level
        self.stream = stream
        self.result = result
        self.fd_read, self.fd_write = os.pipe()
        self.pipe_reader = os.fdopen(self.fd_read)
        self.start()

    def fileno(self):
        """
        Return the write file descriptor of the pipe.
        """
        return self.fd_write

    def run(self):
        """
        Run the thread, logging everything that comes through the pipe.
        """
        for line in iter(self.pipe_reader.readline, ''):
            if self.result is not None:
                self.result.append(line)
            if self.logger is not None:
                self.logger.log(self.level, line.strip('\n'))
            if self.stream is not None:
                self.stream.write(line)
        self.pipe_reader.close()

    def close(self):
        """
        Close the write end of the pipe.
        """
        os.close(self.fd_write)

def subprocess_log_streams(args, logger=None,
                           stdoutlogger=None, stdoutlevel=logging.INFO,
                           stdoutstream=None,
                           stdoutresult=None,
                           stderrlogger=None, stderrlevel=logging.ERROR,
                           stderrstream=None,
                           stderrresult=None,
                           warntime=None, killtime=None):
    # pylint: disable=R0912,R0913
    #  R0912: Too many branches (13/12)
    #  R0913: Too many arguments
    """
    Forks a subprocess and logs it's stdout and stderr to (separate) loggers
    and/or writes to output streams.
    The function waits for the process to finish (needed for cleanup (closing
    write end of pipes).
    Parameters:
        args    arguments for subprocess (commandline as string or list of args
        logger  logger for logging messages of the caller side
        stdoutlogger  logger for subprocesses stdout
        stdoutlevel   loglevel for the subprocesses stdout
        stdoutstream  write stdout to output stream (file obj...)  
        stdoutresult  pass back stdout to caller (list.append)
        stderrlogger  logger for subprocesses stderr
        stderrlevel   loglevel for the subprocesses stderr
        stderrstream  write stderr to output stream (file obj...)  
        stderrresult  pass back stderr to caller (list.append)
        warntime      log warning to logger when runtime exceeds warntime (sec)
        killtime      kill subprocess when runtime exceeds killtime (seconds)
    This implementation is heavily inspired by:
    http://codereview.stackexchange.com/a/17959/20201 (thanks to deuberger)
    """
    if isinstance(args, six.string_types):
        args = shlex.split(args)
    if not logger:
        logger = logging.getLogger('subprocess')
    logger.info("spawning subprocess: " + ' '.join(args))

    stdoutpipe = None
    stderrpipe = None
    if stdoutlogger is not None or stdoutstream is not None or \
       stdoutresult is not None:
        stdoutpipe = LogPipe(logger=stdoutlogger, level=stdoutlevel,
                             stream=stdoutstream, result=stdoutresult)
    if stderrlogger is not None or stderrstream is not None or \
         stderrresult is not None:
        if stderrlogger == stdoutlogger and stderrlevel == stdoutlevel and \
           stderrstream == stdoutstream and stderrresult == stdoutresult:
            stderrpipe = subprocess.STDOUT
        else:
            stderrpipe = LogPipe(logger=stderrlogger, level=stderrlevel,
                                 stream=stderrstream, result=stderrresult)
    try:
        stin_pin, stin_pout = os.pipe()
        proc = subprocess.Popen(args, stdout=stdoutpipe, stderr=stderrpipe, stdin=stin_pin)
        logger.info("spawned pid: {0}".format(proc.pid))
        sec = 0
        while proc.poll() is None:
            if killtime and sec >= killtime:
                logger.error("subprocess still running - killing")
                proc.kill()
            if warntime and sec > 0 and sec % warntime == 0:
                logger.warn("subprocess still running - " + \
                            "parent is alive and waiting")
            time.sleep(1)
            sec += 1
        os.close(stin_pin)
        os.close(stin_pout)
    except OSError as expt:
        logger.error("error spawning process: {0}".format(expt.strerror))
        raise
    finally:
        if isinstance(stdoutpipe, LogPipe):
            stdoutpipe.close()
        if isinstance(stderrpipe, LogPipe):
            stderrpipe.close()
    logger.info("process {0} exited with code {1}"
                .format(proc.pid, proc.returncode))
    return proc
