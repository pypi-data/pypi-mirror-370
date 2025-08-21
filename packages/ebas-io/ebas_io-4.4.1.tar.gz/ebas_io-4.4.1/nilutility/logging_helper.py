"""
nilutility/logging_helper.py
$Id: logging_helper.py 2452 2020-04-23 19:20:47Z pe $

Module for logging initialisation.
This module is just a helper for the default python logging module.
It helps set up logging. But the use of python logging for the user modules
is completely uncahnged.
In the default case, the main script uses nilu.logging to set up the logging
facilities and other customizations. Logging itself will be uncahnges and
still done by using the default logging module

Features:
- typical logging setups can be done in a simple call to init_logging
- CustomFormatter class provides additional format names
  (level_on_>=warning, level+logger_on_>=warning)
- modified default log format for console output:
  '%(level+logger_on_>=warning)s%(message)s'
  (more practical for most usage cases)
- modified default log format for logfile output:
  '%(asctime)s %(name)-12s %(levelname)-8s: %(message)s'

Synopsis:

* general purpose console output (for usual commandline tools)
import logging
import nilu.logging_helper
nilu.logging_helper.init_logging(console={'level': logging.INFO})
logger = logging.getLogger('MyMainModule')
logger.info('hello')
logger.debug('debug test')
logger.warning('watch out!')
logger.critical('too late...')
>>CONSOLE OUTPUT:
hello
debug test
WARNING (MyMainModule): watch out!
CRITICAL (MyMainModule): too late...

* background task, silent, but create a logfile
import logging
import nilu.logging_helper
nilu.logging_helper.init_logging(\
    logfile=[{'level': logging.INFO, 'file': '/tmp/%Y%m%d.log'}])
logger = logging.getLogger('MyMainModule')
logger.info('hello')
logger.debug('debug test')
logger.warning('watch out!')
logger.critical('too late...')
>>CONSOLE OUTPUT:
>>/tmp/<date>.log:
2011-06-18 20:59:23,628 MyMainModule INFO    : hello
2011-06-18 20:59:23,631 MyMainModule WARNING : watch out!
2011-06-18 20:59:23,632 MyMainModule CRITICAL: too late...

* info and higher to console, one normal logfile and one debug log
import logging
import nilu.logging_helper
nilu.logging_helper.init_logging(\
    console={'level': logging.INFO},
    logfile=[{'level': logging.INFO, 'file': '/tmp/info_%Y%m%d.log'},
             {'level': logging.DEBUG,'file': '/tmp/debug_%Y%m%d.log'},])
logger = logging.getLogger('MyMainModule')
logger.info('hello')
logger.debug('debug test')
logger.warning('watch out!')
logger.critical('too late...')
>>CONSOLE OUTPUT:
hello
WARNING (MyMainModule): watch out!
CRITICAL (MyMainModule): too late...
>>/tmp/info_<date>.log:
2011-06-18 21:03:41,271 MyMainModule INFO    : hello
2011-06-18 21:03:41,275 MyMainModule WARNING : watch out!
2011-06-18 21:03:41,277 MyMainModule CRITICAL: too late...
>>/tmp/debug_<date>.log:
2011-06-18 21:03:41,271 MyMainModule INFO    : hello
2011-06-18 21:03:41,273 MyMainModule DEBUG   : debug test
2011-06-18 21:03:41,275 MyMainModule WARNING : watch out!
2011-06-18 21:03:41,277 MyMainModule CRITICAL: too late...

* play with format (console) and dateformats and timezones (logfiles):
import logging
import time
import nilu.logging_helper
nilu.logging_helper.init_logging(\
    console={'level': logging.INFO,
             'format': '%(name)-12s %(levelname)-8s: %(message)s'},
    logfile=[{'level': logging.DEBUG,
              'file': '/tmp/localtime_%Y%m%d%H%M.log',
              'datefmt': '%Y%m%d%H%M%S'},
             {'level': logging.DEBUG,
              'file': '/tmp/utc_%Y%m%d%H%M.log',
              'datefmt': '%Y%m%d%H%M%S',
              'datecvt': time.gmtime}])
logger = logging.getLogger('MyMainModule')
logger.info('hello')
logger.debug('debug test')
logger.warning('watch out!')
logger.critical('too late...')
>>CONSOLE OUTPUT:
MyMainModule INFO    : hello
MyMainModule WARNING : watch out!
MyMainModule CRITICAL: too late...
>>/tmp/localtime_<localtimestamp>.log:
20110618214534 MyMainModule INFO    : hello
20110618214534 MyMainModule DEBUG   : debug test
20110618214534 MyMainModule WARNING : watch out!
20110618214534 MyMainModule CRITICAL: too late...
>>/tmp/utc_<utctimestamp>.log:
20110618194534 MyMainModule INFO    : hello
20110618194534 MyMainModule DEBUG   : debug test
20110618194534 MyMainModule WARNING : watch out!
20110618194534 MyMainModule CRITICAL: too late...


History:
V.1.0.0  2011-06-17  pe  initial version

"""

