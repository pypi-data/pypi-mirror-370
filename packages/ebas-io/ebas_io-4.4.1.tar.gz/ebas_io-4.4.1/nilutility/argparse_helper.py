"""
nilu/argparse_helper.py
$Id: argparse_helper.py 2721 2021-10-22 23:02:49Z pe $

Module with argparse helper functions.
This module is just a helper for the default python argparse module.
It helps setting up argument parsers.

Features:
- Help Formatter that deals reasonably with newlines in help texts.
- Argument parsers for various purposes
  (datetime, interval, filename, loglevels etc)

Synopsis:


History:
V.1.0.0  2012-12.-10 pe  initial version

"""

import argparse
import logging
from . import logging_helper
import re
import textwrap
import datetime
from nilutility.datetime_helper import DatetimeInterval
from dateutil.relativedelta import relativedelta
from nilutility.datatypes import datetimeprec
from nilutility.datetime_helper import datetime_parse_iso8601

LOGLEVELNAMES = {
    'silent':   logging.CRITICAL + 1,
    'critical': logging.CRITICAL,
    'errors':   logging.ERROR,
    'warnings': logging.WARNING,
    'info+':    logging_helper.INFO_PLUS,
    'info':     logging.INFO,
    'info-':    logging_helper.INFO_MINUS,
    'debug':    logging.DEBUG}

LOGLEVELSTRING = ', '.join([k[0] for k in \
    sorted(list(LOGLEVELNAMES.items()), key=lambda lev: lev[1], reverse=True)])

class NiluArgumentParser(argparse.ArgumentParser):  # pylint: disable=R0904
    # R0904: Too many public methods
    #  --> this is due to base class argparse.ArgumentParser
    """
    Customizes the default argument parser provided by argparse.

    This class extends the ArgumentParser class by thi method:
        set_known_defaults()

    The default implementation substitutes all whitespaces (including \n)
    with a blank, which results hard to read help text for long sections.
    Implementations in RawDescriptionHelpFormatter and RawTextHelpFormatter
    go to far and do not change the format of help text at all.
    """
    def __init__(self, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, **kwargs)
        self.formatter_class = HelpFormatterWrapButKeepNewlines

    def set_known_defaults(self, **kwargs):
        """
        Sets defaults like the standard set_defaults method, but does __NOT__
        set defaults for unknown arguments.
        """
        for action in self._actions:
            if action.dest in kwargs:
                action.default = kwargs[action.dest]

    def add_config_arguments(self, cfgfile=True):
        """
        Add configuration relevant arguments to parser.
        Parameters:
            parser     parser object
        Returns:
            None
        """
        parser_cfg_group = self.add_argument_group('configuration options')
        if cfgfile:
            parser_cfg_group.add_argument('--cfgfile',
                                          help='configuration file to be used')

    def add_logging_arguments(self, logfile=True,
                              loglevconsole=True, def_loglevconsole='silent',
                              loglevfile=True, def_loglevfile='silent',
                              profile=True):
        # pylint: disable=R0913
        #  R0913: Too many arguments
        """
        Adds a group for logging specific arguments.
        Parameters:
            parser             existing argpase.parser object
            logfile            Bool; True if argument '--logfile' should be
                               added
            loglevconsole      Bool; True if argument '--loglevconsole' should
                               be added
            def_loglevconsole  string; default log level forconsole logging
                               ('silent', 'critical', 'errors', 'warnings',
                                'info', 'debug')
            loglevfile         Bool; True if argument '--loglevfile' should be
                               added
            def_loglevfile     string; default log level for logfiles
                               ('silent', 'critical', 'errors', 'warnings',
                                'info', 'debug')
        Returns:
            parser_log_group   argument group object
        """
        parser_log_group = self.add_argument_group('logging and debug options')
        if loglevconsole:
            parser_log_group.add_argument(
                '--loglevconsole', type=parse_loglevel_args,
                default=def_loglevconsole,
                help='log level for console output ({0})'
                .format(LOGLEVELSTRING))
        if loglevfile:
            parser_log_group.add_argument(
                '--loglevfile', type=parse_loglevel_args,
                default=def_loglevfile,
                help='log level for logfile output ({0})'
                .format(LOGLEVELSTRING))
        if logfile:
            parser_log_group.add_argument(
                '--logfile', type=str, default=None,
                help='Logfile name (including path)')
        if profile:
            parser_log_group.add_argument(
                '--profile', action='store_true',
                help='activate code profiling (developer only)')
        return parser_log_group

    def add_db_args(self, nowrite=False, nocommit=False, transcomment=False):
        """
        Add a group for DB relevant arguments to parser.
        Parameters:
            nowrite       include nowrite option
            nocommit      include nocommit option
            transcomment  include transaction comment argument
        Returns:
            None
        """
        parser_db_group = self.add_argument_group(
            'database parameters',
            textwrap.dedent('''\
            Database user and password can also be fetched from your .netrc
            file (machine=ebas_db).
            In this case do not specify --dbUser and --dbPasswd as an \
            argument.'''))
        parser_db_group.add_argument(
            '--nodb', action='store_true',
            help='do not connect to database (work offline, useful for e.g. '
                 '--version, --help etc. when the database is not reachable)')
        parser_db_group.add_argument(
            '--dbHost', type=str, default=None,
            help='db host name or IP')
        parser_db_group.add_argument(
            '--dbPort', type=int, default=None,
            help='IP port for DB connection')
        parser_db_group.add_argument(
            '--db', type=str, default=None,
            help='DB to be used.')
        parser_db_group.add_argument(
            '--dbUser', type=str, default=None,
            help='database username.')
        parser_db_group.add_argument(
            '--dbPasswd', type=str, default=None,
            help='database password. discouraged, more secure hidden input '
                 'if not set on commandline')
        if nowrite:
            parser_db_group.add_argument(
                '--nowrite', action='store_true',
                help='do not write to DB, just work on memory objects '
                '(test/debug)')
        if nocommit:
            parser_db_group.add_argument(
                '--nocommit', action='store_true',
                help='write but do not commit to DB (test/debug)')
        if transcomment:
            parser_db_group.add_argument(
                '--transcomment', type=str, default=None,
                help='transaction comment (archived in database)')


