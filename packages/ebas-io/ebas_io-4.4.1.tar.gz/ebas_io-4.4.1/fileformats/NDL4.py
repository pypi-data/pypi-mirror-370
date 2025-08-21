"""
File IO for ASCII datafiles in fixed witdh format.
"""

from nilutility.datatypes import DataObject
import datetime
import logging

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


class FormatError(Exception):
    """
    File format error, raised during read.
    """
    pass


class NDL4(object):
    # pylint: disable=R0902
    # R0902: Too many instance attributes
    """
    File IO for NDL4 datafile format.

    Synopsis:

    General: setup object:
        ndl4 = NDL4()
        ndl4.add_column("varname1", int)
        ndl4.add_column("varname2")  # default is float
        try:
            ndl4.read("filename")
        except IOError as excpt:
            # handle this
            pass
        except FormatError as excpt:
            # handle that
            pass

    2 ways of usage/data access:

    1) access variables as lists:
        ndl4.start[0]  # first start time in file (as datetime.ddatetime)
        ndl4.start[-1]  # last end time in file (as datetime.ddatetime)
        ndl4.coverage  # data coverage list (last column)

        ndl4.varname1  # variable access as attibute (list)
        ndl4.data[0]   # same variable (list)

    2) access by starttime/end time
        # get the value for variable "varname1" for the sample time
        # 2018-01-01 12:36:00 - 2018-01-01 12:37:00
        ndl4.get("varname1",
                 datetime.datetime(2018, 1, 1, 12, 36, 0),
                 datetime.datetime(2018, 1, 1, 12, 37, 0))
    """

    def __init__(self):
        """
        Set up IO object.

        Parameters:
            None
        Returns:
            None
        Raises:
            None
        """
        self.logger = logging.getLogger('NDL4')
        self.format_desc = DataObject(columns=[])
        self.start = []
        self.end = []
        self.data = []
        self.coverage = []
        self.filename = None
        # faster access for sequential reads: remember last time and index
        self.recent_start = None  # last acccessed start time
        self.recent_index = None  # last acccessed index

    def add_column(self, name, datatype=float):
        """
        Adds a column to the format description.

        Parameters:
            pos_start   start position in file
            length      length of the column
            datatype    datatype to be used for the column
        """
        self.format_desc.columns.append(
            DataObject(name=name, datatype=datatype))
        self.data.append([])

    def __getattr__(self, name):
        """
        Attribute like access for variables: wrapper for var_by_name.
        Parameters:
            name   attribute name
        Returns:
            variable by name
        """
        try:
            return self.var_by_name(name)
        except ValueError:
            raise AttributeError("no column named '{}'".format(name))

    def var_by_name(self, name):
        """
        Get a variable by it's name.
        Parameters:
            name   variabble name
        Returns:
            variable by name
        """
        ind = [x.name for x in self.format_desc.columns].index(name)
        return self.data[ind]

    def read(self, filename):
        """
        Reads a file according to the data format description.

        Parameters:
            filename     file path and name

        Returns:
            None
        Raises:
            FormatError
        """
        self.filename = filename
        fil = open(self.filename)
        linenum = -1
        timeparser = DatetimeParserFactory('%Y.%m.%d %H:%M:%S')
        for line in fil:
            linenum += 1
            if len(line) < 39:
                raise FormatError('line {}: syntax error, too short line',
                                  linenum)
            # prosess start/end time
            try:
                self.start.append(timeparser(line[0:19]))
            except ValueError as excpt:
                raise FormatError('line {}, start time: {}', linenum,
                                  excpt.message)
            try:
                self.end.append(timeparser(line[20:39]))
            except ValueError as excpt:
                raise FormatError('line {}, end time: {}', linenum,
                                  excpt.message)
            # prosess data
            data = line[39:].split()
            if len(self.format_desc.columns)+3 != len(data)+2:
                raise FormatError(
                    'line {}: Data format specifies {} columns, {} found'
                    .format(linenum, len(self.format_desc.columns)+3,
                            len(data)+2))
            for var_index in range(len(self.format_desc.columns)):
                val = data[var_index]
                if val == "-9900":
                    val = None
                else:
                    val = self.format_desc.columns[var_index].datatype(val)
                self.data[var_index].append(val)
            var_index = len(self.format_desc.columns)  # last column is coverage
            self.coverage.append(int(data[var_index]))

    def get(self, name, start, end):
        """
        Get a data value by variable name and sample start/end times.
        Prameters:
            name    variable name
            start   sample start time of requested sample
            end     sample end time of requested sample
        Returns:
            One value for one variable at one sample interval.
            When the satrt/end time does not exists in the file, None is
            returned
        """
        ind = None
        if self.recent_start and self.recent_start == start:
            ind = self.recent_index
        else:
            startind = 0
            stopind = len(self.start)
            if self.recent_start and self.recent_start < start:
                startind = self.recent_index
            for i in range(startind, stopind):
                if self.start[i] == start:
                    ind = i
                    break
        if ind is not None and self.start[ind] == start and \
           self.end[ind] == end:
            if ind != self.recent_index:
                self.recent_start = start
                self.recent_index = ind
            return self.var_by_name(name)[ind]
        elif ind is None:
            errtxt = "Input file '{}': start {}, end {} not found".format(
                self.filename, start, end)
            self.logger.warning(errtxt)
            return None
        else:
            errtxt = ("Input file '{}', line {}: start {}, end {} does not "
                      "match requested start {}, end {}").format(
                          self.filename, ind+1, self.start[ind], self.end[ind],
                          start, end)
            self.logger.warning(errtxt)
            return None
