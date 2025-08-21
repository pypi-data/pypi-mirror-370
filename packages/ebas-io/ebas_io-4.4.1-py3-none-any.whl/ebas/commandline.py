"""
Wrapper for ebas command line programs.

"""

import logging
import argparse
import getpass
import textwrap
import datetime
import re
from nilutility.argparse_helper import NiluArgumentParser, \
    ParseStrings, ParseIntegers, \
    ExclusiveMultiswithAction, \
    parse_time_instant, parse_time_interval
from nilutility.commandline import NiluCommandline
from nilutility.datetime_helper import DatetimeInterval
from nilutility.datatypes import DataObject
import six
from six.moves import input
from .io.file import EbasIOFormatOption, EbasIOFlagOption, \
    EBAS_IOSTYLE_SINGLECOLUMN, EBAS_IOSTYLE_MULTICOLUMN, \
    EBAS_IOSTYLE_MULTICOLUMN_PRECIP, EBAS_IOSTYLE_KEEP
from .db_fileindex import IndexDb, OperationalError

class EbasCommandline(NiluCommandline):  # pylint: disable-msg=R0902
    # R0902: Too many instance attributes
    """
    Class for handling Ebas commandline arguments.

    EbasCommandline is a wrapper for all ebas commandline programs, which
    handles all commandline arguments and the calls a callback function to the
    main program.
    Example usage:
        ```
        EbasCommandline(
            ebas_read_example,
            custom_args=['CONFIG', 'LOGGING', 'TIME_CRIT', 'NASA_READ'],
            private_args=add_private_args,
            help_description='%(prog)s example for reading a NasaAmes datafile.',
            version=__version__).run()
        ```

    The calling program specifies a callback method `func` (`ebas_read_example`
    in the example) which is called by the wrapper after the commandline
    arguments have been processed. The program logic is implemented in `func`
    in the caller's domain.

    `custom_args` defines the groups of arguments from the default ebas aruments
    which are needed by the calling program. For example

    - CONFIG adds the configuration file functionality
    - LOGGING adds the logfile aruments
    - TIME_CRIT adds time range argument
    - NASA_READ adds all arguments dealing with input files
    - ... many more

    `private_args` is a callback method in the callers domain which can set up
    additional arguments needed for the specific program.

    The commandline module in ebas can handle different levels of default values
    for all commandline arguments. There is a set of system default values for
    all arguments in the code.  
    When using the custom_args value CONFIG, the commandline module looks for a
    config file (called ebas.cfg by default) for reading default values which
    overrule the system default.  
    Thus, the user can set her own defaults. There is also the possibility to
    have config files in different places. The highest precedence has the file
    which is specified explicitly with ***full path name*** in the argument
    `--cfgfile` in the commanline, next is a config file in the current working
    directory, then in the user's home directory and finally a config file in
    the directory, the called program is located.

    All default values (system default or overruled by a config file) can of
    course be again overruled by using an explicit commandline argument.

    Settings in the config file can be done either on top level (Section EBAS4)
    for all programs, or for each program individually, or for a single program.
    Examples:
        ```
        [EBAS4]
        loglevfile=info
        ```
        Would generate by default a log file containing INFO messages or more severe for ALL programs.

        ```
        [EBAS4]

        [ebas_read_example]
        loglevfile=info
        ```
        Would generate by default this log file only for ebas_read_example.py
    """
    SUDOERS = ['paul', 'annehj', 'ebas', 'yong', 'richard', 'mye']

    def __init__(self, func, custom_args=None,  # pylint: disable-msg=R0913
                 private_args=None, help_description=None,
                 version='#no-version-number',
                 version_date=datetime.datetime.now(),
                 progname=None, def_args=None,
                 read_masterdata=True):
        NiluCommandline.__init__(
            self, func, custom_args=custom_args, private_args=private_args,
            help_description=help_description, version=version,
            version_date=version_date, progname=progname, def_args=def_args,
            config_main_section='EBAS4')
        self.dbh = None
        self.read_masterdata = read_masterdata
        self.versiontext = textwrap.dedent('''\n
            EBAS %(prog)s {0}
            Copyright (C) 2012-{1} NILU - Norwegian Institut for Air Reserch
            '''.format(self.version, self.version_date.year))
        self.logger = logging.getLogger('EbasCmdLine')

    def run(self):
        """
        Processes the arguments, then calls the `func` callback method.  
        Always ends the program with a DB rollback.
        Programs shoiuld commit on success before exiting.
        Programs crashing, or just exiting without commit will by this rollback
        mechanism clean up open TR entries.
        Works with ctrl-c, sysexit and all kinds of exceptions.
        Works also with --help and --version.
        """
        try:
            NiluCommandline.run(self)
        finally:
            if self.dbh:
                self.dbh.rollback()

    def preparse(self):
        NiluCommandline.preparse(self)
        if 'DB' in self.custom_args or 'DBWRITE' in self.custom_args:
            self.preparse_db()

    def set_defaults(self):
        """
        Set defaults.

        Parameters:
            None
        Returns:
           None
        """
        NiluCommandline.set_defaults(self)
        if 'CONFIG' in self.custom_args:
            self.def_args['cfgfile'] = 'ebas.cfg'
        if 'DB' in self.custom_args or 'DBWRITE' in self.custom_args:
            self.def_args['dbHost'] = 'prod-ebas-pg'
            self.def_args['db'] = 'ebas'
            self.def_args['dbUser'] = getpass.getuser()
            self.def_args['dbPasswd'] = None

    def preparse_db(self):
        """
        Setup db connection.
        Partially parse commandline arguments relevant for db, then connect
        according to setings.
        Needs to be pre-parsed in order to use master data from the DB to
        validate other arguments.
        """
        from ebas.db4 import EbasDb, DbError
        preparser = NiluArgumentParser(add_help=False)
        preparser.add_db_args()
        preparser.set_known_defaults(**self.def_args)
        self.args, self.unparsed = preparser.parse_known_args(
            args=self.unparsed, namespace=self.args)

        if self.args.nodb:
            self.logger.info('DB connection disabled by argument --nodb')
            return
        if not self.args.db or not self.args.dbHost:
            self.logger.error(
                'no DB server or database name specified, no DB connection '
                'possible')
            return
        while not self.args.dbUser:
            self.args.dbUser = input(
                'user name for database {0}: '.format(self.args.db))
        #while self.args.dbPasswd is None or self.args.dbPasswd == '':
        #    self.args.dbPasswd = getpass.getpass(
        #        'password for user {0} at database {1}: '
        #        .format(self.args.dbUser, self.args.db))
        try:
            self.dbh = EbasDb(self.args.dbHost, self.args.dbUser,
                              self.args.dbPasswd, self.args.db,
                              port=self.args.dbPort,
                              readonly=not 'DBWRITE' in self.custom_args,
                              progname=self.progname, progvers=self.version)
        except DbError as exp:
            self.logger.error(exp)
            self.dbh = None
        if self.dbh and self.read_masterdata:
            from ebas.domain.masterdata import read_all_caches_from_db
            read_all_caches_from_db(self.dbh)

    def add_custom_args(self, parser):
        """
        Add arguments for specific customized goals. E.g. custom parser
        'DS_CRIT' activates all arguments used to select datasets.

        Parameters:
            parser    parser object
        Returns:
            None
        """
        NiluCommandline.add_custom_args(self, parser)
        if 'DBWRITE' in self.custom_args:
            parser.add_db_args(nowrite=True, nocommit=True, transcomment=True)
        elif 'DB' in self.custom_args:
            parser.add_db_args(nowrite=False, nocommit=False,
                               transcomment=False)
        if 'DS_CRIT' in self.custom_args:
            parser_ds_crit_group = parser.add_argument_group(
                'dataset selection criteria')
            option_type = option_bool('AuxiliaryOption',
                                      'include-auxiliary',
                                      'exclude-auxiliary')
            parser_ds_crit_group.add_argument(
                '--include-auxiliary', '--exclude-auxiliary',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='include-auxiliary',
                dest='auxiliary',
                help='include or exclude auxiliary datasets')
            option_type = option_bool('NonAuxiliaryOption',
                                      'include-nonauxiliary',
                                      'exclude-nonauxiliary')
            parser_ds_crit_group.add_argument(
                '--include-nonauxiliary', '--exclude-nonauxiliary',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='include-nonauxiliary',
                dest='nonauxiliary',
                help='include or exclude non auxiliary datasets')
            option_type = option_bool('NRTOption',
                                      'include-nrt',
                                      'exclude-nrt')
            parser_ds_crit_group.add_argument(
                '--include-nrt', '--exclude-nrt',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='include-nrt',
                dest='nrt',
                help='include or exclude NRT datasets')
            option_type = option_bool('NonNRTOption',
                                      'include-non-nrt',
                                      'exclude-non-nrt')
            parser_ds_crit_group.add_argument(
                '--include-non-nrt', '--exclude-non-nrt',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='include-non-nrt',
                dest='nonnrt',
                help='include or exclude non NRT datasets')
            parser_ds_crit_group.add_argument('--dw_id', type=int,
                                              help='download id from database')
            parser_ds_crit_group.add_argument(
                '--setkey', '-k ',
                type=ParseIntegers(allow_scalar=True, allow_list=True,
                                   allow_range=True),
                default=None,
                help='dataset setkey; int, list of int or min-max')
            parser_ds_crit_group.add_argument(
                '--su_id',
                type=ParseIntegers(allow_scalar=True, allow_list=True,
                                   allow_range=True),
                default=None,
                help='submission identifier; int, list of int or min-max')
            parser_ds_crit_group.add_argument(
                '--station', '-s ',
                type=ValidateArgument(self, ValidateArgument.val_stationcode),
                default=None,
                help='station code or station code list')
            parser_ds_crit_group.add_argument(
                '--project', '-p ',
                type=ValidateArgument(self, ValidateArgument.val_project),
                default=None,
                help='project or project list')
            parser_ds_crit_group.add_argument(
                '--exproject',
                type=ValidateArgument(self, ValidateArgument.val_project),
                default=None,
                help='exclude project or project list (experimental, probably '
                'removed again')
            parser_ds_crit_group.add_argument(
                '--instrument', '-i ',
                type=ValidateArgument(self, ValidateArgument.val_instrument),
                default=None,
                help='instrument type or instrument type list')
            parser_ds_crit_group.add_argument(
                '--component', '-c ',
                type=ValidateArgument(self, ValidateArgument.val_component),
                default=None,
                help='component name or component name list. Strict synonyms '
                'are allowed, lookup names are accepted case insensitive as '
                'long as this is not in conflicht with other names.')
            parser_ds_crit_group.add_argument(
                '--matrix', '-m ',
                type=ValidateArgument(self, ValidateArgument.val_matrix),
                default=None,
                help='matrix name or matrix name list')
            parser_ds_crit_group.add_argument(
                '--group', '-g ',
                type=ValidateArgument(self, ValidateArgument.val_group),
                default=None,
                help='parameter group or parameter group list:\n' + 'bla')
            parser_ds_crit_group.add_argument(
                '--fi_ref',
                type=ValidateArgument(self, ValidateArgument.val_fi_ref),
                default=None,
                help='field instrument reference, or field instrument '
                     'reference list')
            parser_ds_crit_group.add_argument(
                '--me_ref',
                type=ValidateArgument(self, ValidateArgument.val_me_ref),
                default=None,
                help='method reference or method reference list')
            parser_ds_crit_group.add_argument(
                '--resolution',
                type=ValidateArgument(self, ValidateArgument.val_resolution),
                default=None,
                help='time resolution or time resolution list')
            parser_ds_crit_group.add_argument(
                '--statistics',
                type=ValidateArgument(self, ValidateArgument.val_statistics),
                default=None,
                help='statistical dimension or list of statistical dimensions')
            parser_ds_crit_group.add_argument(
                '--datalevel',
                type=ValidateArgument(self, ValidateArgument.val_datalevel),
                default=None,
                help='data level')
            parser_ds_crit_group.add_argument(
                '--characteristics',
                type=ValidateArgument(
                    self, ValidateArgument.val_characteristics),
                default=None,
                help='characteristics criteria: characteristic_type=value[,...]')
            # TODO: HDS, HVM, DP, SU, DC criteria
        if 'TIME_CRIT' in self.custom_args:
            parser_ds_crit_group = parser.add_argument_group('time selection')
            parser_ds_crit_group.add_argument(
                '--time', '-t ', type=parse_time_interval,
                default=DatetimeInterval(None, None),
                help=textwrap.dedent('''
                time criteria: format FROM[-TO].
                FROM and TO each has the format YYYY[-MM[-DD[THH[:MM[:SS]]]]].

                If only one time is specified, the period which is defined by\
                the precision of the time format will be chosen:
                2011-01 --> [2011-01-01T00:00:00,2011-02-01T00:00:00[\
                (i.e. the period January 2011).
                2011-11-23T11 --> [11:00, 12:00[ on 23 Nov.

                If both FROM and TO are given, the interval is defined by the\
                start of the FROM period and the end of the TO period:
                2011-01-2012-01-22 -->\
                [2011-01-01T00:00:00, 2012-01-23T00:00:00[

                The time criteria works by overlapping the given criteria with\
                the measurement sample sequence.
                When time is specified as YYYY or YYYY-MM, a slightly different\
                approach is used: sample sequences that overlap only partly\
                with the first or last sample in the sequence are not included.\
                (This is to prevent non-intuitive overlaps when one e.g.\
                07:00-07:00 sample overlaps from the last month or year of data)
                With other words: when specifying only YYYY or YYYY-MM, a hit\
                is only considered, if at least 1 _full_ sample is within the\
                respective year or month.'''))
        if 'STATE_CRIT' in self.custom_args:
            parser_ts_crit_group = parser.add_argument_group('database state')
            parser_ts_crit_group.add_argument(
                '--state', type=parse_time_instant, default=None,
                help=textwrap.dedent('''
                    state criteria: format YYYY-MM-DDTHH:MM:SS.MMM
                    Defines the (historic) state of the database which should \
                    be shown.'''))
            parser_ts_crit_group.add_argument(
                '--diff', type=parse_time_instant, default=None,
                help=textwrap.dedent('''
                    diff criteria: format YYYY-MM-DDTHH:MM:SS.MMM
                    Only data changed between this timestamp and the requested \
                    state will be considered.'''))
        if 'US_ID' in self.custom_args:
            username = getpass.getuser()
            if username in self.__class__.SUDOERS:
                parser_us_group = parser.add_argument_group('on behalf of...')
                parser_us_group.add_argument(
                    '--us_id', type=int, default=None,
                    help=textwrap.dedent('''
                        data access will be done on behalf of the specified \
                        EBAS user ID (US_ID). Use 1 for anonymous access'''))
        if 'NASA_READ' in self.custom_args:
            parser_nasa_group = parser.add_argument_group(
                'nasa ames reading options')
            parser_nasa_group.add_argument(
                '--ignore',
                type=ParseStrings(
                    allow_scalar=True, allow_list=True, allowed_values=[
                        'numformat', 'dx0', 'rescode', 'sample-duration',
                        'identical-values', 'revdate', 'parameter',
                        'flag-consistency', 'value-check', 'template-check']),
                default=[],
                help='ignore certain errors while reading (numformat, dx0, '
                'rescode, identical-values, flag-consistency, value-check)\n\n'
                'numformat: ignore if number format does not match missing '
                'value code\n\n'
                'dx0: allow DX=0 with regular data (DX!=0 will always raise an '
                'error if not correct)\n\n'
                'rescode: ignore resolution code errors\n\n'
                'sample-duration: ignore sample duration code errors\n\n'
                'identical-values: ignore errors related to all values of one '
                'variable being equal (e.g. all data missing for one variable, '
                'all values 0.0, or all values any other constant value). '
                'Those cases usually indicate an ERROR in the data. However if '
                'this is investigated and those data should be read, use this '
                'flag to downgrade the ERROR severity to WARNING. For the '
                'opposite (those cases are definitely identified as ERROR '
                'should not be read while the rest of the file should be read, '
                'consider the --skip-variables parameter)\n\n'
                'parameter: ignore validity of parameters (component names or '
                'component/matrix combination.\n\n'
                'flag-consistency: ignore checks for flag validity, flag '
                'consistency and value/flag consistency\n'
                'Those issues will be downgraded to WARNING.\n'
                '!!! Please be aware that this only applies to the reading of '
                'input files. For example, ebas_insert will _still_ come up '
                'with error messages regarding flag consistency and illegal '
                'flags!!!\n\n'
                'value-check: ignore value checks (boundaries and spikes)\n'
                'Those issues will be downgraded to WARNING.\n'
                '!!! Please be aware that this only applies to the reading of '
                'input files. For example, ebas_insert will _still_ come up '
                'with error messages regarding boundary and spike checks!!!\n\n')
            parser_nasa_group.add_argument(
                '--fix',
                type=ParseStrings(
                    allow_scalar=True, allow_list=True, allowed_values=[
                        'flag-consistency', 'overlap_set_start', 'bc211']),
                default=[],
                help='fix certain errors while reading (flag consistency, '
                'sample overlap, flag away boundary checks).\n\n'
                'flag-consistency: fix problems with flag consistency (e.g. '
                'missing flag for valid value, flag 100 for missing data, ...'
                '\n\noverlap_set_start: Errors with overlapping sample times '
                'are fixed by adjusting the start time of the second sample'
                '\n\nbc211: in case of boundary check violations, add flag 211')
            parser_nasa_group.add_argument(
                '--condense-messages',
                type=ParseIntegers(allow_scalar=True, allow_list=False,
                                   allow_range=False),
                default=8,
                help='Threshold for condensation of multiple occurrences of '
                'the same error or warning message. 0 turns off condensation '
                '(each single message will be logged)')
            parser_nasa_group.add_argument(
                '--skip-variables',
                type=ParseIntegers(allow_scalar=True, allow_list=True,
                                   allow_range=False),
                default=[],
                help='skip the variable(s) referenced by the variable '
                'number(s) while reading the file.\n'
                'Specify a single variable number or a comma separated list of '
                'variable numbers. '
                'Variable numbers start with 1 for the variable succeeding '
                'end_time (same numbering as in all WARNING/ERROR messages)\n'
                'start_time and end_time can not be skipped, numflags may not '
                'be skipped')
            parser_nasa_group.add_argument(
                '--skip-data', action='store_true',
                help='do not read data from the file, only header information '
                'and metadata.')
            option_type = option_bool('UnitConvertOption',
                                      'unitconvert-read',
                                      'no-unitconvert-read')
            parser_nasa_group.add_argument(
                '--unitconvert-read', '--no-unitconvert-read',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='unitconvert-read',
                dest='unitconvert_read',
                help='No conversion of units when reading a file.')
        elif 'OTHER_READ' in self.custom_args:
            parser_file_group = parser.add_argument_group(
                'file reading options')
            parser_file_group.add_argument(
                '--ignore',
                type=ParseStrings(allow_scalar=True, allow_list=True,
                                  allowed_values=['identical-values',
                                                  'parameter',
                                                  'flag-consistency',
                                                  'value-check']),
                default=[],
                help='ignore certain errors while reading (identical-values, '
                'flag-consistency, value-check)\n\n'
                'identical-values: ignore errors related to all values of one '
                'variable being equal (e.g. all data missing for one variable, '
                'all values 0.0, or all values any other constant value). '
                'Those cases usually indicate an ERROR in the data. However if '
                'this is investigated and those data should be read, use this '
                'flag to downgrade the ERROR severity to WARNING. For the '
                'opposite (those cases are definitely identified as ERROR '
                'should not be read while the rest of the file should be read, '
                'consider the --skip-variables parameter)\n\n'
                'parameter: ignore validity of parameters (component names or '
                'component/matrix combination.\n\n'
                'flag-consistency: ignore checks for flag validity, flag '
                'consistency and value/flag consistency\n'
                'Those issues will be downgraded to WARNING.\n'
                '!!! Please be aware that this only applies to the reading of '
                'input files. For example, ebas_insert will _still_ come up '
                'with error messages regarding flag consistency and illegal '
                'flags!!!\n\n'
                'value-check: ignore value checks (boundaries and spikes)\n'
                'Those issues will be downgraded to WARNING.\n'
                '!!! Please be aware that this only applies to the reading of '
                'input files. For example, ebas_insert will _still_ come up '
                'with error messages regarding boundary and spike checks!!!\n\n')
            option_type = option_bool('UnitConvertOption',
                                      'unitconvert-read',
                                      'no-unitconvert-read')
            parser_file_group.add_argument(
                '--unitconvert-read', '--no-unitconvert-read',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='unitconvert-read',
                dest='unitconvert_read',
                help='No conversion of units when reading a file.')
        if 'FILE_OUTPUT' in self.custom_args or \
                'FILE_OUTPUT_KEEPCOLUMNS' in self.custom_args:
            parser_output_group = parser.add_argument_group(
                'file output options')
            parser_output_group.add_argument(
                '--format', type=EbasIOFormatOption,
                default=EbasIOFormatOption('NasaAmes'),
                help='file format for output: ({})'.format(
                    ', '.join(
                        [str(x) for x in EbasIOFormatOption.legal_options()])))
            if 'FILE_OUTPUT_KEEPCOLUMNS' in self.custom_args:
                option_type = option_int(
                    'MulticolumnOption', {
                        'multicolumn': EBAS_IOSTYLE_MULTICOLUMN,
                        'singlecolumn': EBAS_IOSTYLE_SINGLECOLUMN,
                        'multicolumn-precipitation':
                            EBAS_IOSTYLE_MULTICOLUMN_PRECIP,
                        'keep-columns': EBAS_IOSTYLE_KEEP,
                    })
                parser_output_group.add_argument(
                    '--multicolumn', '--singlecolumn',
                    '--multicolumn-precipitation', '--keep-columns',
                    type=option_type,
                    action=ExclusiveMultiswithAction,
                    default='keep-columns',
                    dest='style',
                    help='singlecolumn output or multicolumn output '
                         '(one or more variables per file\n'
                         '--multicolumn-precipitation: generally singlecolumn '
                         'output, but add precipitation_amount as additional '
                         'variables\n'
                         '--keep-columns: keep the columns as they are in the '
                         'source file')
            else:
                option_type = option_int(
                    'MulticolumnOption', {
                        'multicolumn': EBAS_IOSTYLE_MULTICOLUMN,
                        'singlecolumn': EBAS_IOSTYLE_SINGLECOLUMN,
                        'multicolumn-precipitation':
                            EBAS_IOSTYLE_MULTICOLUMN_PRECIP,
                    })
                parser_output_group.add_argument(
                    '--multicolumn', '--singlecolumn',
                    '--multicolumn-precipitation',
                    type=option_type,
                    action=ExclusiveMultiswithAction,
                    default='multicolumn',
                    dest='style',
                    help='singlecolumn output or multicolumn output '
                         '(one or more variables per file\n'
                         '--multicolumn-precipitation: generally singlecolumn '
                         'output, but add precipitation_amount as additional '
                         'variables')
            option_type = option_bool('LongTimeseriesOption',
                                      'long_timeseries', 'no-long_timeseries')
            parser_output_group.add_argument(
                '--long_timeseries', '--no-long_timeseries',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='no-long_timeseries',
                dest='long_timeseries',
                help='make long timeseries, even when metadata change. Only '
                     'supported for file formats which support changing '
                     'metadata (OPenDAP, NetCDF)')
            option_type = option_bool('CreateFilesOption',
                                      'createfiles', 'stdout')
            parser_output_group.add_argument(
                '--createfiles', '--stdout',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='createfiles',
                dest='createfiles',
                help='create files or output to stdout')
            option_type = option_bool('XmlWrapOption',
                                      'xmlwrap', 'no-xmlwrap')
            parser_output_group.add_argument(
                '--xmlwrap', '--no-xmlwrap',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='no-xmlwrap',
                dest='xmlwrap',
                help='wrap output in xml containers (only for --stdout)')
            option_type = option_bool('UnitConvertOption',
                                      'unitconvert-write',
                                      'no-unitconvert-write')
            parser_output_group.add_argument(
                '--unitconvert-write', '--no-unitconvert-write',
                type=option_type,
                action=ExclusiveMultiswithAction,
                default='unitconvert-write',
                dest='unitconvert_write',
                help='For some parameters, additional variables with different '
                     'units will be generated on export (e.g. VOCs or ozone in '
                     'nmol/mol, nitrate and sulphate in ug/m3, ...).\n\n'
                     'With the option --no-unitconvert-write, the additional '
                     'variables will not be exported. Only the variables with '
                     'the default units stored in EBAS will be exported.')
            parser_output_group.add_argument(
                '--destdir', action=ParseDestDirAction,
                help='set output directory for files')

            parser_output_group.add_argument(
                '--flags',
                choices=EbasIOFlagOption.legal_options(), action=None,
                default=EbasIOFlagOption('one-or-all'), type=EbasIOFlagOption,
                help=textwrap.dedent('''
                    flag columns style:

                    * one-or-all (default):
                    If all variables share the same sequence of flags throughout\
                    the whole file, use one flag column as last column.
                    Else, one flag column per variable is used.
                    This is the default behavior starting from EBAS 3.0.

                    * compress:
                    If multiple variables share the same sequence of flags\
                    throughout the whole file, one flag column after this group\
                    of variables is used.
                    This produces files as narrow as possible without losing any flag\
                    information.
                    This used to be the default behavior up to EBAS 2.2.

                    * all
                    All variables get a dedicated flag column.

                    * none
                    No flag columns are exported. Invalid or missing data are both\
                    reported as MISSING value. This should be used very carfully,\
                    as information is LOST on export!
                    Intended for non expert uses, as the easiest approach to process\
                    only valid data, without bothering about the EBAS flag system.
                    Note: Detection limit values (flag 781) are exported as\
                    value/2.0 (only in this case, when no flag information is \
                    extracted).

                    As a general rule, a flag column applies ALWAYS to all preceding\
                    variables after the previous flag column.'''))
            parser_output_group.add_argument(
                '--fileindex', type=parse_fileindex,
                help='file path and name for ebas file index database (sqlite3).'
                     'Prepend a plus sign (+) to the filename in order to add to an '
                     'existing database instead of creating a new one.')

    def get_custom_args(self, custom_parser):
        """
        Get custom parser arguments in a separate dictionary.

        Parameters:
            custom_parser    parser group name
        Returns:
            {}
        """
        ret = DataObject()
        translate = \
            {
                'DS_CRIT':
                {
                    'dw_id': 'DW_ID',
                    'su_id': 'SU_ID',
                    'setkey': 'DS_SETKEY',
                    'station': 'ST_STATION_CODE',
                    'project': 'PR_ACRONYM',
                    'exproject': '!PR_ACRONYM',
                    'instrument': 'FT_TYPE',
                    'component': 'CO_COMP_NAME',
                    'matrix': 'MA_MATRIX_NAME',
                    'group': 'PG_NAME',
                    'fi_ref': 'FI_REF',
                    'me_ref': 'ME_REF',
                    'resolution': 'DS_RESCODE',
                    'statistics': 'SC_STATISTIC_CODE',
                    'datalevel': 'DL_DATA_LEVEL',
                },
                'FILE_OUTPUT':
                {
                    'format': 'outformat',
                    'style': 'outstyle',
                    'createfiles': 'createfiles',
                    'destdir': 'destdir',
                    'xmlwrap': 'xmlwrap',
                    'flags': 'flags',
                    'fileindex': 'indexdb',
                    'unitconvert_write': 'gen_converted',
                    'long_timeseries': 'long_timeseries',
                }
            }
        if custom_parser == 'NASA_READ':
            # keyword parameters for EbasNasaAmes init:
            ret['nas_init'] = DataObject()
            ret['nas_init']['condense_messages'] = self.args.condense_messages
            # keyword parameters for EbasNasaAmes read:
            ret['nas_read'] = DataObject()
            ret['nas_read']['ignore_numformat'] = False
            if 'numformat' in self.args.ignore:
                ret['nas_read']['ignore_numformat'] = True
            ret['nas_read']['ignore_dx0'] = False
            if 'dx0' in self.args.ignore:
                ret['nas_read']['ignore_dx0'] = True
            ret['nas_read']['ignore_revdate'] = False
            if 'revdate' in self.args.ignore:
                ret['nas_read']['ignore_revdate'] = True
            ret['nas_read']['ignore_rescode'] = False
            if 'rescode' in self.args.ignore:
                ret['nas_read']['ignore_rescode'] = True
            ret['nas_read']['ignore_sampleduration'] = False
            if 'sample-duration' in self.args.ignore:
                ret['nas_read']['ignore_sampleduration'] = True
            ret['nas_read']['ignore_identicalvalues'] = False
            if 'identical-values' in self.args.ignore:
                ret['nas_read']['ignore_identicalvalues'] = True
            ret['nas_read']['ignore_parameter'] = False
            if 'parameter' in self.args.ignore:
                ret['nas_read']['ignore_parameter'] = True
            ret['nas_read']['ignore_flagconsistency'] = False
            if 'flag-consistency' in self.args.ignore:
                ret['nas_read']['ignore_flagconsistency'] = True
            ret['nas_read']['ignore_valuecheck'] = False
            if 'value-check' in self.args.ignore:
                ret['nas_read']['ignore_valuecheck'] = True
            if 'template-check' in self.args.ignore:
                ret['nas_read']['ignore_templatecheck'] = True
            ret['nas_read']['fix_flagconsistency'] = False
            if 'flag-consistency' in self.args.fix:
                ret['nas_read']['fix_flagconsistency'] = True
            ret['nas_read']['fix_overlap_set_start'] = False
            if 'overlap_set_start' in self.args.fix:
                ret['nas_read']['fix_overlap_set_start'] = True
            ret['nas_read']['fix_bc211'] = False
            if 'bc211' in self.args.fix:
                ret['nas_read']['fix_bc211'] = True
            ret['nas_read']['skip_variables'] = \
                [self.args.skip_variables] \
                    if isinstance(self.args.skip_variables, int) \
                    else self.args.skip_variables
            ret['nas_read']['skip_data'] = self.args.skip_data
            # reversed logic for skip_unitconvert
            ret['nas_read']['skip_unitconvert'] = not self.args.unitconvert_read
        elif custom_parser == 'OTHER_READ':
            # keyword parameters for EbasNasaAmes init:
            ret['file_init'] = DataObject()
            # keyword parameters for EbasNasaAmes read:
            ret['file_read'] = DataObject()
            ret['file_read']['ignore_identicalvalues'] = False
            if 'identical-values' in self.args.ignore:
                ret['file_read']['ignore_identicalvalues'] = True
            ret['file_read']['ignore_parameter'] = False
            if 'parameter' in self.args.ignore:
                ret['file_read']['ignore_parameter'] = True
            ret['file_read']['ignore_flagconsistency'] = False
            if 'flag-consistency' in self.args.ignore:
                ret['file_read']['ignore_flagconsistency'] = True
            ret['file_read']['ignore_valuecheck'] = False
            if 'value-check' in self.args.ignore:
                ret['file_read']['ignore_valuecheck'] = True
            # reversed logic for skip_unitconvert
            ret['file_read']['skip_unitconvert'] = not self.args.unitconvert_read
        else:
            for argname, critname in list(translate[custom_parser].items()):
                if argname in self.args.__dict__ and \
                        self.args.__dict__[argname] is not None:
                    ret[critname] = self.args.__dict__[argname]
        # additional elemet for DS_CRIT: add single characteristics
        if custom_parser == 'DS_CRIT' and self.args.characteristics:
            for key in self.args.characteristics.keys():
                ret[key] = self.args.characteristics[key]
        return ret