import os
import sys
import logging
import logging.handlers
import time
import datetime
import getpass

INFO_PLUS = 25
INFO_MINUS = 15

class CustomFormatter(logging.Formatter):
    """
    Customized logging formatter class.

    Adiitional features:
        level_on_>=warning
            prints level name if level is >= WARNING
            e.g. "CRITICAL: <rest of log text>"
        level+logger_on_>=warning
            prints level and logger name if level is >= WARNING
            e.g. "CRITICAL (MyMainModule): <rest of log text>"
    """
    def format(self, record):
        """
        Format the specified record as text.

        fills:
            record.__dict__['level_on_>=warning']
            record.__dict__['level+logger_on_>=warning']
        and calls base class method to do the actual formatting.
        """
        if record.__dict__['levelno'] >= logging.WARN:
            record.__dict__['level_on_>=warning'] = logging.getLevelName(\
                record.levelno) + "): "
            record.__dict__['level+logger_on_>=warning'] = \
                logging.getLevelName(record.levelno) + \
                " (" + record.name + "): "
        else:
            record.__dict__['level_on_>=warning'] = ''
            record.__dict__['level+logger_on_>=warning'] = ''
        return logging.Formatter.format(self, record)

class CustomHandlerBase(object):
    """
    Provides functionality for custom handlers
    """
    def generate_filename(self, spec):
        """
        Generate the filename for logging handlers which log to files.
         - substitutes date/time format specifiers in filepath
         - option createdirs
        Parameters:
            spec   file handler specification (dict)
        Returns:
            file name
        """
        # the final datatype of now will be datetime.datetime in order
        # to to get microseconds support. (%f can be used in filename)

        # - now is set to spec[timestamp] if provided
        if 'timestamp' in spec:
            now = spec['timestamp']
            # timestamp may be struct_time or datetime
            if isinstance(now, time.struct_time):
                now = datetime.datetime.fromtimestamp(time.mktime(now))
        # - else now will be retrieved from datecvt if given
        elif 'datecvt' in spec:
            now = spec['datecvt']()
            # datecvt() must return struct_time object (generally for logging)
            # so this is expected to always be true:
            if isinstance(now, time.struct_time):
                now = datetime.datetime.fromtimestamp(time.mktime(now))
        # - else set now to datetime object right away
        else:
            now = datetime.datetime.now()

        # substitute dat/time format specifiers
        filename = now.strftime(spec['file'])
        # expand ~ to users directories ~ home, ~user other user's home:
        filename = os.path.expanduser(filename)
        # substitute $user$
        if '$user$' in filename:
            filename = filename.replace('$user$', getpass.getuser())
        if 'createdirs' in spec and spec['createdirs']:
            filepath = os.path.dirname(filename)
            if filepath and not os.path.isdir(filepath):
                os.makedirs(filepath, 0o775)
        return filename

