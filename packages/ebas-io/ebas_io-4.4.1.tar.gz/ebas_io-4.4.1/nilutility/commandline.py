"""
$Id: commandline.py 2454 2020-04-24 20:22:51Z pe $

wrapper for nilu command line programs.
"""
import sys
import errno
import logging
import argparse
import getpass
import textwrap
import netrc
import cProfile, pstats
import datetime
import re
import os.path
from nilutility.argparse_helper import NiluArgumentParser, \
    ParseStrings, ParseIntegers, \
    parse_time_instant, parse_time_interval
from nilutility import logging_helper
from nilutility.encoding import fix_io_encoding
from nilutility.datetime_helper import DatetimeInterval

# ConfigParser has been renamed to configparser in python3
# when dropping python to -> import configparser
from six.moves import configparser


class NiluCommandline(object):  # pylint: disable-msg=R0902
    # R0902: Too many instance attributes
    """
    class for handling Nilu commandline arguments.
    """
    def __init__(self, func, custom_args=None,  # pylint: disable-msg=R0913
                 private_args=None, help_description=None,
                 version='#no-version-number',
                 version_date=datetime.datetime.now(),
                 logging_params = None,
                 progname=None, config_main_section='GENERAL',
                 def_args=None):
        # R0913: Too many arguments
        self.custom_args = custom_args or []
        self.private_args = private_args
        self.help_description = help_description
        self.version = version
        self.version_date = version_date
        self.func = func
        self.unparsed = None
        if progname:
            self.progname = progname
        else:
            self.progname = func.__name__  # func can be a class or a function
        self.config_main_section = config_main_section
        self.startuptime = datetime.datetime.now()
        self.logbasename = self.progname + \
                           self.startuptime.strftime('_%Y-%m-%d_%H%M%S')
        self.logging_params = logging_params
        self.logger = None
        self.args = None
        self.def_args = def_args
        self.set_defaults()
        self.versiontext=textwrap.dedent('''\n                                   
            %(prog)s {0}                                                    
            Copyright (C) 2012-{1} NILU - Norwegian Institut for Air Reserch     
            '''.format(self.version, self.version_date.year))
        self.logger = logging.getLogger('NiluCmdLine')

    def run(self):
        self.unparsed = sys.argv[1:]
        self.preparse()
        self.parse_args()
        self.logger.debug("starting {}, version {}".format(self.progname,
                                                           self.version))
        self.wrap_func()

    def preparse(self):
        if 'CONFIG' in self.custom_args:
            self.preparse_config()
        if 'LOGGING' in self.custom_args:
            self.preparse_logging()

    def set_defaults(self):
        """
        Set defaults.

        Parameters:
            None
        Returns:
           None
        """
        default = {}   # the global nilutility default
        if 'CONFIG' in self.custom_args:
            default['cfgfile'] = '{}.cfg'.format(self.progname)
        if 'LOGGING' in self.custom_args:
            default['loglevfile'] = 'silent'
            default['loglevconsole'] = 'info'
            default['logfile'] = os.path.join(
                '.', self.logbasename) + '.log'
        if self.def_args:
            # update with default from caller (if set)
            default.update(self.def_args)
        self.def_args = default

    def _preparse_config_prepare(self):
        """
        Prepare the configuration file (find the file and open it).
        This logig is rather general and can easyly be reused by derived
        classes.
        Parameters:
            None
        Returns:
            config parser object
            None if any problem with the config file
        """
        preparser = NiluArgumentParser(add_help=False)
        preparser.add_config_arguments(cfgfile=True)
        preparser.set_known_defaults(**self.def_args)
        self.args, self.unparsed = preparser.parse_known_args(
            args=self.unparsed, namespace=self.args)
        # expand ~ to users directories ~ home, ~user other user's home:
        self.args.cfgfile = os.path.expanduser(self.args.cfgfile)
        # read config
        try:
            fil = open(self.args.cfgfile, "r")
            if (os.sep not in self.args.cfgfile and
                os.path.realpath(os.path.expanduser(
                    '~/'+self.args.cfgfile)) !=
                    os.path.realpath((self.args.cfgfile))):
                sys.stderr.write('WARNING: using local config file {}\n'.format(
                    self.args.cfgfile))
            self.args.cfgfile = fil
        except IOError as expt:
            if expt.errno == 2:
                if os.sep in self.args.cfgfile:
                    sys.stderr.write(
                        "no config file ({}) found; using defaults".format(
                            self.args.cfgfile) + '\n')
                    self.args.cfgfile = None
                    return None
                else:
                    # relative filename: when current dir failed, try
                    # users home dir, finally program dir (thus, a default
                    # config can be provided with the installation)

                    # try program's directory:
                    localname = os.path.expanduser('~/' + self.args.cfgfile)
                    try:
                        fil = open(localname, 'r')
                        # no warning when using home dir config file
                        self.args.cfgfile = fil
                    except IOError as expt:
                        if expt.errno == 2:
                            # try program's directory:
                            localname = os.path.join(os.path.dirname(
                                os.path.realpath(sys.argv[0])),
                                self.args.cfgfile)
                            try:
                                fil = open(localname, 'r')
                                sys.stderr.write(
                                    'WARNING: using program global config file '
                                    '{}\n'.format(localname))
                                self.args.cfgfile = fil
                            except IOError as expt:
                                if expt.errno == 2:
                                    sys.stderr.write(
                                        "no config file (./{0}, ~/{0}, {1}) "
                                        "found; using defaults".format(
                                            self.args.cfgfile, localname) + \
                                        '\n')
                                    self.args.cfgfile = None
                                    return None
                                else:
                                    sys.stderr.write(
                                        "config file ({}) error: {}; "
                                        "using defaults\n".format(
                                            localname, str(expt)))
                                    self.args.cfgfile = None
                                    return None
                        else:
                            sys.stderr.write(
                                "config file ({}) error: {}; using defaults\n"\
                                    .format(localname, str(expt)))
                            self.args.cfgfile = None
                            return None

            else:
                sys.stderr.write("config file error: " + str(expt) + \
                                 '; using defaults\n')
                return None
        config = configparser.ConfigParser()
        config.optionxform = str  # make config options case sensitive!
        try:
            config.readfp(fil)
        except AttributeError:
            # from python 3.12, ConfigParser has no readfp
            config.read_file(fil)
        # reset the file, in case the app wants to use the config file:
        fil.seek(0)
        return config

    def preparse_config(self):
        """
        Partially parse commandline arguments relevant config file location.
        Then read the config file.
        preparser: process only --cfgfile
        Needs to be pre-parsed in order to use defaults in the real
        parser.
        """
        # prepare the config file parser:
        config = self._preparse_config_prepare()
        if config is None:
            return

        try:
            self.def_args.update(dict(config.items(self.config_main_section)))
        except configparser.Error as expt:
            sys.stderr.write('config file {}; error: {}\n'.format(
                self.args.cfgfile, str(expt)) + '\n')
        if self.config_main_section == self.progname:
            return

        try:
            self.def_args.update(dict(config.items(self.progname)))
        except configparser.NoSectionError:
            pass
        except configparser.Error as expt:
            sys.stderr.write('config file {}; error: {}\n'.format(
                self.args.cfgfile, str(expt)) + '\n')

    def add_custom_args(self, parser):                                           
        """                                                                      
        Add arguments for specific customized goals.

        Parameters:
            parser    parser object
        Returns:
            None
        """
        parser.add_argument('--version', '-V ', action='version', \
            version=self.versiontext,
            help='display version information and exit')
        if 'CONFIG' in self.custom_args:
            parser.add_config_arguments(cfgfile=True)
        if 'LOGGING' in self.custom_args:
            parser.add_logging_arguments(logfile=True, loglevconsole=True,
                                         loglevfile=True, profile=True)

    def preparse_logging(self):
        """
        Partially parse commandline arguments relevant for logging, then init
        logging according to setings.
        """
        preparser = NiluArgumentParser(add_help=False)
        preparser.add_logging_arguments(logfile=True, loglevconsole=True,
                                        loglevfile=True, profile=True)
        preparser.set_known_defaults(**self.def_args)
        self.args, self.unparsed = preparser.parse_known_args(
            args=self.unparsed, namespace=self.args)

        # init logging
        console={'level': self.args.loglevconsole,
                 'format': '%(levelname)-8s: %(message)s'}
        if self.logging_params and 'console' in self.logging_params:
            console.update(self.logging_params['console'])
        logfile={'file': self.args.logfile,
                 'createdirs': True,
                 'level': self.args.loglevfile}
        if self.logging_params and 'file' in self.logging_params:
            logfile.update(self.logging_params['file'])
        try:
            logging_helper.init_logging(console=console, logfile=[logfile])
        except IOError as expt:
            sys.stderr.write("log file error: {}; exiting\n".format(str(expt)))
            sys.exit(expt.errno)  # IOError errcodes are all positive integers

    def parse_args(self):
        """
        Main argument parsing.

        Parameters:
            None
        Returns:
           None
        """
        parser = NiluArgumentParser(add_help=True,
                                    description=self.help_description)

        # custom parsers (parser groups used for the same purpose in many
        # programs)
        self.add_custom_args(parser)
        # callback function for argumenst used only by the calling program
        if self.private_args:
            self.private_args(parser, self)

        parser.set_known_defaults(**self.def_args)
        self.args = parser.parse_args(args=self.unparsed,
                                      namespace=self.args)

    def wrap_func(self):
        """
        Wrapper for nilu commandline programs. Catches Ctrl-C and broken pipe.
        Catches sys.exit from below and finishes profiling in those cases before
        re-raising.
        Adds profiling if commandline option --profile is given

        Parameters:
            func      function to be called (main execution for the program)
            args      args to be used for function call
            kwargs    kwargs to be used for function call

        Returns:
            None

        Exits:
            with exit code in case of user interrupt or broken pipe
        """

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--profile', action='store_true')
        arg, _ = parser.parse_known_args()
        sysexit = None
        if arg.profile:
            prof = cProfile.Profile()
            prof.enable()
        try:
            self.func(self)
        except KeyboardInterrupt:
            logger = logging.getLogger('NiluMain')
            logger.fatal('terminated on user request')
            sys.exit(1)
        except IOError as expt:
            if expt.errno == errno.EPIPE:
                logger = logging.getLogger('NiluMain')
                logger.fatal('broken pipe, exit')
                sys.exit(expt.errno)
            else:
                raise
        except SystemExit as expt:
            logger = logging.getLogger('NiluMain')
            logger.debug("%s terminated with exit code %s", self.progname,
                         str(expt.code))
            sysexit = expt
        if arg.profile:
            prof.disable()
            profile_file = self.logbasename + '.profstat'
            self.logger.info('writing profiling statistics to file %s',
                             profile_file)
            self.logger.info('writing profiling top 10% sorted by time to '
                             'stderr')
            prof.dump_stats(profile_file)
            sortby = 'time'
            pstat = pstats.Stats(prof, stream=sys.stderr).sort_stats(sortby)
            pstat.print_stats(.1)
        if sysexit:
            raise sysexit # pylint: disable-msg=E0702
            # E0702: Raising NoneType
            #    this is conditional. Pylint bug.

fix_io_encoding('UTF-8')