class ValidateArgument(ParseStrings):
    """
    Argument validation. Based on ParseStrings.
    """

    def __init__(self, ebasargs, validation):
        ParseStrings.__init__(self, allow_scalar=True, allow_list=True)
        self.ebasargs = ebasargs
        self.validation = validation

    def __call__(self, arguments):
        """
        Validation for station code or station code list.
        Parameters:
            string   cmd-line parameter string to be checked
        Reurns:
            string   in case of a single station code
            [string, ...]
                     in case of a comma separated list of station codes
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        return self.validation(self, arguments)

    def val_stationcode(self, station_codes):
        """
        Validation for station codes.
        Parameters:
            station_codes   cmd-line parameter string to be checked
        Reurns:
            string   in case of a single station code
            [string, ...]
                     in case of a comma separated list of station codes
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        def _check_stationcode(code):
            """
            Checks single station coode fromcommand line.
            Parameters:
                code     station code as entered at commandline
            Returns:
                code     modified station code (maybe appended '%' wildcard)
            Raises:
                argparse.ArgumentTypeError in case of syntax error or no
                matching station
            """
            if re.search('%', code):
                search = code
                search = re.sub('%', '.*', search)
            elif re.match('[A-Z][A-Z]$', code) or \
                 re.match('[A-Z][A-Z][0-9][0-9][0-9][0-9]$', code):
                search = code + '.*'
                code += '%'
            elif re.match('[A-Z][A-Z][0-9][0-9][0-9][0-9][A-Z]$', code):
                search = code
            else:
                raise argparse.ArgumentTypeError(
                    "station code syntax error '{}'".format(code))
            if len(list(st_.lookup_stationcode(search))) < 1:
                raise argparse.ArgumentTypeError(
                    "No match for station code '{}'".format(code))
            return code


        from ebas.domain.masterdata.st import EbasMasterST
        st_ = EbasMasterST(self.ebasargs.dbh)
        arg = self.parse(station_codes)
        if isinstance(arg, six.string_types):
            res = _check_stationcode(arg)
            return res
        elif isinstance(arg, list):
            for i in range(len(arg)):
                arg[i] = _check_stationcode(arg[i])
            return arg
        else:
            raise argparse.ArgumentTypeError('station code or station code '
                                             'list expected')

    def val_component(self, comp_name):
        """
        Validation for component or or component list.
        Parameters:
            string   cmd-line parameter string to be checked
        Reurns:
            string   in case of a single component
            [string, ...]
                     in case of a comma separated list of components
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        from ebas.domain.masterdata.cy import EbasMasterCY
        from ebas.domain import EbasDomainError
        cy_ = EbasMasterCY(self.ebasargs.dbh)
        arg = self.parse(comp_name)
        if isinstance(arg, six.string_types):
            try:
                return cy_.lookup_synonym_strict(arg, case_sensitive=False)
            except EbasDomainError as expt:
                raise argparse.ArgumentTypeError(str(expt))
        elif isinstance(arg, list):
            for i, string in enumerate(arg):
                try:
                    arg[i] = cy_.lookup_synonym_strict(string,
                                                       case_sensitive=False)
                except EbasDomainError as expt:
                    raise argparse.ArgumentTypeError(str(expt))
            return arg
        else:
            raise argparse.ArgumentTypeError('component or component list '
                                             'expected')

    def val_project(self, projects):
        """
        Validation for project or project list.
        Parameters:
            projects   cmd-line parameter string to be checked
        Reurns:
            string   in case of a single project
            [string, ...]
                     in case of a comma separated list of projects
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        from ebas.domain.masterdata.pr import EbasMasterPR
        from ebas.domain import EbasDomainError
        pr_ = EbasMasterPR(self.ebasargs.dbh)
        arg = self.parse(projects)
        if isinstance(arg, six.string_types):
            try:
                return pr_.lookup_project(arg)
            except EbasDomainError as expt:
                raise argparse.ArgumentTypeError(str(expt))
        elif isinstance(arg, list):
            for i, string in enumerate(arg):
                try:
                    arg[i] = pr_.lookup_project(string)
                except EbasDomainError as expt:
                    raise argparse.ArgumentTypeError(str(expt))
            return arg
        else:
            raise argparse.ArgumentTypeError('project or project list '
                                             'expected')

    def val_datalevel(self, datalevel):
        """
        Validation for datalevel.
        Parameters:
            datalevel   cmd-line parameter string to be checked
        Reurns:
            string   datalevel, checked and OK
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        from ebas.domain.masterdata.dl import EbasMasterDL
        dl_ = EbasMasterDL(self.ebasargs.dbh)
        arg = self.parse(datalevel)
        if isinstance(arg, six.string_types):
            try:
                return dl_[arg].DL_DATA_LEVEL
            except KeyError:
                raise argparse.ArgumentTypeError(
                    "Datalevel '{}' not defined".format(arg))
        elif isinstance(arg, list):
            for i, string in enumerate(arg):
                try:
                    arg[i] = dl_[string].DL_DATA_LEVEL
                except KeyError:
                    raise argparse.ArgumentTypeError(
                        "Datalevel '{}' not defined".format(string))
            return arg
        else:
            raise argparse.ArgumentTypeError(
                'datalevel or datalevel list expected')

    def val_instrument(self, instruments):
        """
        Validation for instrument type or instrument type list.
        Parameters:
            instruments   cmd-line parameter string to be checked
        Reurns:
            string   in case of a single instrument type
            [string, ...]
                     in case of a comma separated list of instrument types
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        arg = self.parse(instruments)
        return arg
        # TODO ...

    def val_matrix(self, matrices):
        """
        Validation for matrix or matrix list.
        Parameters:
            matrices   cmd-line parameter string to be checked
        Reurns:
            string   in case of a single matrix
            [string, ...]
                     in case of a comma separated list of matrices
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        arg = self.parse(matrices)
        return arg
        # TODO ...

    def val_group(self, groups):
        """
        Validation for parameter group.
        Parameters:
            groups   cmd-line parameter string to be checked
        Reurns:
            string   in case of a group
            [string, ...]
                     in case of a comma separated list of groups
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        arg = self.parse(groups)
        return arg
        # TODO ...

    def val_fi_ref(self, fi_refs):
        """
        Validation for instrument references.
        Parameters:
            fi_refs   cmd-line parameter string to be checked
        Reurns:
            string   in case of one fi_ref
            [string, ...]
                     in case of a comma separated list of fi_refs
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        arg = self.parse(fi_refs)
        return arg
        # TODO ...

    def val_me_ref(self, me_refs):
        """
        Validation for method references.
        Parameters:
            me_refs   cmd-line parameter string to be checked
        Reurns:
            string   in case of one me_ref
            [string, ...]
                     in case of a comma separated list of me_refs
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        arg = self.parse(me_refs)
        return arg
        # TODO ...

    def val_resolution(self, rescodes):
        """
        Validation for resolution codes.
        Parameters:
            rescodes   cmd-line parameter string to be checked
        Reurns:
            string   in case of one resolution code
            [string, ...]
                     in case of a comma separated list of resolution codes
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        arg = self.parse(rescodes)
        return arg
        # TODO ...

    def val_statistics(self, statistics):
        """
        Validation for statistic codes.
        Parameters:
            statistics   cmd-line parameter string to be checked
        Reurns:
            string   in case of one statistic code
            [string, ...]
                     in case of a comma separated list of statistic codes
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        arg = self.parse(statistics)
        return arg
        # TODO ...

    def val_characteristics(self, characteristics):
        """
        Validation for statistic codes.
        Parameters:
            characteristics   cmd-line parameter string to be checked
        Reurns:
            string   in case of one statistic code
            [string, ...]
                     in case of a comma separated list of statistic codes
        Raises:
            argparse.ArgumentTypeError
                     in case of argument error
        """
        arg = self.parse(characteristics)
        ret = {}
        for char in arg.split(','):
            tag, val = char.split('=')
            ret[tag] = val
        return ret