class CustomFileHandler(logging.FileHandler, CustomHandlerBase):
    """
    File handler with some extra functionality:
     - substitutes date/time format specifiers in filepath
     - option createdirs

    The handler can pass an extra keys from spec to the underlying
    logging.FileHandler:
        mode (deafult 'a')
    """
    def __init__(self, spec):
        """
        Setup customized FileHandler.
        Parameters:
            spec   file handler specification (dict)
        Returns:
            None
        """
        filename = self.generate_filename(spec)
        mode = 'a'  # default: append to file when exists
        if 'mode' in spec:
            mode = spec['mode']
        super(CustomFileHandler, self).__init__(filename, mode)
        self.setLevel(spec['level'])

class CustomTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler,
                                     CustomHandlerBase):
    """
    TimedRotatingFileHandler with some extra functionality:
     - substitutes date/time format specifiers in filepath
     - option createdirs

    The handler can pass some extra keys from spec to the underlying
    logging.TimedRotatingFileHandler:
        when (defult 'h'), interval (default 1), backupCount (default 0),
        utc (default False)
    """
    def __init__(self, spec):
        """
        Setup customized TimedRotatingFileHandler
        Parameters:
            spec   handler specification (dict)
        Returns:
            None
        """
        filename = self.generate_filename(spec)
        kwlist = ('when', 'interval', 'backupCount', 'encoding', 'delay', 'utc')
        kwargs = {kw: spec[kw] for kw in kwlist if kw in spec}
        super(CustomTimedRotatingFileHandler, self).__init__(filename, **kwargs)
        self.setLevel(spec['level'])

class StreamLogger(object):
    # pylint: disable=R0903
    #  R0903: Too few public methods
    """
    Stream object which redirects output to a logger.
    (use this to redirect streams like stdout, stderr)
    """
    def __init__(self, logger, loglevel=logging.INFO):
        """
        Set up StreamLogger object.
        Parameters:
            logger    logger object
            loglevel  log level to be used for messages through this stream
        """
        self.logger = logger
        self.loglevel = loglevel

    def write(self, buf):
        """
        Write method for stream. Writes to logger.
        Parameters:
            buf   output string
        Returns:
            None
        """
        for line in buf.rstrip().splitlines():
            self.logger.log(self.loglevel, line)


def init_logging(console=None, logfile=None, loggers=None, catch_stdout=False,
                 catch_stderr=False):
    """
    Initialize logging.
    Sets up all needed logging facilities and logger configurations.

    Parameters:
       console     definition for console logging
                   dictionary:
                      level:  minimum loglevel for console output
                      format: format for logging
                      datefmt: date format (format time.strftime())
                      datecvt: date converter function
                               Control the timezone for output.
                               e.g. time.gmtime, time.localtime [=default]

                   e.g.:
                      {'level': logging.DEBUG,
                       'format': '%(level+logger_on_>=warning)s%(message)s'}
       logfile     array of dictionaries (multiple logfiles possible):
                      file:    file name (may contain time format elements
                               like %Y%m%d)
                      level:   minimum loglevel for console output
                      format:  format for logging
                      datefmt: date format (format time.strftime())
                      datecvt: date converter function
                               This affects format strings for the log file
                               name as well as the log entries timestamp
                               e.g. time.gmtime, time.localtime [=default]
                      timestamp:
                               provide a timestamp for filename generation
                               (time or datetime.datetime)
                   e.g.:
                      [{'file': 'log', 'level' logging.DEBUG }, ...]
       loggers     minimum loglevels per logger name (modules?)
                   If not defined, all loggers will inherit their level from
                   the root logger.
                   array of dictionaries:
                      [{'<logger-name>': <level>}, ...}
       catch_stdout
                   if true, stdout stream will be caught and written as
                   to logger name STDOUT and severity INFO
       catch_stderr
                   if true, stderr stream will be caught and written as
                   to logger name STDERR and severity ERROR

    Returns:
       None
    """
    logging.addLevelName(25, 'INFO+')
    logging.addLevelName(15, 'INFO-')

    _init_logging_console(console)
    _init_logging_logfiles(logfile)

    if loggers is None:
        # should not use {} as default argument value (pylint W:158)
        loggers = {'root': logging.DEBUG}
    logging.root.level = loggers['root']
    for log in list(loggers.keys()):
        if log != 'root':
            logger = logging.getLogger(log)
            logger.level = loggers[log]

    if catch_stdout:
        stdout_logger = logging.getLogger('STDOUT')
        slo = StreamLogger(stdout_logger, logging.INFO)
        sys.stdout = slo
    if catch_stderr:
        stderr_logger = logging.getLogger('STDERR')
        slo = StreamLogger(stderr_logger, logging.ERROR)
        sys.stderr = slo

