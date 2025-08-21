"""
$Id: export_filter.py 2561 2020-12-07 23:09:30Z pe $

Parser for export filter

This parser is needed with and without the domain layer (e.g. ebas-io package)
Thus is's placed in the basic domain logic.

"""

import re
import argparse


# Export filter options (filter data from DB to domain) - bitfield
# Default (0):
#     Filter flag 900 for non instrument owners.
#     Filter all data flagged with any invalid flag.

# Include data with  flag 900, also for non-instrument owners
# (only for data curation! Not for data users!)
EXPORT_FILTER_INCLUDE_900 = 1

# Include data flagged with invalid flags.
# (mainly for data curation, maybe for expert users (this is like lev0))
EXPORT_FILTER_INCLUDE_INVALID = 2


class ParseExportFilter(object):
    # pylint: disable=R0903
    # R0903: Too few public methods
    #  --> this is a function factory implememnted as a class, no need for more
    #      public methods
    """Factory for creating a parser object for the --export-filter argument

    User for the argument parser in ebas_extract, in ebasmetadata for parsing
    the 'Extract state' metadata element.
    """

    def __init__(self, default=0):
        self.value = default
        self.set_900 = False
        self.set_invalid = False

    def __call__(self, string):
        return self.parse(string)

    def parse(self, string):
        """
        Parser for the --export-filter argument.

        The string value is parsed, and the applicable value (int) is returned.

        Parameters:
           string   string to be parsed (from commandline or from file metadata)
        Returns:
           int (a bitfield consisting of EXPORT_FILTER_INCLUDE_900 and/or
           EXPORT_FILTER_INCLUDE_INVALID)
        Raises:
            argparse.ArgumentTypeError in case of argument errors
        """
        self.set_900 = False
        self.set_invalid = False
        if re.search(",", string):
            hstr = string
            rex = re.search("^([^,]*),", hstr)
            while rex:
                self._update_value(rex.group(1))
                hstr = re.sub("^([^,]+),?", "", hstr)
                rex = re.search("^([^,]+),?", hstr)
            return self.value
        self._update_value(string)
        return self.value

    def _update_value(self, string):
        """
        Update self.value according to the string representation.
        """
        if string in ('include-900', 'exclude-900') and self.set_900:
            raise argparse.ArgumentTypeError(
                "include/exclude-900 appears more then once")
        if string in ('include-invalid', 'exclude-invalid') and \
                self.set_invalid:
            raise argparse.ArgumentTypeError(
                "include/exclude-invalid appears more then once")
        if string == 'include-900':
            self.value |= EXPORT_FILTER_INCLUDE_900
            self.set_900 = True
        elif string == 'exclude-900':
            self.value &= ~EXPORT_FILTER_INCLUDE_900
            self.set_900 = True
        elif string == 'include-invalid':
            self.value |= EXPORT_FILTER_INCLUDE_INVALID
            self.set_invalid = True
        elif string == 'exclude-invalid':
            self.value &= ~EXPORT_FILTER_INCLUDE_INVALID
            self.set_invalid = True
        else:
            raise argparse.ArgumentTypeError(
                "invalid option: '{}'; "
                "only allowed: include-900, exclude-900, "
                "include-invalid, exclude-invalid".format(string))

    def __repr__(self):
        return '{}({}, {})'.format(
            self.__class__.__name__,
            "include-900" if self.value & EXPORT_FILTER_INCLUDE_900
            else "exclude-900",
            "include-invalid" if self.value & EXPORT_FILTER_INCLUDE_INVALID
            else "exclude-invalid")

    def __str__(self):
        return '{},{}'.format(
            "include-900" if self.value & EXPORT_FILTER_INCLUDE_900
            else "exclude-900",
            "include-invalid" if self.value & EXPORT_FILTER_INCLUDE_INVALID
            else "exclude-invalid")