def option_bool(classname, truevalue, falsevalue):
    """
    Class factory, only used to translate bool value to text and vice versa.
    """
    class OptionBool(int):
        """
        The class itself, needs to be int based (bool cannot be used as base
        class).
        """
        TRUEVALUE = truevalue
        FALSEVALUE = falsevalue

        def __new__(cls, val):
            if val == cls.TRUEVALUE:
                return super(OptionBool, cls).__new__(cls, True)
            if val == cls.FALSEVALUE:
                return super(OptionBool, cls).__new__(cls, False)
            return super(OptionBool, cls).__new__(cls, val)
        def __repr__(self):
            return "{}({})".format(self.__class__.__name__, str(self))
        def __str__(self):
            if self:
                return self.__class__.TRUEVALUE
            return self.__class__.FALSEVALUE
    OptionBool.__name__ = classname
    OptionBool.__qualname__ = classname
    return OptionBool

def option_int(classname, text_to_val):
    """
    Class factory, only used to translate bool value to text and vice versa.
    """
    class OptionInt(int):
        """
        The class itself.
        """
        TEXT_TO_VAL = text_to_val
        VAL_TO_TEXT = {text_to_val[x]: x for x in text_to_val.keys()}

        def __new__(cls, text):
            return super(OptionInt, cls).__new__(
                cls, cls.TEXT_TO_VAL[text])
        def __repr__(self):
            return "{}({})".format(self.__class__.__name__, str(self))
        def __str__(self):
            return self.__class__.VAL_TO_TEXT[self]
    OptionInt.__name__ = classname
    OptionInt.__qualname__ = classname
    return OptionInt