def _init_logging_console(console=None):
    """
    Initialize logging. Set up log handler for console output.

    Parameters:
       console     definition for console logging
                   dictionary:
                      level:  minimum loglevel for console output
                      format: format for logging
                      datefmt: date format (format time.strftime())
                      datecvt: date converter function
                               Control the timezone for output.
                               e.g. time.gmtime, time.localtime [=default]

                   e.g.:
                      {'level': logging.DEBUG,
                       'format': '%(level+logger_on_>=warning)s%(message)s'}

    Returns:
       None
    """
    if console != None:
        if not 'level' in console:
            console['level'] = logging.INFO
        if console['level'] <= logging.CRITICAL:
            consolehdl = logging.StreamHandler()
            consolehdl.setLevel(console['level'])
            if 'format' in console and console['format'] != None:
                formatter_c = CustomFormatter(console['format'])
            else:
                formatter_c = CustomFormatter(\
                    '%(level+logger_on_>=warning)s%(message)s')
            if 'datefmt' in console:
                formatter_c.datefmt = console['datefmt']
            if 'datecvt' in console:
                formatter_c.converter = console['datecvt']
            consolehdl.setFormatter(formatter_c)
            logging.root.addHandler(consolehdl)

def _init_logging_logfiles(logfiles=None):
    """
    Initialize logging. Set up log handler for logfile(s)

    Parameters:
       logfiles    array of dictionaries (multiple logfiles possible):
                      handler  CustomFileHandler, CustomTimedRotatingFileHandler
                      file:    file name (may contain time format elements
                               like %Y%m%d)
                      level:   minimum loglevel for console output
                      format:  format for logging
                      datefmt: date format (format time.strftime())
                      datecvt: date converter function
                               This affects format strings for the log file
                               name as well as the log entries timestamp
                               e.g. time.gmtime, time.localtime [=default]
                      timestamp:
                               provide a timestamp for filename generation
                               (time or datetime.datetime)
                      some handlers have extra attributes:
                          CustomFileHandler:
                              mode: file mode, default 's'
                          CustomTimedRotatingFileHandler:
                              when: rotating time S, M, D, W0-W6, midnight
                              interval: how many 'when's to rotate
                              backupCount: how many files to kkep
                              utc: genera filename for backup files in utc
                   e.g.:
                      [{'file': 'log', 'level' logging.DEBUG }, ...]
    """
    filehdls = []
    if logfiles is None:
        # should not use [] as default argument value (pylint W:158)
        logfiles = []
    for log in logfiles:
        if not 'level' in log:
            log['level'] = logging.INFO
        if log['level'] <= logging.CRITICAL:
            if not 'file' in log or log['file'] is None:
                raise ValueError('insufficient logfile definition')
            if 'createdirs' not in log:
                log['createdirs'] = True
            if 'handler' in log:
                logfilehdl = log['handler'](log)
            else:
                logfilehdl = CustomFileHandler(log)
            formatter_f = None
            if 'format' in log:
                formatter_f = CustomFormatter(log['format'])
            else:
                formatter_f = CustomFormatter(\
                    '%(asctime)s %(name)-12s %(levelname)-8s: %(message)s')
            if 'datefmt' in log:
                formatter_f.datefmt = log['datefmt']
            if 'datecvt' in log:
                formatter_f.converter = log['datecvt']
            logfilehdl.setFormatter(formatter_f)
            filehdls.append(logfilehdl)
    for filehdl in filehdls:
        logging.root.addHandler(filehdl)
