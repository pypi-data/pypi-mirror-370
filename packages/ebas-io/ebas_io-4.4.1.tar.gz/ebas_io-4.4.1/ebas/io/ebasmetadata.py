"""
ebas/nasa_ames/ebasmetadata.py
$Id: ebasmetadata.py 2713 2021-09-28 14:07:57Z pe $

Defines all legal metadata tags in ebas Nasa Ames files.
Used both, for writing Nasa Ames files, and for parsing input files.

"Print" means converting internal (NasaAmes object's) representation to string
for output. Those functions always return one str or a generator of str.
(No real "print" is done)

"Parsing" is the conversion from string representation to internal (NasaAmes
objects's) representation. Checks are restricted to syntax check and very
fundamental value checks.
Advanced value checks that need validation data from the DB or value checks that
depend on other metadata __must__  be done by the caller (NasaAmes Object).

History:
V.1.0.0  2013-03-11  pe  initial version

"""

import datetime
import re
from six import string_types
from numbers import Number
from collections import defaultdict
from .file import EBAS_IOMETADATA_OPTION_SETKEY
from nilutility.datatypes import DataObject
from nilutility.string_helper import list_joiner, list_splitter
from nilutility.struct_builder import StructureBuilder, Condition, Merge, \
    Substitute, Default, IsIn, NotIn, BitAnd
from ebas.domain import EbasDomainError
from ebas.domain.basic_domain_logic.time_period import normalize_period_code
from ebas.domain.basic_domain_logic.export_filter import ParseExportFilter
from ebas.domain.basic_domain_logic.unit_convert import UnitConvert
from argparse import ArgumentTypeError
from ebas.domain.masterdata.dc import DCBase, DCListBase, DCError, DCWarning
from ebas.domain.masterdata.ac import EbasMasterAC
from ebas.domain.masterdata.ax import EbasMasterAX
from ebas.domain.masterdata.ay import EbasMasterAY
from ebas.domain.masterdata.ca import EbasMasterCA
from ebas.domain.masterdata.cc import EbasMasterCC
from ebas.domain.masterdata.ft import EbasMasterFT
from ebas.domain.masterdata.ht import EbasMasterHT
from ebas.domain.masterdata.im import EbasMasterIM
from ebas.domain.masterdata.it import EbasMasterIT
from ebas.domain.masterdata.org import EbasMasterOR
from ebas.domain.masterdata.ma import EbasMasterMA
from ebas.domain.masterdata.sc import EbasMasterSC
from ebas.domain.masterdata.re import EbasMasterRE
from ebas.domain.masterdata.sp import EbasMasterSP
from ebas.domain.masterdata.se import EbasMasterSE
from ebas.domain.masterdata.sw import EbasMasterSW
from ebas.domain.masterdata.zn import EbasMasterZN
from ebas.domain.masterdata.fp import EbasMasterFP
from ebas.domain.masterdata.oc import EbasMasterOC
from ebas.domain.masterdata.wc import EbasMasterWC
from ebas.domain.masterdata.zt import EbasMasterZT
from ebas.domain.masterdata.md import EbasMasterMD
from ebas.domain.masterdata.qm_qv import EbasMasterQM
from ebas.domain.masterdata.qm_qv import EbasMasterQO
from ebas.domain.masterdata.pm import EbasMasterPM
from ebas.domain.masterdata.co import EbasMasterCO
from ebas.domain.masterdata.cy import EbasMasterCY
from ebas.domain.masterdata.sm import EbasMasterSM
from ebas.domain.masterdata.vp import EbasMasterVP
from ebas.domain.masterdata.vt import EbasMasterVT

# DCError, DCWarning are needed for export
NOWARNINGS_ = DCError, DCWarning
from .file import EBAS_IOFORMAT_NASA_AMES, EBAS_IOFORMAT_CSV

class EbasMetadataError(Exception):
    """
    Exception used in parser functions.
    """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg
    def __str__(self):
        return self.msg

class EbasMetadataWarning(Exception):
    """
    Exception used in parser functions.
    """
    def __init__(self, retval, msg):
        Exception.__init__(self, msg)
        self.retval = retval
        self.msg = msg
    def __str__(self):
        return self.msg

class EbasMetadataNone(Exception):
    """
    Exception raised by metadata_value if a metadata element should not be
    shown.
    """
    pass

class EbasMetadataEmpty(Exception):
    """
    Exception raised by metadata_value if a metadata element is empty.
    """
    pass


def check_orcid(orcid):
    """
    Check the ORCID.
    Parameters:
        orcid    a 16 digit orcid
    Returns:
        True if OK, error text if not OK
    """
    reg = re.match(r'^(\d\d\d\d)-(\d\d\d\d)-(\d\d\d\d)-(\d\d\d[\dX])$', orcid)
    if not reg:
        return "ORCID syntax error (must be format 9999-9999-9999-999?)"
    digits = reg.group(1) + reg.group(2) + reg.group(3) + reg.group(4)
    # sum the the first 15 digits:
    total = 0
    for i in range(len(digits)-1):
        total = (total + int(digits[i])) * 2
    result = (12 - total % 11) % 11
    check = "X" if result == 10 else str(result)
    if digits[15] != check:
        return "ORCID is not valid (checksum mismatch)"
    return True


