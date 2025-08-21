"""
File IO for ASCII datafiles in fixed witdh format.
"""

from nilutility.datatypes import DataObject
import datetime
from six import PY2

class DatetimeParserFactory(object):  # pylint: disable=R0903
    # R0903:Too few public methods
    """
    Factory class for datetime.datetime, constructed by parsing a string.
    """
    def __init__(self, formatstring):
        """
        Set up datetime_parser_factory.
        Parameters:
            None
        Returns:
            None
        """
        self.formatstring = formatstring

    def __call__(self, datetimestr):
        """
        Actually create the object: a datatime.datetime that is parsed from a
        string.
        Parameters:
            datetimestring     string containing the datetime value according to
                               the format string self.formatstr
        Returns:
            datetime.datetime object
        """
        return datetime.datetime.strptime(datetimestr, self.formatstring)

class AsciiFixedwidth(object):
    """
    File IO for ASCII datafiles in fixed witdh format.
    """

    def __init__(self, header=False):
        """
        Set up IO object.

        Parameters:
            None
        Returns:
            None
        Raises:
            None
        """
        self.format_desc = DataObject(header=header, columns=[])
        self.data = []
        self.header = []

    def add_column(self, pos_start, length, datatype=None):
        """
        Adds a column to the format description.

        Parameters:
            pos_start   start position in file
            length      length of the column
            datatype    datatype to be used for the column
        """
        if PY2:
            datatype = unicode
        else:
            datatype = str
        self.format_desc.columns.append(
            DataObject(pos_start=pos_start, length=length,
                       datatype=datatype, header=None))
        self.data.append([])
        self.header.append(None)

    def read(self, filename):
        """
        Reads a file according to the data format description.

        Parameters:
            filename     file path and name

        Returns:
            None
        """
        fil = open(filename)
        linenum = -1
        for line in fil:
            linenum += 1
            if self.format_desc.header and linenum == 0:
                # prosess header
                for col in self.format_desc.columns:
                    col.header = line[col.pos_start:col.pos_start+col.length]\
                                     .strip()
            else:
                # prosess data
                var_index = 0
                for col in self.format_desc.columns:
                    self.data[var_index].append(col.datatype(
                        line[col.pos_start:col.pos_start+col.length].strip()))
                    var_index += 1