class ParseDestDirAction(argparse.Action):  # pylint: disable-msg=R0903
    # R0903: ParseDestDirAction: Too few public methods
    #  this is due to argparse.Action
    """
    Parser action for --destdir argument: is only allowed when --createfiles is
    set.
    """
    def __call__(self, parser, namespace, values, _option_string=None):
        createfiles = getattr(namespace, 'createfiles', False)
        if not createfiles:
            parser.error("--destdir is only allowed after --createfiles!")
        else:
            setattr(namespace, self.dest, values)

def parse_fileindex(string):
    """
    Parser for fileindex. Returns a IndexDb object.

    Parameters:
       string   cmd-line parameter string to be parsed.
    Returns:
       IndexDb object
    Raises:
        argparse.ArgumentTypeError
    """
    if not string:
        return None
    append = False
    if string.startswith('+'):
        append = True
        string = string[1:]
    try:
        indexdb = IndexDb(string)
    except OperationalError as excpt:
        if excpt.message == 'unable to open database file':
            raise argparse.ArgumentTypeError("can not open index db {}".format(
                string))
        else:
            raise
    try:
        indexdb.create_tables()
    except OperationalError as excpt:
        if re.match('table .* already exists', excpt.message):
            if not append:
                raise argparse.ArgumentTypeError(
                    "index db {} exists already".format(string))
            # if append, ignore
        else:
            raise
    return indexdb