class ToggleAction(argparse.Action):  # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Argparse action class. Implements toggeling a boolean option by
    using the --xxx / --no-xxx / --reset-xxx logic.
    """

    def __init__(self, option_strings, dest,
                 default=None, required=False,
                 type=bool,
                 help=None):
        """
        Initialize the object.
        """
        super(ToggleAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=default,
            type=type,
            required=required,
            help=help)

        if len(option_strings) != 2:
            raise RuntimeError("ToggleAction needs 2 option strings")
        if sum([x.startswith('--include-') for x in option_strings]) == 1 and \
           sum([x.startswith('--exclude-') for x in option_strings]) == 1:
            # exactly 1 argument starts with --include- and one with --exclude-
            self.evaluate = self.evaluate_include_exclude
        elif sum([x.startswith('--no-') for x in option_strings]) == 1:
            # exactly 1 argument starts with --no-
            self.evaluate = self.evaluate_no_with_dash
        elif sum([x.startswith('--no') for x in option_strings]) == 1:
            # exactly 1 argument starts with --no
            self.evaluate = self.evaluate_no_without_dash
        else:
            # use the first action for true, the second for false:
            self.evaluate = lambda o: True if o == option_strings[0] else False

    def __call__(self, parser, namespace, values,  # @UnusedVariable
                 option_string=None):
        """
        Perform the action.
        """
        if option_string.startswith('--reset-'):
            setattr(namespace, self.dest, None)
        else:
            setattr(
                namespace, self.dest, self.type(self.evaluate(option_string)))

    def evaluate_include_exclude(self, option_string):
        """
        Evaluate the options string for the --include-xxx / --exclude-xxx mode
        of operation.

        Parameter:
            option_string   otpion string to be evaluated

        Returns:
            True/False
        """
        if option_string.startswith('--include-'):
            return True
        if option_string.startswith('--exclude-'):
            return False
        raise RuntimeError('option string inot recognized')

    def evaluate_no_with_dash(self, option_string):
        """
        Evaluate the options string for the --xxx / --no-xxx mode of operation.

        Parameter:
            option_string   otpion string to be evaluated

        Returns:
            True/False
        """
        if option_string.startswith('--no-'):
            return False
        else:
            return True

    def evaluate_no_without_dash(self, option_string):
        """
        Evaluate the options string for the --xxx / --noxxx mode of operation.

        Parameter:
            option_string   otpion string to be evaluated

        Returns:
            True/False
        """
        if option_string.startswith('--no'):
            return False
        else:
            return True


class ExclusiveMultiswithAction(argparse.Action):  # pylint: disable=R0903
    # R0903: Too few public methods
    """
    Argparse action class. Implements a multiple state switch.
    E.g. --red --green --blue (only one possible)
         result goes to one and the same attribute
    Important: type needs to be a class that accepts the option names as value
    """

    def __init__(self, option_strings, dest,
                 default=None, required=False,
                 type=int,
                 help=None):
        """
        Initialize the object.
        """
        super(ExclusiveMultiswithAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=default,
            type=type,
            required=required,
            help=help)

    def __call__(self, parser, namespace, values,  # @UnusedVariable
                 option_string=None):
        """
        Perform the action.
        """
        setattr(namespace, self.dest, self.type(option_string.lstrip('-')))


class HelpFormatterWrapButKeepNewlines(argparse.HelpFormatter):
    """
    Customizes the default help formatters provided by argparse.

    This class respects existing newline characters in the help texts, but
    additionally wraps long lines.
    The default implementation substitutes all whitespaces (including \n)
    with a blank, which results hard to read help text for long sections.
    Implementations in RawDescriptionHelpFormatter and RawTextHelpFormatter
    go to far and do not change the format of help text at all.
    """

    def _get_help_string(self, action):
        helpstr = action.help
        defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
        # pylint: disable=W0212
        # W0212: Access to a protected member _StoreTrueAction of a client
        # class
        if '(default:' in action.help or \
           (isinstance(self, argparse._StoreTrueAction) and \
            action.default == False) or\
           action.default is argparse.SUPPRESS or \
           (not action.option_strings and action.nargs not in defaulting_nargs):
            return helpstr
        helpstr += '\n(default: %(default)s)'
        return helpstr

    def _split_lines(self, text, width):
        """
        Formats the description for one argument.
        This customized formatter respects newline characters already in the
        description, but additionally wraps long lines.
        """
        _whitespace_matcher = re.compile(r'[ \t]+')
        text = _whitespace_matcher.sub(' ', text).strip()
        ret = []
        for line in text.splitlines():
            wrapped = textwrap.wrap(line, width, replace_whitespace=False)
            ret += wrapped
            if not wrapped:
                ret.append('')
        return ret

    def _fill_text(self, text, width, indent):
        """
        Formats the description for one argument.
        The default implementation substitutes all whitespaces (including \n)
        with a blank, which results hard to read help text for long sections.
        This customized formatter respects newline characters already in the
        description.
        """
        _whitespace_matcher = re.compile(r'[ \t]+')
        text = _whitespace_matcher.sub(' ', text).strip()
        return '\n'.join(
            [textwrap.fill(line, width, initial_indent=indent,
                           subsequent_indent=indent)
             for line in text.splitlines()])

def parse_loglevel_args(string):
    """
    Parser for loglevel strings.

    The commandline argument's value is parsed, and the applicable logging
    level is returned.

    Parameters:
       string   cmd-line parameter string to be checked.
    Returns:
       logging.<level> applicable level number from class logging
       (silent=CRITICAL+1).
    """
    try:
        return LOGLEVELNAMES[string.lower()]
    except KeyError:
        raise argparse.ArgumentTypeError(\
            "loglevel must be in ({})".format(LOGLEVELSTRING))


class ParseIntegers(object):
    # pylint: disable=R0903
    # R0903: Too few public methods
    #  --> this is a function factory implememnted as a class, no need for more
    #      public methods
    # Could be alternatively implemented it as a pure function factory without
    # class overhead?
    """
    Factory for creating integer object parsers

    Instances of ParseIntegers are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - allow_scalar   plain integer is allowed
        - allow_list     list of integers is allowed (e.g. 1,2,3,4)
        - allow_range    integer range is allowed (e.g. 1-4)
    """

    def __init__(self, allow_scalar=True, allow_list=True, allow_range=True):
        self._scalar = allow_scalar
        self._list = allow_list
        self._range = allow_range
        # generate descriptive text of allowed types
        allowed = []
        if self._scalar:
            allowed.append("integer")
        if self._list:
            allowed.append("list of integers")
        if self._range:
            allowed.append("integer range")
        self.allowed_str = ', '.join(allowed[0:-1])
        if len(allowed) == 1:
            self.allowed_str += allowed[0]
        if len(allowed) > 1:
            self.allowed_str += ' or ' + allowed[-1]

    def __call__(self, string):
        return self.parse(string)

    def __repr__(self):
        args = '(scalar={0}, list{1}, range{2})'.format(\
                             self._scalar, self._list, self._range)
        return '%s (%s)' % (type(self).__name__, args)

    def parse(self, string):
        """
        Parser for integer, integer-list (comma separated) or
        integer-min-max (<min>-<max>) strings.

        The commandline argument's value is parsed, and the applicable values
        are returned.

        Parameters:
           string   cmd-line parameter string to be checked.
        Returns:
           int
                   in case of a single integer value
           [int,...]
                   in case of integer list
           {'min': <min>, 'max': <max>}
                   in case of min/max definition
        Raises:
            argparse.ArgumentTypeError
                    in case of argument errors
        """
        rex = re.search("^([0-9]*)-([0-9]*)$", string)
        if rex:
            if not self._range:
                raise argparse.ArgumentTypeError(\
                    'integer range is not allowed')
            mini = rex.group(1)
            maxi = rex.group(2)
            mini = int(mini) if mini != '' else None
            maxi = int(maxi) if maxi != '' else None
            return {'min': mini, 'max': maxi}
        if re.search(",", string):
            if not self._list:
                raise argparse.ArgumentTypeError(\
                    'integer list is not allowed')
            ret = []
            hstr = string
            rex = re.search("^([0-9]*),", hstr)
            while rex:
                ret.append(int(rex.group(1)))
                hstr = re.sub("^([0-9]*),", "", hstr)
                rex = re.search("^([0-9]*),", hstr)
            rex = re.search("^([0-9]*)$", hstr)
            if not rex:
                raise argparse.ArgumentTypeError(\
                    'malformed list of integers')
            ret.append(int(rex.group(1)))
            return ret
        rex = re.search("^([0-9]*)$", string)
        if rex:
            if not self._scalar:
                raise argparse.ArgumentTypeError(\
                    'integer value is not allowed')
            return int(string)
        else:
            raise argparse.ArgumentTypeError(\
                self.allowed_str + ' expected')


class ParseFloats(object):
    # pylint: disable=R0903
    # R0903: Too few public methods
    #  --> this is a function factory implememnted as a class, no need for more
    #      public methods
    # Could be alternatively implemented it as a pure function factory without
    # class overhead?
    """
    Factory for creating floating point object parsers

    Instances of ParseFloats are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - allow_scalar   plain float is allowed
        - allow_list     list of floats is allowed (e.g. 1.1,2.2,3,4.99)
        - allow_range    float range is allowed (e.g. 1.1-4.4)
    """

    def __init__(self, allow_scalar=True, allow_list=True, allow_range=True):
        self._scalar = allow_scalar
        self._list = allow_list
        self._range = allow_range
        # generate descriptive text of allowed types
        allowed = []
        if self._scalar:
            allowed.append("float")
        if self._list:
            allowed.append("list of floats")
        if self._range:
            allowed.append("float range")
        self.allowed_str = ', '.join(allowed[0:-1])
        if len(allowed) == 1:
            self.allowed_str += allowed[0]
        if len(allowed) > 1:
            self.allowed_str += ' or ' + allowed[-1]

    def __call__(self, string):
        return self.parse(string)

    def __repr__(self):
        args = '(scalar={0}, list{1}, range{2})'.format(\
                             self._scalar, self._list, self._range)
        return '%s (%s)' % (type(self).__name__, args)

    def parse(self, string):
        """
        Parser for float, float-list (comma separated) or
        float-min-max (<min>-<max>) strings.

        The commandline argument's value is parsed, and the applicable values
        are returned.

        Parameters:
           string   cmd-line parameter string to be checked.
        Returns:
           float
                   in case of a single floating point value
           float,...]
                   in case of float list
           {'min': <min>, 'max': <max>}
                   in case of min/max definition
        Raises:
            argparse.ArgumentTypeError
                    in case of argument errors
        """
        rex = re.search(r"^([+-]?[0-9]*(\.[0-9]*)?)-([+-]?[0-9]*(\.[0-9]*)?)$",
                        string)
        if rex:
            if not self._range:
                raise argparse.ArgumentTypeError(\
                    'float range is not allowed')
            mini = rex.group(1)
            maxi = rex.group(2)
            mini = float(mini) if mini != '' else None
            maxi = float(maxi) if maxi != '' else None
            return {'min': mini, 'max': maxi}
        if re.search(",", string):
            if not self._list:
                raise argparse.ArgumentTypeError(\
                    'float list is not allowed')
            ret = []
            hstr = string
            rex = re.search(r"^([+-]?[0-9]*(\.[0-9]*)?),", hstr)
            while rex:
                ret.append(float(rex.group(1)))
                hstr = re.sub(r"^([+-]?[0-9]*(\.[0-9]*)?),", "", hstr)
                rex = re.search(r"^([+-]?[0-9]*(\.[0-9]*)?),", hstr)
            rex = re.search(r"^([+-]?[0-9]*(\.[0-9]*)?)$", hstr)
            if not rex:
                raise argparse.ArgumentTypeError(\
                    'malformed list of floatss')
            ret.append(float(rex.group(1)))
            return ret
        rex = re.search(r"^([+-]?[0-9]*(\.[0-9]*)?)$", string)
        if rex:
            if not self._scalar:
                raise argparse.ArgumentTypeError(\
                    'floating point value is not allowed')
            return float(string)
        else:
            raise argparse.ArgumentTypeError(\
                self.allowed_str + ' expected')


class ParseStrings(object):
    # pylint: disable=R0903
    # R0903: Too few public methods
    #  --> this is a function factory implememnted as a class, no need for more
    #      public methods
    # Could be alternatively implemented it as a pure function factory without
    # class overhead?
    """Factory for creating string object parsers

    Instances of ParseStrings are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - allow_scalar   single string is allowed
        - allow_list     list of strings is allowed (e.g. 1,2,3,4)
    """

    def __init__(self, allow_scalar=True, allow_list=True, allowed_values=None):
        self._scalar = allow_scalar
        self._list = allow_list
        # generate descriptive text of allowed types
        allowed = []
        if self._scalar:
            allowed.append("string")
        if self._list:
            allowed.append("list of strings")
        self.allowed_str = ', '.join(allowed[0:-1])
        if len(allowed) == 1:
            self.allowed_str += allowed[0]
        if len(allowed) > 1:
            self.allowed_str += ' or ' + allowed[-1]
        self.allowed_values = allowed_values

    def __call__(self, string):
        return self.parse(string)

    def __repr__(self):
        args = '(scalar={}, list={}, allowed={})'.format(
            self._scalar, self._list, self.allowed_values)
        return '%s (%s)' % (type(self).__name__, args)

    def parse(self, string):
        """
        Parser for string or string-list argument.

        The commandline argument's value is parsed, and the applicable values
        are returned.

        Parameters:
           string   cmd-line parameter string to be checked.
        Returns:
           string
                   in case of a single string value
           [string,...]
                   in case of a comma separated list of strings
        Raises:
            argparse.ArgumentTypeError
                    in case of argument errors
        """
        def _check_value(string):
            """
            Check for allowed values in string.
            Parameters:
                string   string to be checked
            Returns:
                None
            Raises:
                ArgumentTypeError if not allowed
            """
            if self.allowed_values and string not in self.allowed_values:
                raise argparse.ArgumentTypeError(
                    "'{}' is not allowed (only {})"
                    .format(string, ', '.join(self.allowed_values)))
        if re.search(",", string):
            if not self._list:
                raise argparse.ArgumentTypeError(\
                    'string list is not allowed')
            ret = []
            hstr = string
            rex = re.search("^([^,]*),", hstr)
            while rex:
                _check_value(rex.group(1))
                ret.append(rex.group(1))
                hstr = re.sub("^([^,]*),", "", hstr)
                rex = re.search("^([^,]*),", hstr)
            rex = re.search("^([^,]*)$", hstr)
            if not rex:
                raise argparse.ArgumentTypeError(\
                    'malformed list of strings')
            _check_value(rex.group(1))
            ret.append(rex.group(1))
            return ret
        rex = re.search("^([^,]*)$", string)
        if rex:
            if not self._scalar:
                raise argparse.ArgumentTypeError(\
                    'string is not allowed')
            _check_value(string)
            return string
        else:
            raise argparse.ArgumentTypeError(\
                self.allowed_str + ' expected')

class ParseEmailAddr(ParseStrings):
    # pylint: disable=R0903
    # R0903: Too few public methods
    #  --> this is a function factory implememnted as a class, no need for more
    #      public methods
    # Could be alternatively implemented it as a pure function factory without
    # class overhead?
    """Factory for creating email address parsers

    Instances of ParseEmailAddr are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - allow_scalar   single string is allowed
        - allow_list     list of strings is allowed (e.g. 1,2,3,4)
    """

    def parse(self, string):
        """
        Parser for email-address or email-address-list argument.

        The commandline argument's value is parsed, and the applicable values
        are returned.

        Parameters:
           string   cmd-line parameter string to be checked.
        Returns:
           string
                   in case of a single email address
           [string,...]
                   in case of a comma separated list of email addresses
        Raises:
            argparse.ArgumentTypeError
                    in case of argument errors
        """
        def _check_value(string):
            """
            Check for allowed values in string.
            Parameters:
                string   string to be checked
            Returns:
                None
            Raises:
                ArgumentTypeError if not allowed
            """
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                            string):
                raise argparse.ArgumentTypeError(
                    "'{}' is not a valid email address")
            if self.allowed_values and string not in self.allowed_values:
                raise argparse.ArgumentTypeError(
                    "'{}' is not allowed (only {})"
                    .format(string, ', '.join(self.allowed_values)))
        if re.search(",", string):
            if not self._list:
                raise argparse.ArgumentTypeError(\
                    'email address list is not allowed')
            ret = []
            hstr = string
            rex = re.search("^([^,]*),", hstr)
            while rex:
                _check_value(rex.group(1))
                ret.append(rex.group(1))
                hstr = re.sub("^([^,]*),", "", hstr)
                rex = re.search("^([^,]*),", hstr)
            rex = re.search("^([^,]*)$", hstr)
            if not rex:
                raise argparse.ArgumentTypeError(\
                    'malformed list of email addresses')
            _check_value(rex.group(1))
            ret.append(rex.group(1))
            return ret
        rex = re.search("^([^,]*)$", string)
        if rex:
            if not self._scalar:
                raise argparse.ArgumentTypeError(\
                    'single email address is not allowed')
            _check_value(string)
            return string
        else:
            raise argparse.ArgumentTypeError(\
                self.allowed_str + ' expected')


class ParseKeywordsToNumber(object):
    # pylint: disable=R0903
    # R0903: Too few public methods
    #  --> this is a function factory implememnted as a class, no need for more
    #      public methods
    # Could be alternatively implemented it as a pure function factory without
    # class overhead?
    """Factory for creating object parsers for keywords to numbers

    Instances of ParseKeywordsToNumber are typically passed as type= arguments
    to the ArgumentParser add_argument() method.

    Keyword Arguments:
        - allow_list     list of strings is allowed (e.g. 1,2,3,4)
    """

    def __init__(self, allow_list=True, keywords=None):
        """
        Set up the parser object.
        Parameters:
            allow_list     list of keywords is allowed (e.g. 1,2,3,4)
                           in this case, the values are combined using bit-or
            keywords       dict of keywords to numbers
        Returns:
            None
        """
        self._list = allow_list
        self.allowed_str = "Keywords" + \
                           " or list of keywords" if self._list else ""
        self.keywords = keywords if keywords is not None else {}

    def __call__(self, string):
        return self.parse(string)

    def __repr__(self):
        args = '(list={})'.format(self._list)
        return '%s (%s)' % (type(self).__name__, args)

    def parse(self, string):
        """
        Parser for keyword or keyword-list argument.

        The commandline argument's value is parsed, and the applicable values
        are returned.

        Parameters:
           string   cmd-line parameter string to be checked.
        Returns:
           number   the respective number for the keyword
                    (bitwise or in case of list)
        Raises:
            argparse.ArgumentTypeError
                    in case of argument errors
        """
        if re.search(",", string):
            if not self._list:
                raise argparse.ArgumentTypeError(\
                    'keyword list is not allowed')
        ret = 0
        for key in string.split(','):
            try:
                ret |= self.keywords[key]
            except KeyError:
                raise argparse.ArgumentTypeError(
                    "'{}' is not allowed (only {})"
                    .format(string, ', '.join(list(self.keywords.keys()))))
        return ret


def parse_time(string):
    # pylint: disable=R0911
    #  R0911: Too many return statements
    #   -> many returns still better then endless elif-chains
    """
    Parses a single time string and returns start and end point of time period.

    Parameters:
        string    time string
    Returns:
        DatetimeInterval(datetimeprec, datetimeprec)
            start and end points of time interval (each with precision given
            at the commandline)
    Raises:
        argparse.ArgumentTypeError
                in case of argument errors
    """
    def gen_res(tim1, tim2, prec):
        """
        Result generator helper.
        """
        return DatetimeInterval(datetimeprec.fromdatetime(tim1, prec),
                                datetimeprec.fromdatetime(tim2, prec))
    try:
        tim = datetime_parse_iso8601(string)
    except ValueError:
        raise argparse.ArgumentTypeError('illegal time: ' + string)

    if len(string) > 20:
        # special case: delta depends on precision given in fractions of seconds
        n_digi = len(string)-20
        delta_s = 10**-n_digi
        return gen_res(tim, tim + datetime.timedelta(seconds=delta_s), "f")
    if len(string) > 17:
        return gen_res(tim, tim + datetime.timedelta(seconds=1), "S")
    if len(string) > 14:
        return gen_res(tim, tim + datetime.timedelta(minutes=1), "M")
    if len(string) > 11:
        return gen_res(tim, tim + datetime.timedelta(hours=1), "H")
    if len(string) > 8:
        return gen_res(tim, tim + datetime.timedelta(days=1), "d")
    if len(string) > 5:
        # special cases for month: use relativedelta
        return gen_res(tim, tim + relativedelta(months=1), "m")
    # special cases for year: use relativedelta
    return gen_res(tim, tim + relativedelta(months=12), "Y")

def parse_time_interval(string):
    """
    Parser for time intervals. Allowed are ISO dates (YYYY-MO-DDTHH:MI:SS

    The commandline argument's value is parsed, and the applicable values.

    Parameters:
       string   cmd-line parameter string to be parsed.
    Returns:
       [dattimeprec, dattimeprec]
               start, endtime   datetime objects with precision
    Raises:
        argparse.ArgumentTypeError
                through parse_time()
    """
    if not string:
        return DatetimeInterval.empty()
    reg = re.match('([0-9][0-9][0-9][0-9].*)[-,]([0-9][0-9][0-9][0-9].*$)',
                   string)
    if reg:
        # FROM and TO defined
        from_time = parse_time(reg.group(1))
        to_time = parse_time(reg.group(2))
        if from_time >= to_time:
            raise argparse.ArgumentTypeError('illegal time interval: ' +\
                string + ': FROM time must be earlier than TO time')
        return DatetimeInterval(from_time[0], to_time[1])
    return parse_time(string)

def parse_time_instant(string):
    """
    Parses a time string and returns a datetime object with precision.

    Parameters:
        string    time string
    Returns:
        datetimeprec
                  timestamp with precision
    Raises:
        argparse.ArgumentTypeError
                in case of argument errors
    """
    return parse_time(string)[0]

def parse_date(string):
    """
    Parses a date string (YYYY-MO-DD) and returns a datetime.date object.

    Parameters:
        string    time string
    Returns:
        datetime.date
                  date
    Raises:
        argparse.ArgumentTypeError
                in case of argument errors
    """
    try:
        return datetime.datetime.strptime(string, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError('illegal date: ' + string)