class EbasMetadata(object):
    """
    Metadata I/O for ebas specific metadata (Tag=Value)
    Conversion functions are called parsers and printers and are referenced
    by the corresponding elements in the conversion dictionaries (for each data
    version) below.
    """

    # generic parsers/printers:

    @staticmethod
    def parse_generic_factory(unit_=None, type_=None, range_=None, allowed=None,
                              len_=None):
        # type range and len are keywords, append _ to all keyword arguments
        # in order to allow for generic calling form file parser.
        """
        Factory for a generic parser function. Some generic checks can be set
        in the factory.
        Parameters:
            unit_   the value must be a number and a unit string
            type_   the type the value should be converted in
            range_  the legal value range [min, max]
            len_    the legal range for the len() of the value (must be a
                    (type that supports len, most likely string)
            allowed list with allowed values
        Returns:
            (number, unit)
        Raises:
            EbasMetadataError if not legal
        """

        def _parse(value):
            """
            Generic parser.
            Parameters:
                value   value from a tag/value pair (string)
            Returns:
                value if legal
            Raises:
                EbasMetadataError if not legal
            """
            if unit_:
                # metadata elements with static unit (e.g. Altitude (m))
                try:
                    reg = re.match(r'^([0-9+\-\.Ee]+) *'+unit_+'$', value)
                    if not reg:
                        raise ValueError()
                    value = float(reg.group(1))  # raises also ValueError
                except ValueError:
                    raise EbasMetadataError(
                        "syntax error (expected '<{}> {}')"
                        .format(type_.__name__ if type_ else 'float', unit_))
            if type_:
                try:
                    value = type_(value)
                except (TypeError, ValueError):
                    raise EbasMetadataError(
                        "data type error (expected type {})"
                        .format(type_.__name__))
            if range_:
                # split into 3 cases, in order to produce a "nice" error message
                if range_[1] is None and range_[0] is not None and \
                   value < range_[0]:
                    raise EbasMetadataError('value must be grater then {}'
                                            .format(range_[0]))
                if range_[0] is None and range_[1] is not None and \
                   value > range_[1]:
                    raise EbasMetadataError('value must be less then {}'
                                            .format(range_[1]))
                if range_[0] is not None and range_[1] is not None and \
                   (value < range_[0] or value > range_[1]):
                    raise EbasMetadataError('value must be between {} and {}'
                                            .format(range_[0], range_[1]))
                # there is no possibiolity for TypeError when comparing:
                # every comparison is legal in python
            if allowed:
                if value not in allowed:
                    raise EbasMetadataError('value must be in [{}]'.format(
                        ', '.join(allowed)))
            if len_:
                try:
                    len_val = len(value)
                except TypeError:
                    raise EbasMetadataError('type {} has no length'
                                            .format(type(value).__name__))
                # split into 3 cases, in order to produce a "nice" error message
                if len_[1] is None and len_[0] is not None and \
                   len_val < len_[0]:
                    raise EbasMetadataError('value must be longer then {}'
                                            .format(len_[0]))
                if len_[0] is None and len_[1] is not None and \
                   len_val > len_[1]:
                    raise EbasMetadataError('value must be shorter then {}'
                                            .format(len_[1]))
                if len_[0] is not None and len_[1] is not None and \
                   (len_val < len_[0] or len_val > len_[1]):
                    raise EbasMetadataError('length must be between {} and {}'
                                            .format(len_[0], len_[1]))
            return value

        if unit_:
            if type_:
                RuntimeError('parse_generic: unit and type not compatible')
        return _parse

    @staticmethod
    def print_generic_factory(unit_=None):
        """
        Factory for a generic printer function (including unit
        if necessary).
        Parameters:
            unit     optional unit that should be added
        Returns:
            printer function
        Parameters:
            unit_    unit string to be appended to the value
        """

        def _print(value):
            """
            Generic printer function (including unit
            if necessary).
            Parameters:
                value   value to be printed
            Returns:
                string representation of the metadata value
            """
            if unit_:
                return u"{} {}".format(value, unit_)
            return u"{}".format(value)

        return _print

    @staticmethod
    def parse_datetime_arbitrary(value):
        """
        Parse date/time in long or short format.
        Syntax:
            YYYYMODDHHMISS or YYYYMODD
        Parameters:
            value     value part from the tag/value pair (str)
        Returns:
            value as datetime object if legal
        Raises:
            EbasMetadataError if not legal
        """
        # for now, we only read Nasa Ames, so the parser needs only this format
        allowed_fmt = [r"^(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$",
                       r"^(\d\d\d\d)(\d\d)(\d\d)$"]
        for fmt in allowed_fmt:
            reg = re.match(fmt, value)
            if reg:
                try:
                    return datetime.datetime(*[int(k) for k in reg.groups()])
                except ValueError as excpt:
                    raise EbasMetadataError(str(excpt))
        # generate exception
        raise EbasMetadataError(
            "illegal date/time format {}, must be 'YYYYMODDHHMISS' or "
            "'YYYYMODD'".format(value))

    def print_datetime_arbitrary(self, value):
        """
        Creates the output string for date/time values in long or short format
        (if elements from hour and below are 0, use short format, else long).
        Parameters:
            value      date/time value to be prited
        Returns:
            str
        """
        if value.microsecond != 0:
            # something wrong here, arbitrary is only to be used for
            # non-microsecond precision times!
            raise RuntimeError("git microsecond precision time")
        if value.time() == datetime.time(0, 0, 0):
            if self.data_format == EBAS_IOFORMAT_NASA_AMES:
                return value.strftime("%Y%m%d")
            elif self.data_format == EBAS_IOFORMAT_CSV:
                return value.strftime("%Y-%m-%d")
            else:
                # EBAS_IOFORMAT_NETCDF1, EBAS_IOFORMAT_NETCDF, EBAS_IOFORMAT_XML
                return value.strftime('%Y-%m-%d UTC')
        if self.data_format == EBAS_IOFORMAT_NASA_AMES:
            return value.strftime("%Y%m%d%H%M%S")
        elif self.data_format == EBAS_IOFORMAT_CSV:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # EBAS_IOFORMAT_NETCDF1, EBAS_IOFORMAT_NETCDF, EBAS_IOFORMAT_XML
            return value.strftime('%Y-%m-%dT%H:%M:%S UTC')

    @staticmethod
    def parse_datetime_creation(value):
        """
        Parse date/time creation: arbitrary format second or microsecond
        resolution. This is for backwards compatibility with old files. Creation
        date used to be second resolution, later it was changed microsecond.
        So we accept both on read...
        Syntax:
            YYYYMODDHHMISS[tttttt]
        Parameters:
            value     value part from the tag/value pair (str)
        Returns:
            value as datetime object if legal
        Raises:
            EbasMetadataError if not legal
        """
        # for now, we only read Nasa Ames, so the parser needs only this format
        reg = re.match(
            r"^(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d\d\d\d\d)$",
            value)
        if not reg:
            reg = re.match(r"^(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$",
                           value)
            if not reg:
                raise EbasMetadataError(
                    "illegal date/time format {}, must be YYYYMODDHHMISS or"
                    "YYYYMODDHHMISStttttt".format(value))
        try:
            date = datetime.datetime(*[int(k) for k in reg.groups()])
        except ValueError as excpt:
            raise EbasMetadataError(str(excpt))
        return date

    @staticmethod
    def parse_datetime_state(value):
        """
        Parse date/time down to microseconds.
        Syntax:
            YYYYMODDHHMISS.tttttt
        Parameters:
            value     value part from the tag/value pair (str)
        Returns:
            value as datetime object if legal
        Raises:
            EbasMetadataError if not legal
        """
        # for now, we only read Nasa Ames, so the parser needs only this format
        reg = re.match(
            r"^(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d\d\d\d\d)$",
            value)
        if not reg:
            raise EbasMetadataError(
                "illegal date/time format {}, must be YYYYMODDHHMISStttttt"\
                    .format(value))
        try:
            date = datetime.datetime(*[int(k) for k in reg.groups()])
        except ValueError as excpt:
            raise EbasMetadataError(str(excpt))
        return date

    def print_datetime_state(self, value):
        """
        Creates the output string for date/time values in long or short format
        (if elements from hour and below are 0, use short format, else long).
        Parameters:
            value      date/time value to be prited
        Returns:
            str
        """
        if self.data_format == EBAS_IOFORMAT_NASA_AMES:
            return value.strftime("%Y%m%d%H%M%S%f")
        elif self.data_format == EBAS_IOFORMAT_CSV:
            return value.strftime("%Y-%m-%d %H:%M:%S.%f")
        else:
            # EBAS_IOFORMAT_NETCDF1, EBAS_IOFORMAT_NETCDF, EBAS_IOFORMAT_XML
            return value.strftime('%Y-%m-%dT%H:%M:%S.%f UTC')
        
    def parse_datetime_dataversion(self, value):
        """
        Parser for date/time metadata according to EBAS data version.
        Used for Revision date, Startdate, File creation, Extract state.
        default syntax:
            EBAS_1: YYYYMODD
            EBAS_1.1: YYYYMODDHHMISS
        The different syntax between EBAS_1 and EBAS_1.1 is accepted with
        warning in both formats.
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        # for now, we only read Nasa Ames, so the parser needs only this format
        warning = False
        if self.data_version == 'EBAS_1':
            dateformat = r"^(\d\d\d\d)(\d\d)(\d\d)$"
        else:
            dateformat = r"^(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$"
        reg = re.match(dateformat, value)
        if not reg:
            if self.data_version == 'EBAS_1':
                dateformat = r"^(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)$"
                warning = "use of EBAS_1.1 time format (YYYYMODDHHMISS) in " +\
                          "EBAS_1"
            else:
                dateformat = r"^(\d\d\d\d)(\d\d)(\d\d)$"
                warning = "deprecated time format YYYYMODD"
            reg = re.match(dateformat, value)
            if not reg:
                raise EbasMetadataError(
                    "illegal date/time format {}".format(value))
        try:
            date = datetime.datetime(*[int(k) for k in reg.groups()])
        except ValueError as excpt:
            raise EbasMetadataError(str(excpt))
        if warning:
            raise EbasMetadataWarning(date, warning)
        return date

    def print_datetime(self, value):
        """
        Creates the output string for date/time values (File creation,
        Startdate, Revision date).
        Parameters:
            value      date/time value to be prited
        Returns:
            str
        """
        if self.data_version == 'EBAS_1':
            if self.data_format == EBAS_IOFORMAT_CSV:
                return value.strftime("%Y-%m-%d")
            return value.strftime("%Y%m%d")
        else:
            if self.data_format == EBAS_IOFORMAT_CSV:
                return value.strftime("%Y-%m-%d %H:%M:%S")
            return value.strftime("%Y%m%d%H%M%S")

    @staticmethod
    def parse_license(value):
        """
        Parses license metadata
        """
        # Allowed values only empty or CCBY 4.0, list of allowed values
        # hardcoded as there will be only 2.
        if not value:
            return None
        if value == 'https://creativecommons.org/licenses/by/4.0/':
            return value
        raise EbasMetadataError("illegal license: '{}'".format(value))

    @staticmethod
    def parse_doi(value):
        r"""
        Parse doi metadata
        Syntax:
            ....-....[part\d\d]
        Parameters:
            value     value part from the tag/value pair (str)
        Returns:
            value as [doi, part#]
        Raises:
            EbasMetadataError if not legal
        """
        if not value:
            return None
        reg = re.match(r"^(https://doi.org.*[0-9A-Z]{4}-[0-9A-Z]{4})( \(part (\d*)\))?$", value)
        if not reg:
            raise EbasMetadataError(
                "illegal DOI format {}".format(value))
        return [reg.group(1), int(reg.group(3))]

    @staticmethod
    def print_doi(value):
        """
        Prints doi
        """
        return "{}{}".format(
            value[0] if value[0] else '',
            ' (part {})'.format(value[1]) if value[1] else '')

    @staticmethod
    def parse_doi_list(value):
        """
        Parses doi_list
        """
        return [doi for doi in list_splitter(value, ",")] if value else None

    @staticmethod
    def print_doi_list(value):
        """
        Prints doi_list
        """
        return ', '.join(value)

    @staticmethod
    def parse_export_filter(value):
        """
        Parses Export filter metadata
        """
        pex = ParseExportFilter(default=0)
        try:
            return pex.parse(value)
        except ArgumentTypeError as excpt:
            raise EbasMetadataError(str(excpt))

    @staticmethod
    def print_export_filter(value):
        """
        Parses Export filter metadata
        """
        pex = ParseExportFilter(default=value)
        return str(pex)

    @staticmethod
    def parse_regime(value):
        """
        Parser for Regime code metadata.
        Must be 'IMG'
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        master = EbasMasterRE()
        try:
            _ = master[value]
        except KeyError:
            raise EbasMetadataError(
                "illegal Regime (only {} allowed)".format(
                    ', '.join([elem.RE_REGIME_CODE for elem in master])))
        return value

    @staticmethod
    def parse_timezone(value):
        """
        Parser for Timezone metadata.
        Must be 'UTC'
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        if value != 'UTC':
            raise EbasMetadataError(
                "illegal time zone. All data in EBAS must be 'UTC'.")
        return value

    @staticmethod
    def print_org(value):
        """
        Creates the output string for organization.
        Parameters:
            value      org dict to be printed
        Returns:
            str
        """
        def _comma_escape(elem):
            """
            Helper: escape comma in strings of a list (wrap in double quotes)
            Parameters:
                elem    list of strings
            Returns:
                None
            """
            for i in range(len(elem)):
                if elem[i] and re.search(",", elem[i]):
                    elem[i] = '"' + re.sub('"', '""', elem[i]) +'"'

        def _none_to_empty(elem):
            """
            Helper: substitute None by empty string in a list.
            Parameters:
                elem    list of strings (or None)
            Returns:
                None
            """
            for i in range(len(elem)):
                if elem[i] is None:
                    elem[i] = ''

        elem = [value['OR_CODE'],
                value['OR_NAME'],
                value['OR_ACRONYM'],
                value['OR_UNIT'],
                value['OR_ADDR_LINE1'],
                value['OR_ADDR_LINE2'],
                value['OR_ADDR_ZIP'],
                value['OR_ADDR_CITY'],
                value['OR_ADDR_COUNTRY']]
        _none_to_empty(elem)
        _comma_escape(elem)
        return u"{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}".format(*elem)

    @staticmethod
    def parse_setkey(value):
        """
        Parser for Dataset key.
        Syntax: int
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value (int) if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            setkey = int(value)
        except (ValueError, TypeError):
            raise EbasMetadataError('syntax error. Should be an integer number')
        if setkey < 1:
            raise EbasMetadataError('must be greater then 0')
        return setkey

    @staticmethod
    def parse_ds_type(value):
        """
        Parser for Set type code metadata.
        Syntax: TI or TU
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        if value not in ('TI', 'TU'):
            raise EbasMetadataError('only TI and TU is valid')
        return value

    @staticmethod
    def parse_timeref(value):
        """
        Parser for Timeref metadata.
        Syntax: HH_MI (hour, minute)
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        reg = re.match(r'^(-?)(\d\d)_(\d\d)$', value)
        if not reg:
            raise EbasMetadataError('syntax error. Should be HH:MI (HH hour '
                                    '(00-23), MI minute (00-59))')
        neg = -1 if reg.group(1) == '-' else 1
        hour = int(reg.group(2))
        minute = int(reg.group(3))
        if hour < 0 or hour > 23:
            raise EbasMetadataError('hour must be between 1 and 23')
        if minute < 0 or minute > 59:
            raise EbasMetadataError('minute must be between 1 and 59')
        return (value, datetime.timedelta(hours=hour*neg, minutes=minute*neg))

    @staticmethod
    def parse_input_dataset(value):
        """
        Parser for Input dataset metadata.
        Syntax:
            PID or
            "Instrument type: <instrument type>, Instrument ref: <instrument reference>, Method ref: <method reference>, Data level: <data level>, Version: <version>
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value (str) if legal
        Raises:
            EbasMetadataError if not legal
        """
        if re.match(r'^https://', value):
            return value
        if re.match(
            r'^Instrument type: .*, Instrument ref: .*, Method ref: .*, '
            r'Data level: .*, Version: .*', value):
            return value
        raise EbasMetadataError(
            'syntax error. Should be either a PID or Syntax: "Instrument type: '
            '<instrument type>, Instrument ref: <instrument reference>, '
            'Method ref: <method reference>, Data level: <data level>, '
            'Version: <version>"')

    @staticmethod
    def parse_statistics(value):
        """
        Parser for Statistics metadata.
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterSC()[value]
        except KeyError:
            raise EbasMetadataError(
                "Unknown statistics code '{}'".format(value))
        return value

    @staticmethod
    def parse_period_rescode(value):
        """
        Parser for periods and resolutions (Period code, Resolution code,
        Sample duration, Orig. time res.).
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            new = normalize_period_code(value)
        except ValueError:
            raise EbasMetadataError("syntax error, no valid time interval")
        if new != value:
            raise EbasMetadataWarning(
                new, "period code {} changed to {}".format(value, new))
        if len(value) > 15:
            raise EbasMetadataWarning(
                value, "period code {} too long. Maximum 15 characters")
        return value

    @staticmethod
    def parse_station_platform_code(value):
        """
        Parser for Station code and Platform code.
        Syntax:
            XX9999Y
                XX: Country, 9999: number,
                Y:  Station type for station codes, platform type for platform
                    codes
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        if not re.match(r'^[A-Z][A-Z]\d\d\d\d[A-Z]$', value):
            raise EbasMetadataError(
                "syntax error. Should be like 'NN1234T' "
                "(NN: nation code, 1234: 4 digit station number within nation, "
                "T: Station type character or platform code)")
        return value

    @staticmethod
    def parse_station_other_ids(value):
        """
        Parser for Station other IDs.
        Syntax: anytext(context), ...
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        for part in list_splitter(value, ","):
            if not re.match(r'^[0-9a-zA-Z_\-\/]* *\([^()]*\)$', part):
                raise EbasMetadataError(
                    "syntax error. Should be like 'Station-ID (Framework or "
                    "project)[, ...]'")
        if len(value) > 255:
            raise EbasMetadataError("maximum: 255 characters")
        return value

    @staticmethod
    def parse_station_wmo_region(value):
        """
        Parser for Station WMO region.
        Syntax: int
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal (int)
        Raises:
            EbasMetadataError if not legal
        """
        try:
            ret = int(value)
        except ValueError:
            raise EbasMetadataError("Station WMO region must be integer")
        try:
            _ = EbasMasterSW()[ret]
        except KeyError:
            raise EbasMetadataError(
                "Unknown WMO region '{}'".format(value))
        return ret

    @staticmethod
    def parse_latitude(value):
        """
        Parser for latitude (station and measurement)
        Syntax: float between -90 and 90
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal (float)
        Raises:
            EbasMetadataError if not legal
        """
        try:
            ret = float(value)
        except ValueError:
            raise EbasMetadataError("Latitude must be float")
        if ret < -90.0 or ret > 90.0:
            raise EbasMetadataError("Latitude must be between -90.0 and 90.0")
        return ret

    @staticmethod
    def parse_longitude(value):
        """
        Parser for longitude (station and measurement)
        Syntax: float between -180 and 180
        Parameter:
            value   value part from the tag/value pair (str)
        Returns:
            value if legal (float)
        Raises:
            EbasMetadataError if not legal
        """
        try:
            ret = float(value)
        except ValueError:
            raise EbasMetadataError("Longitude must be float")
        if ret < -180.0 or ret > 180.0:
            raise EbasMetadataError("Longitude must be between -180.0 and "
                                    "180.0")
        return ret


    # Parsers and printers with non-standard interface.
    # (those are special cases in nasa_ames.read and nasa_ames.write)

    PERSON_SYNTAX = {
        'mandatory': (
            {
                'key': 'PS_LAST_NAME',
                'tag': 'Last name',
                'minlen': None,
                'maxlen': 70,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_FIRST_NAME',
                'tag': 'First name',
                'minlen': None,
                'maxlen': 70,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_EMAIL',
                'tag': 'Email',
                'minlen': None,
                'maxlen': 255,
                'regexp': r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                'syntax': "illegal email address syntax",
            },
            {
                'key': 'PS_ORG_NAME',
                'tag': 'Organization name',
                'minlen': None,
                'maxlen': 255,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_ORG_ACR',
                'tag': 'Organization acronym',
                'minlen': None,
                'maxlen': 16,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_ORG_UNIT',
                'tag': 'Organization unit',
                'minlen': None,
                'maxlen': 255,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_ADDR_LINE1',
                'tag': 'Address line 1',
                'minlen': None,
                'maxlen': 255,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_ADDR_LINE2',
                'tag': 'Address line 2',
                'minlen': None,
                'maxlen': 255,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_ADDR_ZIP',
                'tag': 'ZIP code',
                'minlen': None,
                'maxlen': 10,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_ADDR_CITY',
                'tag': 'City',
                'minlen': None,
                'maxlen': 60,
                'regexp': None,
                'syntax': None,
            },
            {
                'key': 'PS_ADDR_COUNTRY',
                'tag': 'Country',
                'minlen': None,
                'maxlen': 70,
                'regexp': None,
                'syntax': None,
            },
            ),
        'optional': (
            {
                'tag': 'ORCID',
                'key': 'PS_ORCID',
                'minlen': None,  # is implicitly checked with regexp
                'maxlen': None,  # is implicitly checked with regexp
                'regexp': None,
                'syntax': None,
                'check': check_orcid,
            },
            )
    }

    @classmethod
    def parse_person(cls, value):
        """
        Parser for person metadata (Originator, Submuitter).
        Parameter:
            value      value part from the tag/value pair (str)
        Returns:
            person dictionary
        Raises:
            EbasMetadataError if not legal
        """
        mandatory = cls.PERSON_SYNTAX['mandatory']
        optional = cls.PERSON_SYNTAX['optional']

        psa = list_splitter(value, ",")
        if len(psa) < len(mandatory):
            raise EbasMetadataError(
                "syntax error: '{}'; {} elements needed, should be '{}[, {}]'."
                .format(
                    value, len(mandatory),
                    ', '.join([x['tag'] for x in mandatory]),
                    ', '.join(['{}=...'.format(x['tag']) for x in optional])))

        psa = [elem.strip() if elem.strip() != u'' else None for elem in psa]
        errors = []
        ret = {}
        # set mandatory elements
        for i in range(len(mandatory)):
            ret[mandatory[i]['key']] = None
            if psa[i] is None:
                continue
            if '=' in psa[i]:
                errors.append(
                    "mandatory element '{}' ('{}') may not contain '='"
                    .format(mandatory[i]['tag'], psa[i]))
                continue
            if mandatory[i]['minlen'] is not None and \
               len(psa[i]) < mandatory[i]['minlen']:
                errors.append(
                    "element '{}' ('{}') must have minimum length {}"
                    .format(mandatory[i]['tag'], psa[i],
                            mandatory[i]['minlen']))
            if mandatory[i]['maxlen'] is not None and \
               len(psa[i]) > mandatory[i]['maxlen']:
                errors.append(
                    "element '{}' ('{}') must have maximum length {}"
                    .format(mandatory[i]['tag'], psa[i],
                            mandatory[i]['maxlen']))
            if mandatory[i]['regexp'] is not None and \
               not re.match(mandatory[i]['regexp'], psa[i]):
                errors.append(mandatory[i]['syntax'])
            ret[mandatory[i]['key']] = psa[i]

        # initialize optional elements
        for elem in optional:
            ret[elem['key']] = None

        # set optional elemets
        for i in range(len(mandatory), len(psa)):
            if psa[i] is None:
                errors.append(
                    "optional element {} is empty (probably one comma too much)"
                    .format(i+1))
                continue
            if not '=' in psa[i]:
                errors.append("optional element {} ({}) is not format key=value"
                              .format(i+1, psa[i]))
                continue

            try:
                (tag, val) = list_splitter(psa[i], "=")
            except ValueError:
                errors.append("optional element {} ({}) is not format key=value"
                              .format(i+1, psa[i]))
                continue
            tag = tag.strip()
            val = val.strip()
            if val == u'':
                # val = None
                continue

            # find the right element in optional
            elem = [x for x in optional if x['tag'] == tag]
            if len(elem) < 1:
                errors.append("unknown optional element '{}'".format(tag))
                continue
            if len(elem) > 1:
                raise RuntimeError("{} multiply defined".format(tag))
            elem = elem[0]

            if elem['minlen'] is not None and \
               len(val) < elem['minlen']:
                errors.append(
                    "element '{}' ('{}') must have minimum length {}"
                    .format(tag, val, elem['minlen']))
            if elem['maxlen'] is not None and \
               len(val) > elem['maxlen']:
                errors.append(
                    "element '{}' ('{}') must have maximum length {}"
                    .format(tag, val, elem['maxlen']))
            if elem['regexp'] is not None and \
               not re.match(elem['regexp'], val):
                errors.append(elem['syntax'])
            if elem['check'] is not None:
                res = elem['check'](val)
                if res is not True:
                    errors.append(res)
            ret[elem['key']] = val

        if len(errors) > 0:
            raise EbasMetadataError("; ".join(errors))

        return ret

    @classmethod
    def print_person(cls, ps_list):
        """
        Creates an output string for a person list (may be submitters or
        originators).
        Originators and submitters may not occur in vname by definition.
        Parameters:
            ps_list     list of person metadata
        Returns:
            generator of str
        """
        for pers in ps_list:
            outputlist = [pers[x['key']]
                          for x in cls.PERSON_SYNTAX['mandatory']]
            outputlist += ['{}={}'.format(x['tag'], pers[x['key']])
                           for x in cls.PERSON_SYNTAX['optional']
                           if pers[x['key']] is not None]
            yield list_joiner(outputlist, ',', insert_space=True)

    @classmethod
    def print_generic_list(cls, list_):
        """
        Creates an output string for a generic list (e.g. input_dataset and
        software). The elements in those generic lists are already strings, so
        no further processing.
        Those metadata may not occur in vname by definition.
        Parameters:
            list_     list of metadata
        Returns:
            generator of str
        """
        for elem in list_:
            yield elem

    @staticmethod
    def parse_instr_type(value):
        """
        Parse instrument type.
        Syntax: Check with EbasMasterFT
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        if not re.match(r'^[\-_A-Za-z0-9\+]+$', value):
            raise EbasMetadataError(
                "syntax error: '{}' (legal characters are A-Z, a-z, 0-9, "
                "-, _, +)"
                .format(value))
        # check maximum length:
        if len(value) > 40:
            raise EbasMetadataError("too long: '{}'. Maximum length 40 "
                                    "characters".format(value))
        # Legacy types:
        if value == 'chemiluminesc':
            value = 'chemiluminescence_photometer'
            raise EbasMetadataWarning(value, \
                "Legacy instrument type 'chemiluminesc' changed to "
                "'chemiluminescence_photometer'.")
        try:
            _ = EbasMasterFT()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown instrument type '{}'".format(value))
        return value

    @staticmethod
    def parse_ana_technique(value):
        """
        Parse analytical measurement technique .
        Syntax: Check with EbasMasterAT
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterAY()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown analytical measurement technique '{}'".format(value))
        return value

    @staticmethod
    def parse_instr_name(value):
        """
        Parse instrument name.
        Parse analytical instrument name.
        Syntax: max 40 char, characters: -_A-Za-z0-9.+
                not like <OR_CODE>_name
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        if not re.match(r'^[\-_A-Za-z0-9.+]+$', value):
            raise EbasMetadataError(
                "syntax error: '{}' (legal characters are A-Z, a-z, 0-9, -, _, "
                "+, .)".format(value))
        # check maximum length:
        if len(value) > 39:
            raise EbasMetadataError("too long: '{}'. Maximum length 39 "
                                    "characters".format(value))
        if re.match('^([A-Z][A-Z][0-9][0-9][LO])_', value):
            raise EbasMetadataWarning(
                value,
                "suspicious: '{}' looks like ORG code ('{}') at the beginning. "
                "Instrument name should not include ORG code."
                .format(value, value[0:5]))
        return value

    @staticmethod
    def parse_sensor_type(value):
        """
        Parse sensor type.
        Valid values defined in materdata (SE_SENSORTYPE)
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        # For now, only the sensortype can be checked
        # Validity of triple FT/CO/SE is checked in
        # check_interdependent_metadata
        if EbasMasterSE().exist_sensortype(value):
            return value
        raise EbasMetadataError(
            "Unknown sensor type '{}'".format(value))

    @staticmethod
    def parse_absorption_crossection(value):
        """
        Parse sensor type.
        Valid values defined in materdata (AX_ABSORPTION_CROSSSECTION)
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        # For now, only the sensortype can be checked
        # Validity of triple FT/CO/SE is checked in
        # check_interdependent_metadata
        if EbasMasterAX().exist_absorption_crosssection(value):
            return value
        raise EbasMetadataError(
            "Unknown absorption cross section '{}'".format(value))

    @staticmethod
    def parse_matrix(value):
        """
        Parse matrix.
        Syntax: valid matrix from masterdata.
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterMA()[value]
        except KeyError:
            raise EbasMetadataError(
                "Unknown matrix '{}'".format(value))
        return value

    def parse_component(self, value):
        """
        Parse component.
        SPECIAL CASE: used only from _parse_ebasmetadata_vname_positional in
        NasaAmes input.
        This because component name is positional in VNAME, and in NCOM any
        component name is free text, as component in mandatory in VNAME.
        Syntax: valid component name from masterdata.
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        # check if component exists
        try:
            # CO masterdata lookup with additional data level:
            # if CO is not defined in DB masterdata, lookup in exceptional
            # masterdata (data level dependent, not meant to be imported)
            EbasMasterCO()[(value, self.data_level)]
        except KeyError:
            # check if if a historic componentt name exists:
            try:
                comp = EbasMasterCY().lookup_synonym_strict(
                    value, case_sensitive=True, only_historic=True)
            except EbasDomainError:
                # check if a strict synonym exists, maybe even case insensitive
                # lookup name: raise error and add it as suggestion
                try:
                    comp = EbasMasterCY().lookup_synonym_strict(
                        value, case_sensitive=False, only_historic=False)
                except EbasDomainError:
                    raise EbasMetadataError(
                        "Unknown component '{}'".format(value))
                else:
                    raise EbasMetadataError(
                        "Unknown component '{}' (did you mean {}?)"
                        .format(value, comp))
            else:
                raise EbasMetadataWarning(
                    comp, "Legacy componenet name {} changed to {}".format(
                        value, comp))
        return value

    def parse_unit(self, value):
        """
        Parse unit (only NCOM unit, per variable the unit is positional and
        parameter and unit is checked as a quadruple).
        SPECIAL CASE: in addition used from _parse_ebasmetadata_vname_positional
        in NasaAmes input because unit is positional in VNAME.
        Syntax: any unit in any parameter (PM) is valid.
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        pm_ = EbasMasterPM()
        # unit must be unit for **ANY** parameter
        # ppb and ppt can be converted in convert_variables_input
        if pm_.exist_unit(value, datalevel=self.data_level) or \
           value in UnitConvert.converted_units():
            return value
        else:
            raise EbasMetadataError(
                "Unknown unit '{}'".format(value))

    @staticmethod
    def parse_org_code(value, part=None):
        """
        Parse org code.
        Syntax: NN12T (natiuon code, number, tyle L or O)
        Parameters:
            value  value from a tag/value pair
            part   check organization code as part of another metadata element
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        if part:
            part = " part of " + part
        else:
            part = ""
        if value is None or not re.match(r'^[A-Z][A-Z][0-9][0-9][LO]$', value):
            raise EbasMetadataError(
                "syntax error: '{}'. Organization code{} must have the "
                "syntax 'NN12T' (NN: nation code, 12: 2 digit organization "
                "number, T: organization type character [L for lab, O for org])"
                .format(value, part))
        try:
            _ = EbasMasterOR()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "'{}'. Unknown organization code{}"
                .format(value, part))
        return value

    @classmethod
    def parse_method_ref(cls, value):
        """
        Parse method ref.
        Syntax: <OR_CODE>_name
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        reg = re.match(r'^(.....)(_[\-_A-Za-z0-9.+]+)$',
                       value)
        if not reg:
            raise EbasMetadataError(
                "syntax error: '{}'. Should be 'NN12T_AZaz09+.' (NN12T: "
                "Organization code (NN: nation code, 12: 2 digit organization "
                "number, T: organization type character [L for lab, O for org])"
                ", AZaz09+.: free text as method description "
                "(legal characters are A-Z, a-z, 0-9, -, _, +, .))"
                .format(value))
        cls.parse_org_code(reg.group(1), 'method ref')
        # check maximum length:
        if len(value) > 46:
            raise EbasMetadataError("too long: '{}'. Maximum length 46 "
                                    "characters".format(value))
        return value

    @classmethod
    def parse_std_method(cls, value):
        """
        Parse standard method.
        Syntax: any standard_method for any instrument type (SM_STANDARD_METHOD)
        is valid. The combination with instrument type is checked in
        check_interdependent_metadata of the io base class.
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        sm_ = EbasMasterSM()
        if sm_.exist_standardmethod(value):
            return value
        else:
            raise EbasMetadataError(
                "Unknown standard method '{}'".format(value))

    @classmethod
    def parse_cal_scale(cls, value):
        """
        Parse calibration scale.
        Syntax: any calibration scale for any component (CA_CALIBRATION_SCALE)
        is valid. The combination with component is checked in
        check_interdependent_metadata of the io base class.
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        ca_ = EbasMasterCA()
        if ca_.exist_calibrationscale(value):
            return value
        else:
            raise EbasMetadataError(
                "Unknown calibration scale '{}'".format(value))

    @staticmethod
    def parse_inlet_type(value):
        """
        Parse inlet type.
        Syntax: Check with EbasMasterIT
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterIT()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown inlet type '{}'".format(value))
        return value

    @staticmethod
    def parse_inlet_tube_material(value):
        """
        Parse inlet tube material.
        Syntax: Check with EbasMasterIM
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterIM()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown inlet tube material '{}'".format(value))
        return value

    @staticmethod
    def parse_medium(value):
        """
        Parse filter medium.
        Syntax: Check with EbasMasterMD
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        # For now, only the medium can be checked
        # Validity of tuple FT/MD is checked in
        # check_interdependent_metadata
        if EbasMasterMD().exist_medium(value):
            return value
        raise EbasMetadataError(
            "Unknown medium '{}'".format(value))

    @staticmethod
    def parse_flow_rate(value):
        """
        Parse flow rate.
        Syntax: any value in l/min (or m3, or /hour or /day). E.g. <flow> l/min
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        reg = re.match(r"^(\d*(\.\d*)?) *(l|m3) */ *(min|hour|day) *$", value)
        if not reg:
            raise EbasMetadataError(
                "wrong syntax ('{}'). Possible syntax: 999.99 l/min "
                "[m3/hour, m3/day]".format(value))
        try:
            val = float(reg.group(1))
        except ValueError:
            raise EbasMetadataError(
                "illegal float value in ('{}'). Possible syntax: 999.99 l/min "
                "[m3/hour, m3/day]".format(value))
        if reg.group(3) == 'm3':
            val *= 1000.0
        if reg.group(4) == 'hour':
            val /= 60.0
        elif reg.group(4) == 'day':
            val /= 60.0 * 24.0
        if val < 0.1 or val > 3000:
            raise EbasMetadataError(
                'out of bounds (should be between 0.1 and 3000 l/min)')
        return val
            
    @staticmethod
    def parse_filter_prefiring(value):
        """
        Parse filter prefiring.
        Syntax: check with EbasMasterFP, else check for following syntax:
            <temp> K, <duration> h
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterFP()[value]
            return value
        except KeyError:
            reg = re.match(r"^(\d*(\.\d*)?) *K, *(\d*(\.\d*)?) *h$", value)
            if reg:
                try:
                    return (float(reg.group(1)), float(reg.group(3)))
                except ValueError:
                    raise EbasMetadataError(
                        "illegal float value in  ('{}'). "
                        "Possible syntax: {}".format(
                            value, list(EbasMasterFP.META.keys()) +
                            ['<temp> K, <duration> h']))
            else:
                raise EbasMetadataError(
                    "wrong syntax ('{}'). Possible syntax: {}".format(
                        value, list(EbasMasterFP.META.keys()) +
                        ['<temp> K, <duration> h']))
        return value

    @staticmethod
    def print_filter_prefiring(value):
        """
        Print filter prefiring.
        Syntax: value is ether string (print as is), or tupel with temp and
            time. In this case, print:
            <temp> K, <duration> h
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        if isinstance(value, string_types):
            return value
        res = ''
        if value[0] is not None:
            res += '{} K,'.format(value[0])
        else:
            res += ','
        if value[1] is not None:
            res += ' {} h'.format(value[1])
        return res

    @staticmethod
    def parse_filter_conditioning(value):
        """
        Parse filter confitioning.
        Syntax:
            None (string "None") or
            <temp> K, <RH> %, <duration> h
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        if value == "None":
            return value
        else:
            reg = re.match(
                r"^(\d*(\.\d*)?) *K, *(\d*(\.\d*)?) *% *RH, *(\d*(\.\d*)?) *h$",
                value)
            if reg:
                temp, rh_, time = reg.group(1), reg.group(3), reg.group(5)
                try:
                    temp = float(temp)
                    rh_ = float(rh_)
                    time = float(time)
                except ValueError:
                    raise EbasMetadataError(
                        "illegal float value in ('{}'). Possible syntax: 'None' "
                        "or '<temp> K, <RH> %RH, <duration> h'".format(value))

                return (temp, rh_, time)
            raise EbasMetadataError(
                "wrong syntax ('{}'). Possible syntax: 'None' or "
                "'<temp> K, <RH> %RH, <duration> h'".format(value))

    @staticmethod
    def print_filter_conditioning(value):
        """
        Print filter conditioning.
        Syntax: value is ether string 'None' (print as is), or
            tupel with temp, RH and duration. In this case, print:
            <temp> K, <RH> %, <duration> h
        Parameters:
            value  value from a tag/value pair
        Returns:
            strig for output
        """
        if isinstance(value, string_types):
            return value
        res = ''
        if value[0] is not None:
            res += '{} K,'.format(value[0])
        else:
            res += ','
        if value[1] is not None:
            res += ' {} %RH,'.format(value[1])
        else:
            res += ' ,'
        if value[2] is not None:
            res += ' {} h'.format(value[2])
        return res

    @staticmethod
    def parse_filter_type(value):
        """
        Parse filter type.
        Syntax: controlled list, only used for AE33 lev0 per now.
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        allowed = ('Magee AE33-FT', 'Magee M8050', 'Magee M8060')
        if value in allowed:
            return value
        # backward compatibility 2024-06, can be taken out after some years...
        if value == 'Magee 8050':
            raise EbasMetadataWarning(
                'Magee M8050', "Legacy filter type {} changed to {}".format(
                    value, 'Magee M8050'))
        if value == 'Magee 8060':
            raise EbasMetadataWarning(
                'Magee M8060', "Legacy filter type {} changed to {}".format(
                    value, 'Magee M8060'))
        raise EbasMetadataError('Unknown filter type {} (allowed: {})'.format(
            value, ', '.join(allowed)))

    @staticmethod
    def parse_sample_prep(value):
        """
        Parse sample preparation.
        Syntax: check with EbasMasterSP
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterSP()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown sample preparation '{}'".format(value))
        return value

    @staticmethod
    def parse_ozone_corr(value):
        """
        Parse Ozone correction string.
        Syntax: values from EbasMasterOC
        Parameters:
            value value from a tag/value pair
        Returns:
            legal value
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterOC()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown ozone correction '{}'".format(value))
        return value

    @staticmethod
    def parse_watervapor_corr(value):
        """
        Parse Water vapor correction string.
        Syntax: values from EbasMasterWC
        Parameters:
            value value from a tag/value pair
        Returns:
            legal value
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterWC()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown water vapor correction '{}'".format(value))
        return value

    @staticmethod
    def parse_zero_span_type(value):
        """
        Parse Zero/span check type.
        Syntax: values from EbasMasterZT
        Parameters:
            value value from a tag/value pair
        Returns:
            legal value
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterZT()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown zero/span check type '{}'".format(value))
        return value

    @staticmethod
    def parse_blank_corr(value):
        """
        Parse blank correction.
        Syntax: two different values allowed:
         Blank corrected     ==> True
         Not blank corrected ==> False
        Parameters:
            value value from a tag/value pair
        Returns:
            converted value as bool
        Raises:
            EbasMetadataError if not legal
        """
        if value == 'Blank corrected':
            return True
        if value == 'Not blank corrected':
            return False
        raise EbasMetadataError("value not allowed (only 'Blank corrected' and "
                                "'Not blank corrected')")

    @staticmethod
    def parse_artifact_corr(value):
        """
        Parse artifact correction.
        Syntax: check with EbasMetAC
        Parameters:
            value value from a tag/value pair
        Returns:
            converted value as bool
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterAC()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown artifact correction code '{}'".format(value))
        return value

    @staticmethod
    def parse_charring_corr(value):
        """
        Parse charring correction.
        Syntax: check with EbasMetCC
        Parameters:
            value value from a tag/value pair
        Returns:
            converted value as bool
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterCC()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown charring correction code '{}'".format(value))
        return value

    @staticmethod
    def print_blank_corr(value):
        """
        Creates an output string for blank correction.
        Syntax:
         True  ==> Blank corrected
         False ==> Not blank corrected
        Parameters:
            value   Boolean
        Returns:
            str
        """
        if value:
            return "Blank corrected"
        return "Not blank corrected"

    @staticmethod
    def parse_ht_control(value):
        """
        Parse Humidity/temperature control.
        Syntax: controlled by master data table
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        try:
            _ = EbasMasterHT()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown humidity/temperature control code '{}'".format(value))
        return value

    @staticmethod
    def parse_vol_std_temp(value):
        """
        Parse Volume standard Temperature.
        Syntax: 9*.99*K or 'ambient' or 'instrument internal'
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        vt_ = EbasMasterVT()
        try:
            _ = vt_[value]
            return value
        except KeyError:
            new = value.lower()
            try:
                _ = vt_[new]
                raise EbasMetadataWarning(
                    new, "Volume std. temperature value '{}' changed to '{}'".
                    format(value, new))
            except:
                pass
        
        reg = re.match(r'^([0-9]+(\.[0-9]*)?) *K$', value)
        if not reg:
            raise EbasMetadataError(
                "syntax error, should be a valid temperature in Kelvin (e.g. "
                "'273.15 K') or one of ('ambient', 'instrument internal')")
        if float(reg.group(1)) < 263.15 or float(reg.group(1)) > 298.15:
            raise EbasMetadataError(
                "range error (currently 263.15 K - 298.15 K is allowed, please "
                "contact EBAS support if you operate with other standard "
                "conditions).")
        return float(reg.group(1))

    @staticmethod
    def print_vol_std_temp(value):
        """
        Creates an output string for Volume standard Temperature.
        Syntax:
         ambient
         instrument internal
         <value> K
        Parameters:
            value   'ambient', 'instrument internal' or real
        Returns:
            str
        """
        if isinstance(value, Number):
            return "{:.2f} K".format(value)
        return value

    @staticmethod
    def parse_vol_std_press(value):
        """
        Parse Volume standard Pressure.
        Syntax: 9*.99*K or 'ambient' or 'instrument internal'
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        vp_ = EbasMasterVP()
        try:
            _ = vp_[value]
            return value
        except KeyError:
            new = value.lower()
            try:
                _ = vp_[new]
                raise EbasMetadataWarning(
                    new, "Volume std. pressure value '{}' changed to '{}'".
                    format(value, new))
            except:
                pass

        reg = re.match(r'^([0-9]+(\.[0-9]*)?) *hPa$', value)
        if not reg:
            raise EbasMetadataError(
                "syntax error, should be a valid pressure in hPa (e.g. "
                "'1013.25 hPa') or one of ('ambient', 'instrument internal')")
        if float(reg.group(1)) < 540.0 or float(reg.group(1)) > 1020.0:
            raise EbasMetadataError(
                "range error (currently 540.0 hPa - 1020.0 hPa is allowed, "
                "please contact EBAS support if you operate with other "
                "standard conditions).")
        else:
            return float(reg.group(1))

    @staticmethod
    def print_vol_std_press(value):
        """
        Creates an output string for Volume standard pressure.
        Syntax:
         ambient
         instrument internal
         <value> hPa
        Parameters:
            value   'ambient', 'instrument internal' or real
        Returns:
            str
        """
        if isinstance(value, Number):
            return "{:.2f} hPa".format(value)
        return value

    @staticmethod
    def parse_zero_negative(value):
        """
        Parse Zero/negative values code.
        Syntax: valid values defined in masterdata table ZN.
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        # legacy: lower case zero was used until Oct. 2014. Allow lowercase
        # for backward compatibility
        if re.match('^zero', value):
            new = re.sub('^zero', 'Zero', value)
            raise EbasMetadataWarning(
                new, "Zero/negative values code '{}' changed to '{}'".
                format(value, new))
        try:
            _ = EbasMasterZN()[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "Unknown zero/negative values code '{}'".format(value))
        return value

    @classmethod
    def parse_qa_measure_id(cls, value):
        """
        Parse QA measure ID.
        Syntax: either in EbasMasterQM or generic syntax:
            <labcode>_reference_calibration_<dateYYYYMMDD>
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        # check if in Master Data already:
        qm_ = EbasMasterQM()
        try:
            _ = qm_[value]
            return value
        except KeyError:
            refcal = qm_.new_reference_calibration(value)
            if not refcal:
                raise EbasMetadataError("illegal QA measure ID '{}'".format(value))
            cls.parse_org_code(refcal[0], 'QA measure ID')
            try:
                _ = datetime.datetime.strptime(refcal[1], '%Y%m%d')
            except ValueError:
                raise EbasMetadataError(
                    "date used in  QA measure ID '{}' is invalid".format(value))
            return value

    @staticmethod
    def parse_url(value):
        """
        Parse QA document URL.
        Syntax: any valif http:// - url
        TODO: general controlled list of measures needs to be implemented
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if legal
        Raises:
            EbasMetadataError if not legal
        """
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
            r'localhost|' # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not regex.match(value):
            raise EbasMetadataError("syntax error: '{}', must be a valid URL"
                                    .format(value))
        return value

    @staticmethod
    def parse_qa_outcome(value):
        """
        Parse QA outcome.
        Syntax: valid values in EbasMasterQO
        Parameters:
            value  value from a tag/value pair
        Returns:
            value if valid
        Raises:
            EbasMetadataError if not legal
        """
        qo_ = EbasMasterQO()
        try:
            _ = qo_[value]
            return value
        except KeyError:
            raise EbasMetadataError(
                "illegal value '{}', allowed values: {}"
                .format(value, ', '.join(["'{}'".format(x)
                                          for x in qo_.META])))

    @staticmethod
    def print_qa_outcome(value):
        """
        Creates an output string for 'QA outcome'.
        Syntax: only 2 values allowed:
            pass
            no pass
        Parameters:
            value  value (bool)
        Returns:
            output string (True=pass, False=no pass)
        """
        if value:
            return 'pass'
        return 'no pass'

    @staticmethod
    def parse_inlet_diffusion_loss_data(value):
        """
        Parse Inlet diffusion loss data.
        """
        res = []
        for section in list_splitter(value, ","):
            reg = re.match(
               r'^\s*([0-9][0-9]*(\.[0-9]*)?)\s*m\s\s*([0-9][0-9]*(\.[0-9]*)?)\s*l\/min\s*$',
               section)
            if reg:
                res.append([float(reg.group(1)), float(reg.group(3))])
            else:
                raise EbasMetadataError(
                    "syntax error. Should be like '2.1 m 1.2 l/min[, ...]")
        return res

    @staticmethod
    def print_inlet_diffusion_loss_data(value):
        """
        Creates an output string for Inlet diffusion loss data.
        """
        return ', '.join(['{} m {} l/min'.format(section[0], section[1])
                          for section in value])

    @staticmethod
    def parse_float_unit(value):
        """
        Parse number with unit (e.g. detection limit, uncertenty).
        Syntax: 99.99 unit
        Blank between number and unit is necessary (unit can be e.g. "1/cm3"
        -> 0.001/cm3).
        Parameters:
            value  value from a tag/value pair (string: number and unit)
        Returns:
            (number, unit)
        Raises:
            EbasMetadataError if not legal
        """
        try:
            reg = re.match(r'^([0-9+\-\.E]+) *(.+)$', value,
                           flags=re.IGNORECASE)
            if not reg:
                raise ValueError()
            value = float(reg.group(1))
        except ValueError:
            raise EbasMetadataError('syntax error')
        return (float(reg.group(1)), reg.group(2).strip())

    @staticmethod
    def print_float_unit(value):
        """
        Creates an output string for a number/unit combination (e.g. detection
        limit, uncertainty).
        Syntax: 99.99 unit
        Blank between number and unit is necessary (unit can be e.g. "1/cm3"
        -> 0.001/cm3).
        Parameters:
            value   tuple (float, string)
        Returns:
            str
        """
        return "{} {}".format(value[0], value[1])

    def __init__(self, data_version, data_format, data_level=None,
                 metadata_options=0):
        """
        Initialize EbasMetadata object
        Parameters:
            data_version    'EBAS_1', 'EBAS_1.1'
            data_format     constants defined in ebas.io.base:
                            EBAS_IOFORMAT_NASA_AMES, EBAS_IOFORMAT_CSV,
                            EBAS_IOFORMAT_XML
            data_level      data level, string
                            (some exceptions for some data levels)
            metadata_options
                            options for output (bitfield):
                            EBAS_IOMETADATA_OPTION_SETKEY
        """
        self.data_version = data_version
        self.data_format = data_format
        self.data_level = data_level


        # defines possible metadata elements for datasets in EBAS Nasa Ames
        # files depending on the data version
        # key: The name used in the matadata dictionaries of the NasaAmes
        #      object. (NasaAmes.metadata or NasaAmes.variables[i].metadata)
        # tag: Tag used in the NasaAmes file header
        #      (either in the NNCOM lines (syntax: "tag: value")
        #       or in the VNAMES lines (syntax: tag=value))
        # main: specifies the cardinality of the element in the main header
        #       (NNCOM lines)
        #       Bitfield:
        #       0 not allowed
        #       1 allowed but not mandatory
        #       2 mandatory on export
        #       4 mandatory on import
        #       8 critical on import (if missing, exit after reading header)
        # vname: specifies the cardinality of the element in the vname line.
        #       Bitfield:
        #       0 not allowed
        #       1 allowed but not mandatory
        #       2 mandatory on export (not used)
        #       4 mandatory on import
        #       8 critical on import (if missing, exit after reading header)
        # unit: special case for elements that need an additional unit in the
        #       NasaAmes file, e.g. "Station altitude"
        # default: specifies the default value to be set if the emlement is not
        #          set.
        # data_level: array of strings. This metadata element is only valid in
        #             certain data levels (e.g. level 0 metadata)
        
        ebasmetadata = Substitute('data_version', {
            'EBAS_1': [
                {
                    'key': 'datadef',
                    'tag': 'Data definition',
                    'main': 6, 'vname': 0,
                    'parser': None
                },
                {
                    'key': 'type',
                    'tag': 'Set type code',
                    'main': 6, 'vname': 0,
                    'parser': self.parse_ds_type,
                },
                {
                    'key': 'regime',
                    'tag': 'Regime',
                    'main': 6, 'vname': 0,
                    'parser': self.parse_regime,
                },
                {
                    'key': 'station_code',
                    'tag': 'Station code',
                    'main': 6, 'vname': 0,
                    'parser': self.parse_station_platform_code
                },
                {
                    'key': 'platform_code',
                    'tag': 'Platform code',
                    'main': 6, 'vname': 0,
                    'parser': self.parse_station_platform_code
                },
                {
                    'key': 'startdate',
                    'tag': 'Startdate',
                    'main': 10, 'vname': 0,
                    'parser': self.parse_datetime_dataversion,
                    'printer': self.print_datetime
                },
                {
                    'key': 'timeref',
                    'tag': 'Timeref',
                    'main': 10, 'vname': 0,
                    'parser': self.parse_timeref,
                },
                {
                    'key': 'revdate',
                    'tag': 'Revision date',
                    'main': 6, 'vname': 1,
                    'parser': self.parse_datetime_dataversion,
                    'printer': self.print_datetime
                },
                {
                    'key': 'statistics',
                    'tag': 'Statistics',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_statistics,
                    'default': 'arithmetic mean'
                },
                {
                    'key': 'comp_name',
                    'tag': 'Component',
                    # comp name is positional in vname, no keyword allowed
                    'main': 6, 'vname': 0,
                    # parser: per se, all component names are valid, but for
                    # each variable, the component needs to be checked
                    # (--> check interdependent metadata)
                },
                {
                    'key': 'unit',
                    'tag': 'Unit',
                    # unit is positional in vname, no keyword allowed
                    'main': 6, 'vname': 0
                },
                {
                    'key': 'matrix',
                    'tag': 'Matrix',
                    'main': 6, 'vname': 1,
                    # parser: per se, all matrix names are valid, but for
                    # each variable, the matrix needs to be checked
                    # (--> check interdependent metadata)
                },
                {
                    'key': 'period',
                    'tag': 'Period code',
                    'main': 6, 'vname': 0,
                    # period code is a file atrribute not allowed for vname
                    'parser': self.parse_period_rescode
                },
                {
                    'key': 'resolution',
                    'tag': 'Resolution code',
                    'main': 6, 'vname': 0,
                    # rescode is a file atrribute not allowed for vname
                    'parser': self.parse_period_rescode
                },
                {
                    'key': 'lab_code',
                    'tag': 'Laboratory code',
                    'main': 6, 'vname': 1,
                    'parser': self.parse_org_code
                },
                {
                    'key': 'instr_type',
                    'tag': 'Instrument type',
                    'main': 6, 'vname': 1,
                    'parser': self.parse_instr_type,
                },
                {
                    'key': 'instr_name',
                    'tag': 'Instrument name',
                    'main': 6, 'vname': 1,
                    'parser': self.parse_instr_name,
                },
                {
                    'key': 'method',
                    'tag': 'Method ref',
                    'main': 6, 'vname': 1,
                    'parser': self.parse_method_ref,
                },
                {
                    'key': 'ext_lab',
                    'tag': 'Ext. lab. code',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_org_code
                },
                {
                    'key': 'rescode_sample',
                    'tag': 'Add. qualifier',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_period_rescode,
                },
                {
                    'key': 'mea_height',
                    'tag': 'Height AGL',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='m'),
                    'printer': self.print_generic_factory(unit_='m')
                },
                {
                    'key': 'filename',
                    'tag': 'File name',
                    'main': 2, 'vname': 0,
                },
                {
                    'key': None,
                    'tag': 'Ext. meth. ref',
                    'main': 1, 'vname': 0,
                },
                {
                    'key': None,
                    'tag': 'File name ext',
                    'main': 1, 'vname': 0,
                },
            ],
            'EBAS_1.1': [
                {
                    'key': 'datadef',
                    'tag': 'Data definition',
                    'nc_tag': 'data_definition',
                    # this is a file global attribute
                    'main': 6, 'vname': 0,
                    # no parser needed, this needs to be pre parsed before
                    # object instanciation (_get_file_format)
                    # default printer
                },
                {
                    'key': 'license',
                    'tag': 'Data license',
                    'nc_tag': 'data_license',
                    Merge('data_format'): {
                        Default: {'main': 1,'vname': 1},
                        # PR is file global in Nasa Ames, no keyword allowed
                        # thus, the license is also file global
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                    'parser': self.parse_license,
                    # no printer needed
                },
                {
                    'key': 'citation',
                    'tag': 'Citation',
                    'nc_tag': 'citation',
                    # file atrribute, not allowed for vname
                    'main': 1, 'vname': 0,
                    # no parser needed
                    # no printer needed
                },
                {
                    'key': 'type',
                    'tag': 'Set type code',
                    'nc_tag': 'set_type_code',
                    # file atrribute, not allowed for vname
                    'main': 6, 'vname': 0,
                    'parser': self.parse_ds_type,
                },
                {
                    'key': 'timezone',
                    'tag': 'Timezone',
                    'nc_tag': 'timezone',
                    # file atrribute, not allowed for vname
                    'main': 6, 'vname': 0,
                    'parser': self.parse_timezone,
                },
                {
                    'key': 'timeref',
                    'tag': 'Timeref',
                    'nc_tag': 'timeref',
                    # file atrribute, not allowed for vname
                    'main': 1, 'vname': 0,
                    'parser': self.parse_timeref,
                },
                {
                    'key': 'filename',
                    'tag': 'File name',
                    'nc_tag': 'file_name',
                    # file atrribute, not allowed for vname
                    'main': 2, 'vname': 0,
                },
                {
                    'key': 'doi',
                    'tag': 'Represents DOI',
                    'nc_tag': 'represents_doi',
                    # file atrribute, not allowed for vname
                    'main': 1,
                    'vname': 0,
                    'parser': self.parse_doi,
                    'printer': self.print_doi,
                },
                {
                    'key': 'doi_list',
                    'tag': 'Contains data from DOI',
                    'nc_tag': 'contains_doi',
                    # file atrribute, not allowed for vname
                    'main': 1,
                    'vname': 0,
                    'parser': self.parse_doi_list,
                    'printer': self.print_doi_list,
                },
                {
                    'key': 'creation_time',
                    'tag': 'File creation',
                    'nc_tag': 'file_creation',
                    # file atrribute, not allowed for vname
                    'main': 2, 'vname': 0,
                    'parser': self.parse_datetime_creation,
                    'printer': self.print_datetime_state
                    # This is for backwards compatibility with old files.
                    # File creation used to be second resolution, later it was
                    # changed to microsecond.
                    # So we accept both on read, but write microseconds.
                },
                {
                    'key': 'export_state',
                    'tag': 'Export state',
                    'nc_tag': 'export_state',
                    # file atrribute, not allowed for vname
                    'main': 1, 'vname': 0,
                    'parser': self.parse_datetime_state,
                    'printer': self.print_datetime_state
                },
                {
                    'key': 'export_filter',
                    'tag': 'Export filter',
                    'nc_tag': 'export_filter',
                    # file atrribute, not allowed for vname
                    'main': 1, 'vname': 0,
                    'parser': self.parse_export_filter,
                    'printer': self.print_export_filter,
                },
                {
                    'key': 'startdate',
                    'tag': 'Startdate',
                    'nc_tag': 'startdate',
                    # file atrribute, not allowed for vname
                    # critically on input, data will not be read if missing
                    # also part of file name convention: must be mand. on output
                    'main': 10, 'vname': 0,
                    'parser': self.parse_datetime_dataversion,
                    'printer': self.print_datetime
                },
                {
                    'key': 'setkey',
                    'tag': 'Dataset key',
                    'nc_tag': 'dataset_key',
                    'main': 1, 'vname': 2,
                    'parser': self.parse_setkey,
                    Merge('metadata_options'): {
                        Default: {'main': 0, 'vname': 0},
                        # metadata_option EBAS_IOMETADATA_OPTION_SETKEY:
                        # setkey is mandatory for VNAME on input and output
                        BitAnd(EBAS_IOMETADATA_OPTION_SETKEY): \
                            {'main': 1, 'vname': 6}},
                },
                {
                    'key': 'revdate',
                    'tag': 'Revision date',
                    'nc_tag': 'revision_date',
                    # file atrribute, not allowed for vname
                    # also part of file name convention: must be mand. on output
                    'main': 6, 'vname': 1,
                    'parser': self.parse_datetime_dataversion,
                    'printer': self.print_datetime
                },
                {
                    'key': 'revision',
                    'tag': 'Version',
                    'nc_tag': 'version',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(len_=[0, 15])
                },
                {
                    'key': 'revdesc',
                    'tag': 'Version description',
                    'nc_tag': 'version_description',
                    'main': 1, 'vname': 1,
                },
                {
                   'key': 'input_dataset',
                    'tag': 'Input dataset',
                    'nc_tag': 'input_dataset',
                    'parser': self.parse_input_dataset,
                    'printer': self.print_generic_list,
                    'main': 1, 'vname': 0,
                },
                {
                    'key': 'software',
                    'tag': 'Software',
                    'nc_tag': 'software',
                    #'parser': self.parse_software,
                    'printer': self.print_generic_list,
                    'main': 1, 'vname': 0,
                },
                {
                    'key': 'statistics',
                    'tag': 'Statistics',
                    'nc_tag': 'statistics',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_statistics,
                    'default': 'arithmetic mean'
                },
                {
                    'key': 'datalevel',
                    'tag': 'Data level',
                    'nc_tag': 'data_level',
                    # file atrribute, not allowed for vname
                    # also part of file name convention: must be mand. on output
                    'main': 2, 'vname': 1
                    # no parser needed, this needs to be pre parsed before
                    # object instanciation (_get_file_format)
                    # default printer
                },
                {
                    'key': 'period',
                    'tag': 'Period code',
                    'nc_tag': 'period_code',
                    # file atrribute, not allowed for vname
                    # also part of file name convention: must be mand. on output
                    'main': 6, 'vname': 0,
                    'parser': self.parse_period_rescode
                },
                {
                    'key': 'resolution',
                    'tag': 'Resolution code',
                    'nc_tag': 'resolution_code',
                    # file atrribute, not allowed for vname
                    # also part of file name convention: must be mand. on output
                    'main': 6, 'vname': 0,
                    'parser': self.parse_period_rescode
                },
                {
                    'key': 'duration',
                    'tag': 'Sample duration',
                    'nc_tag': 'sample_duration',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_period_rescode
                },
                {
                    'key': 'rescode_sample',
                    'tag': 'Orig. time res.',
                    'nc_tag': 'orig_time_res',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_period_rescode
                },
                {
                    # deprecated in EBAS_1.1, but substituted by Orig. time res.
                    # (same syntax) here defined for backwards compatibility to
                    # EBAS_1
                    'key': 'rescode_sample',
                    'tag': 'Add. qualifier',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_period_rescode,
                    'renamed_tag': 'Orig. time res.'
                },
                {
                    'key': 'station_code',
                    'tag': 'Station code',
                    'nc_tag': 'station_code',
                    # also part of file name convention: must be mand. on output
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: station code is mandatory on input and
                        # output, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 6, 'vname': 0}},
                    'parser': self.parse_station_platform_code
                },
                {
                    'key': 'platform_code',
                    'tag': 'Platform code',
                    'nc_tag': 'platform_code',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: mandatory on input, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 2, 'vname': 0}},
                    'parser': self.parse_station_platform_code
                },
                {
                    'key': 'station_name',
                    'tag': 'Station name',
                    'nc_tag': 'station_name',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_wdca_id',
                    'tag': 'Station WDCA-ID',
                    'nc_tag': 'station_wdca_id',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    # Station WDCA-Name renamed to Station GAW-Name
                    'key': 'station_gaw_name',
                    'tag': 'Station WDCA-Name',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                    'renamed_tag': 'Station GAW-Name',
                },
                {
                    'key': 'station_gaw_id',
                    'tag': 'Station GAW-ID',
                    'nc_tag': 'station_gaw_id',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_gaw_name',
                    'tag': 'Station GAW-Name',
                    'nc_tag': 'station_gaw_name',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_airs_id',
                    'tag': 'Station AIRS-ID',
                    'nc_tag': 'station_airs_id',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_other_ids',
                    'tag': 'Station other IDs',
                    'nc_tag': 'station_other_ids',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                    'parser': self.parse_station_other_ids
                },
                {
                    'key': 'station_state_code',
                    'tag': 'Station state/province',
                    'nc_tag': 'station_state_province',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_landuse',
                    'tag': 'Station land use',
                    'nc_tag': 'station_land_use',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_setting',
                    'tag': 'Station setting',
                    'nc_tag': 'station_setting',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_gaw_type',
                    'tag': 'Station GAW type',
                    'nc_tag': 'station_gaw_type',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_wmo_region',
                    'tag': 'Station WMO region',
                    'nc_tag': 'station_wmo_region',
                    'parser': self.parse_station_wmo_region,
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_latitude',
                    'tag': 'Station latitude',
                    'nc_tag': 'station_latitude',
                    'parser': self.parse_latitude,
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_longitude',
                    'tag': 'Station longitude',
                    'nc_tag': 'station_longitude',
                    'parser': self.parse_longitude,
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                },
                {
                    'key': 'station_altitude',
                    'tag': 'Station altitude',
                    'nc_tag': 'station_altitude',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # Nasa Ames: allowed in main, not allowed in VNAME
                        # (-> only one station per file)
                        EBAS_IOFORMAT_NASA_AMES: {'main': 1, 'vname': 0}},
                    'parser': self.parse_generic_factory(unit_='m'),
                    'printer': self.print_generic_factory(unit_='m')
                },
                {
                    'key': 'mea_latitude',
                    'tag': 'Measurement latitude',
                    'nc_tag': 'measurement_latitude',
                    'parser': self.parse_latitude,
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'mea_longitude',
                    'tag': 'Measurement longitude',
                    'nc_tag': 'measurement_longitude',
                    'parser': self.parse_longitude,
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'mea_altitude',
                    'tag': 'Measurement altitude',
                    'nc_tag': 'measurement_altitude',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='m'),
                    'printer': self.print_generic_factory(unit_='m')
                },
                {
                    'key': 'mea_height',
                    'tag': 'Measurement height',
                    'nc_tag': 'measurement_height',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='m'),
                    'printer': self.print_generic_factory(unit_='m')
                },
                {
                    # deprecated in EBAS_1.1, but substituted by
                    # Measurement Height (same syntax)
                    # here defined for backwards compatibility to EBAS_1
                    'key': 'mea_height',
                    'tag': 'Height AGL',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='m'),
                    'printer': self.print_generic_factory(unit_='m'),
                    'renamed_tag': 'Measurement height'
                },
                {
                    'key': 'regime',
                    'tag': 'Regime',
                    'nc_tag': 'regime',
                    'main': 2, 'vname': 1,
                    'parser': self.parse_regime,
                },
                {
                    'key': 'comp_name',
                    'tag': 'Component',
                    'nc_tag': 'component',
                    # comp name is positional in vname, no keyword allowed
                    # also part of file name convention: must be mand. on output
                    'main': 2,
                    Merge('data_format'): {
                        Default: {'vname': 1},
                        # comp_name is positional in vname, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {'vname': 0}},
                    # parser: per se, all component names are valid, but for
                    # each variable, the component needs to be checked
                    # (--> check interdependent metadata)
                },
                {
                    'key': 'unit',
                    'tag': 'Unit',
                    'nc_tag': 'unit',
                    'main': 1,
                    Merge('data_format'): {
                        Default: {'vname': 2},
                        # unit is positional in vname, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {'vname': 0}},
                },
                {
                    'key': 'matrix',
                    'tag': 'Matrix',
                    'nc_tag': 'matrix',
                    # also part of file name convention: must be mand. on output
                    'main': 2, 'vname': 4,
                    'parser': self.parse_matrix
                },
                {
                    'key': 'lab_code',
                    'tag': 'Laboratory code',
                    'nc_tag': 'laboratory_code',
                    # also part of file name convention: must be mand. on output
                    'main': 2, 'vname': 4,
                    'parser': self.parse_org_code
                },
                {
                    'key': 'instr_type',
                    'tag': 'Instrument type',
                    'nc_tag': 'instrument_type',
                    # also part of file name convention: must be mand. on output
                    'main': 2, 'vname': 4,
                    'parser': self.parse_instr_type,
                },
                {
                    'key': 'instr_name',
                    'tag': 'Instrument name',
                    'nc_tag': 'instrument_name',
                    # also part of file name convention: must be mand. on output
                    'main': 2, 'vname': 4,
                    'parser': self.parse_instr_name,
                },
                {
                    'key': 'instr_manufacturer',
                    'tag': 'Instrument manufacturer',
                    'nc_tag': 'instrument_manufacturer',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'instr_model',
                    'tag': 'Instrument model',
                    'nc_tag': 'instrument_model',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'instr_serialno',
                    'tag': 'Instrument serial number',
                    'nc_tag': 'instrument_serial_number',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'sensor_type',
                    'tag': 'Sensor type',
                    'nc_tag': 'sensor_type',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_sensor_type,
                },
                {
                    'key': 'ana_lab_code',
                    'tag': 'Analytical laboratory code',
                    'nc_tag': 'analytical_laboratory_code',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_org_code
                },
                {
                    'key': 'ana_technique',
                    'tag': 'Analytical measurement technique',
                    'nc_tag': 'analytical_measurement_technique',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_ana_technique,
                },
                {
                    'key': 'ana_instr_name',
                    'tag': 'Analytical instrument name',
                    'nc_tag': 'analytical_instrument_name',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_instr_name,
                },
                {
                    'key': 'ana_instr_manufacturer',
                    'tag': 'Analytical instrument manufacturer',
                    'nc_tag': 'analytical_instrument_manufacturer',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'ana_instr_model',
                    'tag': 'Analytical instrument model',
                    'nc_tag': 'analytical_instrument_model',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'ana_instr_serialno',
                    'tag': 'Analytical instrument serial number',
                    'nc_tag': 'analytical_instrument_serial_number',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'ext_lab',
                    'tag': 'Ext. lab. code',
                    'nc_tag': 'ext_lab_code',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_org_code
                },
                {
                    'key': 'method',
                    'tag': 'Method ref',
                    'nc_tag': 'method_ref',
                    # also part of file name convention: must be mand. on output
                    'main': 2, 'vname': 4,
                    'parser': self.parse_method_ref,
                },
                {
                    'key': 'std_method',
                    'tag': 'Standard method',
                    'nc_tag': 'standard_method',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_std_method,
                },
                {
                    'key': 'cal_scale',
                    'tag': 'Calibration scale',
                    'nc_tag': 'calibration_scale',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_cal_scale,
                },
                {
                    'key': 'cal_std_id',
                    'tag': 'Calibration standard ID',
                    'nc_tag': 'calibration_standard_id',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'sec_std_id',
                    'tag': 'Secondary standard ID',
                    'nc_tag': 'secondary_standard_id',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'inlet_type',
                    'tag': 'Inlet type',
                    'nc_tag': 'inlet_type',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_inlet_type,
                },
                {
                    'key': 'inlet_desc',
                    'tag': 'Inlet description',
                    'nc_tag': 'inlet_description',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'inlet_tube_material',
                    'tag': 'Inlet tube material',
                    'nc_tag': 'inlet_tube_material',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_inlet_tube_material,
                },
                {
                    'key': 'inlet_tube_outerD',
                    'tag': 'Inlet tube outer diameter',
                    'nc_tag': 'inlet_tube_outer_diameter',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='mm'),
                    'printer': self.print_generic_factory(unit_='mm')
                },
                {
                    'key': 'inlet_tube_innerD',
                    'tag': 'Inlet tube inner diameter',
                    'nc_tag': 'inlet_tube_inner_diameter',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='mm'),
                    'printer': self.print_generic_factory(unit_='mm')
                },
                {
                    'key': 'inlet_tube_length',
                    'tag': 'Inlet tube length',
                    'nc_tag': 'inlet_tube_length',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='m'),
                    'printer': self.print_generic_factory(unit_='m')
                },
                {
                    'key': 'time_inlet_to_converter',
                    'tag': 'Time from entry inlet line to entry of converter',
                    'nc_tag': 'time_from_entry_inlet_line_to_entry_of_converter',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='s'),
                    'printer': self.print_generic_factory(unit_='s'),
                    Condition('data_level'): IsIn(['0']),
                    # only used in NOx lev 0 template
                    # only implemeted in ebas.io, ignored in domain
                },
                {
                    'key': 'time_converter_or_bypass_line',
                    'tag': 'Duration of stay in converter or bypass line',
                    'nc_tag': 'duration_of_stay_in_converter_or_bypass_line',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='s'),
                    'printer': self.print_generic_factory(unit_='s'),
                    Condition('data_level'): IsIn(['0']),
                    # only used in NOx lev 0 template
                    # only implemeted in ebas.io, ignored in domain
                },
                {
                    'key': 'time_stay_converter',
                    'tag': 'Duration of stay in converter',
                    'nc_tag': 'duration_of_stay_in_converter',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='s'),
                    'printer': self.print_generic_factory(unit_='s'),
                    Condition('data_level'): IsIn(['0']),
                    # only used in NOx lev 0 template
                    # only implemeted in ebas.io, ignored in domain
                },
                {
                    'key': 'converter_temp',
                    'tag': 'Converter temperature',
                    'nc_tag': 'converter_temperature',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='K'),
                    'printer': self.print_generic_factory(unit_='K'),
                    Condition('data_level'): IsIn(['0']),
                    # only used in NOx lev 0 template
                    # only implemeted in ebas.io, ignored in domain
                },
                {
                    'key': 'maintenance_desc',
                    'tag': 'Maintenance description',
                    'nc_tag': 'maintenance_description',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'flow_rate',
                    'tag': 'Flow rate',
                    'nc_tag': 'flow_rate',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_flow_rate,
                    'printer': self.print_generic_factory(unit_='l/min')
                },
                {
                    'key': 'filter_face_velocity',
                    'tag': 'Filter face velocity',
                    'nc_tag': 'filter_face_velocity',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        unit_='cm/s', range_=[1.0, 150.0]),
                    'printer': self.print_generic_factory(unit_='cm/s'),
                },
                {
                    'key': 'filter_area',
                    'tag': 'Exposed filter area',
                    'nc_tag': 'exposed_filter_area',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        unit_='cm2', range_=[0.5, 500.0]),
                    # ad thresholds: 2018-05-28, KEY:
                    # biggest filter seen was > 400 cm2
                    'printer': self.print_generic_factory(unit_='cm2'),
                },
                {
                    'key': 'filter_descr',
                    'tag': 'Filter description',
                    'nc_tag': 'filter_description',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'medium',
                    'tag': 'Medium',
                    'nc_tag': 'medium',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_medium
                },
                {
                    'key': 'coating_solution',
                    'tag': 'Coating/Solution',
                    'nc_tag': 'coating_solution',
                    'main': 1, 'vname': 1
                },
                {
                    'key': 'filter_prefiring',
                    'tag': 'Filter prefiring',
                    'nc_tag': 'filter_prefiring',
                    'main': 1, 'vname': 1,
                    # just accepted and ignored:
                    # domain, DB
                    'parser': self.parse_filter_prefiring,
                    'printer': self.print_filter_prefiring,
                },
                {
                    'key': 'filter_conditioning',
                    'tag': 'Filter conditioning',
                    'nc_tag': 'filter_conditioning',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_filter_conditioning,
                    'printer': self.print_filter_conditioning,
                },
                {
                    'key': 'filter_type',
                    'tag': 'Filter type',
                    'nc_tag': 'filter_type',
                    'main': 1, 'vname': 1,
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in AE33 lev 0, maybe lev2 later and add
                    # to DB and have controlled vocabulary?
                    'parser': self.parse_filter_type,
                },
                {
                    'key': 'sample_prep',
                    'tag': 'Sample preparation',
                    'nc_tag': 'sample_preparation',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_sample_prep,
                },
                {
                    'key': 'blank_corr',
                    'tag': 'Blank correction',
                    'nc_tag': 'blank_correction',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_blank_corr,
                    'printer': self.print_blank_corr
                },
                {
                    'key': 'artifact_corr',
                    'tag': 'Artifact correction',
                    'nc_tag': 'artifact_correction',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_artifact_corr,
                },
                {
                    'key': 'artifact_corr_desc',
                    'tag': 'Artifact correction description',
                    'nc_tag': 'artifact_correction_description',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'charring_corr',
                    'tag': 'Charring correction',
                    'nc_tag': 'charring_correction',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_charring_corr,
                },
                {
                    'key': 'ozone_corr',
                    'tag': 'Ozone correction',
                    'nc_tag': 'ozone_correction',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_ozone_corr,
                },
                {
                    'key': 'watervapor_corr',
                    'tag': 'Water vapor correction',
                    'nc_tag': 'water_vapor_correction',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_watervapor_corr,
                },
                {
                    'key': 'zero_span_type',
                    'tag': 'Zero/span check type',
                    'nc_tag': 'zero_span_check_type',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_zero_span_type,
                },
                {
                    'key': 'zero_span_interval',
                    'tag': 'Zero/span check interval',
                    'nc_tag': 'zero_span_check_interval',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_period_rescode,
                },
                {
                    'key': 'hum_temp_ctrl',
                    'tag': 'Humidity/temperature control',
                    'nc_tag': 'humidity_temperaure_control',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_ht_control
                },
                {
                    'key': 'hum_temp_ctrl_desc',
                    'tag': 'Humidity/temperature control description',
                    'nc_tag': 'humidity_temperaure_control_description',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'vol_std_temp',
                    'tag': 'Volume std. temperature',
                    'nc_tag': 'volume_std_temperature',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_vol_std_temp,
                    'printer': self.print_vol_std_temp
                },
                {
                    'key': 'vol_std_pressure',
                    'tag': 'Volume std. pressure',
                    'nc_tag': 'volume_std_pressure',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_vol_std_press,
                    'printer': self.print_vol_std_press
                },
                {
                    'key': 'detection_limit',
                    'tag': 'Detection limit',
                    'nc_tag': 'detection_limit',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_float_unit,
                    'printer': self.print_float_unit
                },
                {
                    'key': 'detection_limit_desc',
                    'tag': 'Detection limit expl.',
                    'nc_tag': 'detection_limit_expl',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'upper_range_limit',
                    'tag': 'Upper range limit',
                    'nc_tag': 'upper_range_limit',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_float_unit,
                    'printer': self.print_float_unit
                },
                {
                    'key': 'uncertainty',
                    'tag': 'Measurement uncertainty',
                    'nc_tag': 'measurement_uncertainty',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_float_unit,
                    'printer': self.print_float_unit
                },
                {
                    'key': 'uncertainty_desc',
                    'tag': 'Measurement uncertainty expl.',
                    'nc_tag': 'measurement_uncertainty_expl',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'zero_negative',
                    'tag': 'Zero/negative values code',
                    'nc_tag': 'zero_negative_values_code',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_zero_negative
                },
                {
                    'key': 'zero_negative_desc',
                    'tag': 'Zero/negative values',
                    'nc_tag': 'zero_negative_values',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'abs_cross_section',
                    'tag': 'Absorption cross section',
                    'nc_tag': 'absorption_cross_section',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_absorption_crossection,
                },
                {
                    'key': 'mass_abs_cross_section',
                    'tag': 'Mass absorption cross section',
                    'nc_tag': 'mass_absorption_cross_section',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(unit_='m2/g'),
                    'printer': self.print_generic_factory(unit_='m2/g'),
                    Condition('data_level'): IsIn(['0']),
                    # only used in filter_absorption_photometer lev 0 (AE33,
                    # maap)
                },
                {
                    'key': 'multi_scattering_corr_fact',
                    'tag': 'Multi-scattering correction factor',
                    'nc_tag': 'multi_scattering_correction_factor',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(type_=float),
                    Condition('data_level'): IsIn(['0']),
                    # only used in AE33 lev 0
                },
                {
                    'key': 'max_attenuation',
                    'tag': 'Maximum attenuation',
                    'nc_tag': 'maximum_attenuation',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        type_=float, range_=[10, 200]),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in AE33 lev 0, maybe lev2 later and add
                    # to DB and have some syntax rules?
                },
                {
                    'key': 'leakage_factor_zeta',
                    'tag': 'Leakage factor zeta',
                    'nc_tag': 'leakage_factor_zeta',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        type_=float, range_=[0.01, 0.2]),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in AE33 lev 0, maybe lev2 later and add
                    # to DB and have some syntax rules?
                },
                {
                    'key': 'comp_thresh_atten1',
                    'tag': 'Compensation threshold attenuation 1',
                    'nc_tag': 'compensation_threshold_attenuation_1',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        type_=float, range_=[1, 50]),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in AE33 lev 0, maybe lev2 later and add
                    # to DB and have some syntax rules?
                },
                {
                    'key': 'comp_thresh_atten2',
                    'tag': 'Compensation threshold attenuation 2',
                    'nc_tag': 'compensation_threshold_attenuation_2',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        type_=float, range_=[1, 50]),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in AE33 lev 0, maybe lev2 later and add
                    # to DB and have some syntax rules?
                },
                {
                    'key': 'comp_param_kmin',
                    'tag': 'Compensation parameter k min',
                    'nc_tag': 'compensation_parameter_k_min',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        type_=float, range_=[-0.05, 0.05]),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in AE33 lev 0, maybe lev2 later and add
                    # to DB and have some syntax rules?
                },
                {
                    'key': 'comp_param_kmax',
                    'tag': 'Compensation parameter k max',
                    'nc_tag': 'compensation_parameter_k_max',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        type_=float, range_=[-0.05, 0.05]),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in AE33 lev 0, maybe lev2 later and add
                    # to DB and have some syntax rules?
                },
                {
                    'key': 'coincidence_corr',
                    'tag': 'Coincidence correction',
                    'nc_tag': 'coincidence_correction',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        allowed=['Corrected', 'Not corrected']),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in CPC lev 0
                },
                {
                    'key': 'charge_type',
                    'tag': 'Charge type',
                    'nc_tag': 'charge_type',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        allowed=['Radioactive-pos', 'Radioactive-neg',
                                 'Xray-pos', 'Xray-neg']),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in MPSS lev 0
                },
                {
                    'key': 'inlet_diffusion_loss_data',
                    'tag': 'Inlet diffusion loss data',
                    'nc_tag': 'inlet_diffusion_loss_data',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_inlet_diffusion_loss_data,
                    'printer': self.print_inlet_diffusion_loss_data,
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in MPSS lev 0
                },
                {
                    'key': 'cpc_default_pulse_width',
                    'tag': 'CPC default pulse width',
                    'nc_tag': 'cpc_default_pulse_width',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        unit_='us', range_=[0.0, 200.0]),
                    'printer': self.print_generic_factory(unit_='us'),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in MPSS lev 0
                },
                {
                    'key': 'normalized_ion_mobility',
                    'tag': 'Normalized ion mobility',
                    'nc_tag': 'normalized_ion_mobility',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        unit_='cm2/V/s', range_=[0.0, 20.0]),
                    'printer': self.print_generic_factory(unit_='cm2/V/s'),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in PTR-MS lev 0
                },
                {
                    'key': 'number_density_of_air',
                    'tag': 'Number density of air',
                    'nc_tag': 'number_density_of_air',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        unit_='1/cm3', range_=[1.0E16, 1.0E26]),
                    'printer': self.print_generic_factory(unit_='1/cm3'),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in PTR-MS lev 0
                },
                {
                    'key': 'normalized_pressure',
                    'tag': 'Normalized pressure',
                    'nc_tag': 'normalized_pressure',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        unit_='hPa', range_=[0.0, 1200.0]),
                    'printer': self.print_generic_factory(unit_='hPa'),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in PTR-MS lev 0
                },
                {
                    'key': 'normalized_count_rate',
                    'tag': 'Normalized count rate',
                    'nc_tag': 'normalized_count_rate',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        unit_='1/s', range_=[1.0, 1.0E8]),
                    'printer': self.print_generic_factory(unit_='1/s'),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in PTR-MS lev 0
                },
                {
                    'key': 'drift_tube_length',
                    'tag': 'Drift tube length',
                    'nc_tag': 'drift_tube_length',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_generic_factory(
                        unit_='cm', range_=[1.0, 1.0E8]),
                    'printer': self.print_generic_factory(unit_='cm'),
                    Condition('data_level'): IsIn(['0']),
                    # temp: only used in PTR-MS lev 0
                },
                {
                    'QA_block': True,
                    'key': 'qm_id',
                    'tag': 'QA measure ID',
                    'nc_tag': 'qa_measure_id',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_qa_measure_id,
                },
                {
                    'QA_block': True,
                    'key': 'qm_desc',
                    'tag': 'QA measure description',
                    'nc_tag': 'qa_measure_description',
                    'main': 1, 'vname': 1,
                },
                {
                    'QA_block': True,
                    'key': 'qa_date',
                    'tag': 'QA date',
                    'nc_tag': 'qa_date',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_datetime_arbitrary,
                    'printer': self.print_datetime_arbitrary,
                },
                {
                    'QA_block': True,
                    'key': 'qa_outcome',
                    'tag': 'QA outcome',
                    'nc_tag': 'qa_outcome',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_qa_outcome,
                    'printer': self.print_qa_outcome,
                },
                {
                    'QA_block': True,
                    'key': 'qa_bias',
                    'tag': 'QA bias',
                    'nc_tag': 'qa_bias',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_float_unit,
                    'printer': self.print_float_unit
                },
                {
                    'QA_block': True,
                    'key': 'qa_variability',
                    'tag': 'QA variability',
                    'nc_tag': 'qa_variability',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_float_unit,
                    'printer': self.print_float_unit
                },
                {
                    'QA_block': True,
                    'key': 'qa_doc_name',
                    'tag': 'QA document name',
                    'nc_tag': 'qa_document_name',
                    'main': 1, 'vname': 1,
                },
                {
                    'QA_block': True,
                    'key': 'qa_doc_date',
                    'tag': 'QA document date',
                    'nc_tag': 'qa_document_date',
                    'main': 1, 'vname': 1,
                    'printer': self.print_datetime_arbitrary,
                    'parser': self.parse_datetime_arbitrary,
                },
                {
                    'QA_block': True,
                    'key': 'qa_doc_url',
                    'tag': 'QA document URL',
                    'nc_tag': 'qa_document_url',
                    'main': 1, 'vname': 1,
                    'parser': self.parse_url,
                },
                {
                    'key': 'org',
                    'tag': 'Organization',
                    'nc_tag': 'organization',
                    Merge('data_format'): {
                        Default: {'main': 1, 'vname': 1},
                        # org is ONAME in Nasa Ames, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {'main': 0, 'vname': 0}},
                    'printer': self.print_org,
                },
                {
                    'key': 'projects',
                    'tag': 'Framework acronym',
                    'nc_tag': 'framework_acronym',
                    Merge('data_format'): {
                        Default: {
                            'main': 1,
                            'vname': 1,
                            'printer': lambda value: ', '.join(value)
                            },
                        # frameworks are MNAME in Nasa Ames, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {
                            'main': 0,
                            'vname': 0,
                        }
                    },
                },
                {
                    'key': 'project_names',
                    'tag': 'Framework name',
                    'nc_tag': 'framework_name',
                    Merge('data_format'): {
                        Default: {
                            'main': 1,
                            'vname': 1,
                            'printer': lambda value: ', '.join(value)
                            },
                        # frameworks are MNAME in Nasa Ames, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {
                            'main': 0,
                            'vname': 0,
                        }
                    },
                },
                {
                    'key': 'project_descs',
                    'tag': 'Framework description',
                    'nc_tag': 'framework_description',
                    Merge('data_format'): {
                        Default: {
                            'main': 1,
                            'vname': 1,
                            'printer': lambda value: ', '.join(value)
                            },
                        # frameworks are MNAME in Nasa Ames, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {
                            'main': 0,
                            'vname': 0,
                        }
                    },
                },
                {
                    'key': 'project_cotact_names',
                    'tag': 'Framework contact name',
                    'nc_tag': 'framework_contact_name',
                    Merge('data_format'): {
                        Default: {
                            'main': 1,
                            'vname': 1,
                            'printer': lambda value: ', '.join(value)
                            },
                        # frameworks are MNAME in Nasa Ames, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {
                            'main': 0,
                            'vname': 0,
                        }
                    },
                },
                {
                    'key': 'project_contact_emails',
                    'tag': 'Framework contact email',
                    'nc_tag': 'framework_contact_email',
                    Merge('data_format'): {
                        Default: {
                            'main': 1,
                            'vname': 1,
                            'printer': lambda value : ', '.join(value)
                            },
                        # frameworks are MNAME in Nasa Ames, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {
                            'main': 0,
                            'vname': 0,
                        }
                    },
                },
                {
                    # !!! _parse_person and print_person are special cases.
                    # They need non-default parameters!!!
                    'key': 'originator',
                    'tag': 'Originator',
                    'nc_tag': 'originator',
                    Merge('data_format'): {
                        Default: {'main': 1,'vname': 1},
                        # DO is file global in Nasa Ames, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {'main': 2, 'vname': 0}},
                    'parser': self.parse_person, 'printer': self.print_person
                },
                {
                    # !!! _parse_person and _print_person are special cases.
                    # They need non-default parameters!!!
                    'key': 'submitter',
                    'tag': 'Submitter',
                    'nc_tag': 'submitter',
                    Merge('data_format'): {
                        Default: {'main': 1,'vname': 1},
                        # DS is file global in Nasa Ames, no keyword allowed
                        EBAS_IOFORMAT_NASA_AMES: {'main': 2, 'vname': 0}},
                    'parser': self.parse_person, 'printer': self.print_person
                },
                {
                    'key': 'acknowledgements',
                    'tag': 'Acknowledgement',
                    'nc_tag': 'acknowledgement',
                    'main': 1, 'vname': 1,
                },
                {
                    'key': 'comment',
                    'tag': 'Comment',
                    'nc_tag': 'comment',
                    'main': 1, 'vname': 1,
                }
            ]})
        stb = StructureBuilder({'data_version': data_version,
                                'data_format': data_format,
                                'data_level': data_level,
                                'metadata_options': metadata_options})
        self.metadata = stb.build(ebasmetadata)
        self.metadata_tags = {}
        self.metadata_keys = {}
        i = 0
        for meta in self.metadata:
            # set default parser and printer:
            if 'parser' not in meta:
                meta['parser'] = self.parse_generic_factory()
            if 'printer' not in meta:
                meta['printer'] = self.print_generic_factory()

            self.metadata_tags[meta['tag']] = meta
            if not 'renamed_tag' in meta:
                self.metadata_keys[meta['key']] = meta
            meta['sortorder'] = i
            i += 1
            # do not allow certain combinations:
            # parser is not compatible with unit, type and range

    def metadata_value(self, nas, key, var_index=None, qa_number=None,
                       explicit_only=True):
        """
        Returns the value for a specific metadata attibute for a specific
        variable (or file main metadata if var_index==None).
        Parameters:
            nas         nasa ames object
            key         name of the metadata attibute (key in nasa ames
                        metadata dict)
            var_index   variable number in nasa ames object
            qa_number   optional, only for QA metadata: number of QA block
            explicit_only
                        (applies to var_index!=None only)
                        Only return a valid value if the respective variable has
                        the metadata element set explicitly (or the element is
                        mandatory per variable)
        Returns:
            value    metadata value as stored in the metadata structure
        Raises:
            EbasMetadataNone   the attribute should not occur for one variable
            EbasMetadataEmpty  the attribute should be empty for one variable
        """
        meta_def = self.metadata_keys[key]
        if ('QA_block' in meta_def and qa_number is None) or \
           ('QA_block' not in meta_def and qa_number is not None):
            raise RuntimeError("matadata_value: qa metadata number error")
        if qa_number:
            qa_ = nas.get_qa_by_number(qa_number, None)
            mvalue = qa_[key] if qa_ is not None and key in qa_ else None
            if var_index is None:
                occurrence = 'main'
                vvalue = None
            else:
                occurrence = 'vname'
                qa_ = nas.get_qa_by_number(qa_number, var_index)
                if qa_ is None or key not in qa_:
                    vvalue = EbasMetadataNone
                else:
                    vvalue = qa_[key]
        else:
            mvalue = nas.metadata[key]
            if var_index is None:
                occurrence = 'main'
                vvalue = None
            else:
                occurrence = 'vname'
                if key not in nas.variables[var_index].metadata:
                    vvalue = EbasMetadataNone
                else:
                    vvalue = nas.variables[var_index].metadata[key]

        # now we have occurrence, mvalue and vvalue ready, decide
        # what to use as the correct return value:

        if meta_def[occurrence] == 0:
            # not allowed here
            raise EbasMetadataNone()

        if occurrence == 'vname' and explicit_only == False:
            # return a value, maybe fall back to main value
            if occurrence == 'vname' and vvalue is not EbasMetadataNone:
                if vvalue is None:
                    raise EbasMetadataEmpty()
                return vvalue
            if mvalue is None:
                raise EbasMetadataEmpty()
            return mvalue

        if not meta_def[occurrence] & 2 and \
           ((occurrence == 'main' and mvalue is None) or \
            (occurrence == 'vname' and vvalue is EbasMetadataNone)):
            # not mandatory and value is empty
            raise EbasMetadataNone()
        if meta_def[occurrence] & 2 and \
           (occurrence == 'main' and mvalue is None) or \
           (occurrence == 'vname' and vvalue is None) or \
           (occurrence == 'vname' and vvalue is EbasMetadataNone and \
                                      mvalue is None):
            # mandatory but empty
            raise EbasMetadataEmpty()
        if meta_def[occurrence] & 2 and \
            occurrence == 'vname' and vvalue is EbasMetadataNone:
            # mandatory, but missing for variable: use main metadata
            return mvalue
        if occurrence == 'main':
            return mvalue
        return vvalue

    def metadata_value_str(self, nas, key, var_index=None, qa_number=None,
                           explicit_only=True):
        """
        Creates an output string for a specific metadata attibute for a specific
        variable (or file main metadata if var_index==None).
        Parameters:
            nas         nasa ames object
            key         name of the metadata attibute (key in nasa ames
                        metadata dict)
            var_index   variable number in nasa ames object
            qa_number   optional, only for QA metadata: number of QA block
            explicit_only
                        (applies to var_index!=None only)
                        Only return a valid value if the respective variable has
                        the metadata element set explicitly (or the element is
                        mandatory per variable)

        Returns:
            generator:
                str    metadata value as string, ready to be printed (may also
                       be an empty string if the attribute is set to empty for
                       one variable)
            generator, because there are cases where multiple values can be
            returned (submitter, originator, input_dataset, software) and cases
            where no value should be printed (not allowed or not mandatory and
            empty).
        """
        meta_def = self.metadata_keys[key]
        try:
            value = self.metadata_value(nas, key, var_index=var_index,
                                        qa_number=qa_number,
                                        explicit_only=explicit_only)
        except EbasMetadataNone:
            return
        except EbasMetadataEmpty:
            yield ''
            return

        if key in ('originator', 'submitter', 'input_dataset', 'software'):
            # special case: those are lists
            for val in meta_def['printer'](value):
                yield val
        else:
            # all elements have a printer
            yield meta_def['printer'](value)

    def metadata_list_tag_valuestr(self, nas, var_index=None,
                                   explicit_only=True, nc_tags=False):
        """
        Creates (tag, value_string) pairs of metadata elements for a specific
        variable (or file main metadata if var_nindex==None).
        Parameters:
            nas         nasa ames object
            var_index   variable number in nasa ames object
                        Use file global metadata if var_index==None
            flags         flag column options: FLAGS_ONE_OR_ALL (default),
                          FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE
            explicit_only
                        (applies to var_index!=None only)
                        Only return a valid value if the respective variable has
                        the metadata element set explicitly (or the element is
                        mandatory per variable)
            nc_tags      use NetCDF attribute style tags instead of classic Nasa
                        Ames tags
        Returns:
            generator: (tag, value_str, mata_def)
        """
        tagtype = 'nc_tag' if nc_tags else 'tag'
        tagreplace = ('qa_', 'qa{}_') if nc_tags else ('QA ', 'QA{} ')

        # Special dict for yielding QA metadata in the coreect order.
        # They are not yielded instantly, but collected in qa_.
        # QA metadata shoulkd be yielded in this order:
        #    First all QA1 metadatam, then all QA2, ...
        # The QA elements will come consecutively from the loop through
        # self.metadata, and will be yielded at once, when the next non-QA
        # element appears.
        qa_ = defaultdict(list)

        for meta_def in self.metadata:
            # always iterate through METADATA: this gives a defined output order
            if 'renamed_tag' in meta_def and meta_def['renamed_tag']:
                continue
            if 'QA_block' in meta_def:
                # Do not yield QA metadata instantly. Collect them in qa_
                # See comment above.
                for qanum in nas.get_qa_numbers():
                    tag = meta_def[tagtype].replace(*tagreplace).format(
                        1 if qanum == -1 else qanum)
                        # -1 is the qa index used for QA xxx without number
                        # when read from an input file.
                        # (Can only occur when reading form file)
                        # We do not want to write out QA-1, rather change to QA1
                        # ebas_convert will typically face this issue.
                        # Same in method metadata_list_tag_value
                    for res in self.metadata_value_str(nas, meta_def['key'],
                                                       var_index, qanum):
                        qa_[qanum].append((tag, res, meta_def))
            else:
                # not QA metadata
                if qa_:
                    # Now it's time to yield blocks of QA metadata in the
                    # correct order if they appeared before :
                    for qanum in nas.get_qa_numbers():
                        for elem in qa_[qanum]:
                            yield elem
                    qa_ = defaultdict(list)
                # yield non-QA metadata:
                for res in self.metadata_value_str(nas, meta_def['key'],
                                                   var_index,
                                                   explicit_only=explicit_only):
                    yield(meta_def[tagtype], res, meta_def)

    def metadata_list_tag_value(self, nas, var_index, nc_tags=False):
        """
        Creates (tag, value) pairs of metadata elements for a specific
        variable (or file main metadata if var_nindex==None).
        Parameters:
            nas         nasa ames object
            var_index   variable number in nasa ames object
                        Use file global metadata if var_index==None
            flags         flag column options: FLAGS_ONE_OR_ALL (default),
                          FLAGS_COMPRESS, FLAGS_ALL, FLAGS_NONE
            nc_tags     use NetCDF attribute style tags instead of classic Nasa
                        Ames tags
        Returns:
            generator: (tag, value, mata_def)

        Difference to metadata_list_tag_valuestr:
            - yield value (not string representation thereof), thus the values
              can be sorted natively, not string wise
              (e.g. size bin 20.0 < 150.0)
        """
        tagtype = 'nc_tag' if nc_tags else 'tag'
        tagreplace = ('qa_', 'qa{}_') if nc_tags else ('QA ', 'QA{} ')

        # Special dict for yielding QA metadata in the coreect order.
        # They are not yielded instantly, but collected in qa_.
        # QA metadata shoulkd be yielded in this order:
        #    First all QA1 metadatam, then all QA2, ...
        # The QA elements will come consecutively from the loop through
        # self.metadata, and will be yielded at once, when the next non-QA
        # element appears.
        qa_ = defaultdict(list)

        for meta_def in self.metadata:
            # always iterate through METADATA: this gives a defined output order
            if 'renamed_tag' in meta_def and meta_def['renamed_tag']:
                continue
            if 'QA_block' in meta_def:
                # Do not yield QA metadata instantly. Collect them in qa_
                # See comment above.
                for qanum in nas.get_qa_numbers():
                    tag = meta_def[tagtype].replace(*tagreplace).format(
                        1 if qanum == -1 else qanum)
                        # -1 is the qa index used for QA xxx without number
                        # when read from an input file.
                        # (Can only occur when reading form file)
                        # We do not want to write out QA-1, rather change to QA1
                        # ebas_convert will typically face this issue.
                        # Same in method metadata_list_tag_value
                    try:
                        qa_[qanum].append(
                            (tag, self.metadata_value(nas, meta_def['key'],
                                                      var_index, qanum),
                             meta_def))
                    except EbasMetadataNone:
                        pass
                    except EbasMetadataEmpty:
                        qa_[qanum].append(
                            (tag, None, meta_def))
            else:
                # not QA metadata
                if qa_:
                    # Now it's time to yield blocks of QA metadata in the
                    # correct order if they appeared before :
                    for qanum in nas.get_qa_numbers():
                        for elem in qa_[qanum]:
                            yield elem
                    qa_ = defaultdict(list)
                # yield non-QA metadata:
                try:
                    yield (meta_def[tagtype],
                           self.metadata_value(nas, meta_def['key'], var_index),
                           meta_def)
                except EbasMetadataNone:
                    pass
                except EbasMetadataEmpty:
                    yield (meta_def[tagtype], None, meta_def)


class DatasetCharacteristic(DataObject, DCBase):
    """
    DatasetCharacteristic class for ebas.io.
    """
    def __lt__(self, other):
        """
        Force inheritence from DCBase...
        """
        return DCBase.__lt__(self, other)

class DatasetCharacteristicList(list, DCListBase):
    """
    DatasetCharacteristic list class for ebas.io.
    """
    CLIENT_CLASS_ELEMENTS = DatasetCharacteristic