# output routines shared by different programs:

def dslist_info(dslist):
    """
    Interactive information on a result ds list.
    Parameters:
        dslist
    Returns:
        None
    """
    t_overv = "Overview of different metadata"
    t_list = "List of all dataset metadata"
    t_verb = "Verbose information on all datasets"
    t_sverb = "Super-verbose information on all datasets"
    t_exit = "Exit dataset information"
    choice = ''
    while choice != 'Exit':
        choice = input("\nPlease make your choice:\n " + \
            t_overv + "\n " + t_list + "\n " + t_verb + "\n " + \
            t_sverb + "\n " + t_exit + "\n ")
        print("")
        if t_overv.lower().startswith(choice.lower()):
            for str_ in dslist.metadata_to_string(verbosity=-1):
                print(str_)
        if t_list.lower().startswith(choice.lower()):
            for str_ in dslist.metadata_to_string(verbosity=0):
                print(str_)
        elif t_verb.lower().startswith(choice.lower()):
            for str_ in dslist.metadata_to_string(verbosity=1):
                print(str_)
        elif t_sverb.lower().startswith(choice.lower()):
            for str_ in dslist.metadata_to_string(verbosity=2):
                print(str_)
        if t_exit.lower().startswith(choice.lower()):
            choice = "Exit"

def _confirmation_issues(dslist, verb):
    """
    Check if confirmation is needed and log warnings about thresholds exeeded.

    Confirmation is needed if there is a high risk that the user made
    a mistake when generating the commandline arguments (number of datasets,
    multiple instruments...).
    Parameters:
        dslist       list of EbasDomDS objects to be affected
        interactive  user interactive mode (bool)
        verb         verb to be used for the action intended (delete,
                     change, ...)
                     The verb needs to be defined in two different grammatical
                     forms, passed as a tuple:
                         (second person singular simple present tense active,
                          third person plural future tense passive)
                     Examples: (delete, deleted), (change, changed)
    Returns:
        issues  number of issues discovered (>0 --> confirmation is needed)
    """
    issues = []

    stations = set([x.ST_STATION_CODE for x in dslist])
    if len(stations) > 1:
        issues.append("You're about to {} data from {} stations: {}"
                      .format(verb[0], len(stations),
                              ", ".join(sorted(list(stations)))))
    instruments = set([x.FI_REF for x in dslist])
    if len(instruments) > 1:
        issues.append("You're about to {} data from {} instruments: {}"
                      .format(verb[0], len(instruments),
                              ", ".join(sorted(list(instruments)))))
    nrt = [ds.NRT for ds in dslist if ds.NRT]
    if nrt:
        issues.append("You're selection contains {} NRT datasets. "
                      .format(len(nrt)) +
                      "Data will be {} permanently.".format(verb[1]))
    return issues

def confirm_changes(dslist, interactive, verb=('delete', 'deleted')):
    """
    Generates warnings if there is a high risk that the user made a
    mistake when generating the commandline arguments (number of datasets,
    multiple instruments...).

    Parameters:
        dslist       list of EbasDomDS objects to be affected
        interactive  user interactive mode (bool)
        verb         verb to be used for the action intended (delete,
                     change, ...)
                     The verb needs to be defined in two different grammatical
                     forms, passed as a tuple:
                         (second person singular simple present tense active,
                          third person plural future tense passive)
                     Examples: (delete, deleted), (change, changed)
    Returns:
        True: go ahead
        False: stop
    """
    logger = logging.getLogger('EbasCmdLine')
    messages = _confirmation_issues(dslist, verb)
    for msg in messages:
        if interactive:
            logger.warning(msg)
        else:
            logger.error(msg)
    issues = len(messages)
    if issues and interactive:
        choice = ''
        while choice not in ('yes', 'no'):
            yes = "Yes, I am sure. Please go ahead!"
            no_ = "No, actually I am not so sure. Please get me out here!"
            info = "I am hesitant. Please give me more information!"
            choice = input(
                "\nPlease read the {}{} of warning above. "
                .format(issues if issues > 1 else '',
                        " lines" if issues > 1 else "line") +
                "Are you sure you want to {}?\n ".format(verb[0]) +
                yes + "\n " + no_ + "\n " + info + "\n ")
            if yes.lower().startswith(choice.lower()):
                choice = "yes"
            if no_.lower().startswith(choice.lower()):
                choice = "no"
            if info.lower().startswith(choice.lower()):
                dslist_info(dslist)
        return choice == "yes"
    elif issues:
        logger.info('User interaction impossible, comntact the EBAS '
                    'admin team')
        return False
    # no issues:
    return True

