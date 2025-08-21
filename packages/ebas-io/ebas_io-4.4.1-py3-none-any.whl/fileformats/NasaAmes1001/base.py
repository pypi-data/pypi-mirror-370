"""
/NasaAmes1001/nasa_ames.py
$Id: base.py 2582 2020-12-09 19:23:48Z pe $

Base class for NASA Ames 1001.

History:
V.1.0.0  2013-03-05  pe  initial version

"""
import logging
from nilutility.float_helper import float_almostequal
from nilutility.datatypes import DataObject

class NasaAmes1001Error(Exception):
    """
    Error class for NasaAmes 1001.
    """
    pass

class NasaAmes1001Base(object):
    # pylint: disable=R0902
    # R0902: Too many instance attributes
    """
    Partial class NasaAmes1001: Base class used by Parts.
    """
    # all data attibutes (set on read, getattr implemented)
    DATA_ATTRIBS = [
        'NLHEAD',   # int, nuber of header lines
        'ONAME',    # str, free text for 1001
        'ORG',      # str, free text for 1001
        'SNAME',    # str, free text for 1001
        'MNAME',    # str, free text for 1001
        'IVOL',     # int
        'NVOL',     # int
        'DATE',     # datetime.datetime object
        'RDATE',    # datetime.datetime object
        'DX',       # float
        'XNAME',    # str, free text for 1001
        'NV',       # int, number of dependent variables in file
        'VSCAL',    # list of float, len=NV, scaling factors for data
        'VMISS',    # list of str, len=NV, missing values used for data
        'VFORMAT',  # list of str, len=NV, format str. (gen. from VMISS)
        'VREPR',    # list of type, internal representation (datatype)
        'VNAME',    # str, free text for 1001
        'SCOML',    # list of str, free texts
        'NCOML',    # list of str, free texts for 1001
        'DATA',     # list of lists of float/Decimal
        ]

    # attributes that can be set (before write), others will be calculated
    SETABLE_DATA_ATTRIBS = ['ONAME', 'ORG', 'SNAME', 'MNAME', 'IVOL', 'NVOL',
                            'DATE', 'RDATE', 'XNAME', 'VSCAL', 'VNAME', 'SCOML',
                            'NCOML', 'DATA']
    # read/write states
    SECTIONS = ['NLHEAD', 'ONAME', 'ORG', 'SNAME', 'MNAME', 'IVOL_NVOL',
                'DATE_RDATE', 'DX', 'XNAME', 'NV', 'VSCAL', 'VMISS', 'VNAME',
                'SCOML', 'NCOML', 'DATA']

    # for bitfield strictness:
    # strictly require data in format given by VMISS
    STRICT_NUMFORMAT = 1
    STRICT_DX = 2
    # strictly require irregular data when DX=0 (DX!=0 will always raise an
    # error if not obeyed in data)

    def __setattr__(self, name, value):
        if name in self.__class__.SETABLE_DATA_ATTRIBS:
            self.data[name] = value
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError as expt:
            raise AttributeError(expt)

    def __init__(self, strictness=0):
        """
        Paramaters:
            strictness   bit field for strictness on read
                         (STRICT_NUMFORMAT, STRICT_DX)
        Returns:
            None
        Raises:
            IOError on file open problems
            NasaAmesError
        """
        self.file = None
        self.encoding = None
        self.enc_line = None
        self.state = -1
        self.errors = 0
        self.warnings = 0
        self.strictness = strictness
        self.lnum = 0
        # some special attributes:
        # xformat: calcuated and used internally by write:
        self.xformat = None
        # xmindig: minimum digit of x used in the physical file
        # (order of magnitude)
        # is set by the reader when reading the data lines
        self.xmindig = None
        # min/max xmindig: can be set by the caller to restrict the output
        # precision of x
        # eg. minxmindig =-4, maxxmindig=-1: variable will have at least 1
        # digit after comma, but not more than 4
        self.minxmindig = None
        self.maxxmindig = None

        # min/max vmindig: minimum digit to be used for each var (order of
        # magnitude) can be set by the caller to restrict the precision
        # eg. minvmindig =-4, maxvmindig=-1: variable will have at least 1
        # digit after comma, but not more than 4
        self.minvmindig = []
        self.maxvmindig = []

        # self.minvmiss: caller can request to generate a minimal VMISS value
        # for the respective variable (do not add one order of magnitude if
        # the max value is less than the calculated VMISS)
        # Set to True if wanted for a given variable
        self.minvmiss = []

        # self.vmiss: caller can request a specifiv VMISS value.
        # This is only used if it can be used according to data (type and
        # maxvalue), minvmindig and maxvmindig
        self.vmiss = []

        # the main data attribute, which represents the file's content
        self.data = None
        self.init_data()

        self.logger = logging.getLogger("NasaAmes1001")

    def init_data(self):
        """
        Initializes the data object. Sets all attributes to None.
        Parameters:
            None
        Returns:
            None
        """
        self.data = DataObject(dict([(att, None)
                                     for att in self.__class__.DATA_ATTRIBS]))

    def init_state(self):
        """
        Initialize the object state before reading or writing operations.
        Parameters:
            None
        Returns:
            None
        """
        self.file = None
        self.state = -1
        self.errors = 0
        self.warnings = 0
        self.lnum = 0

    def curr_state_name(self):
        """
        Returns the name of the current reading state.
        Parameters:
            None
        Returns:
            state name (str)
        """
        return self.__class__.SECTIONS[self.state]

    def dx_from_data(self):
        """
        Calculates DX from the sample intervals.
        Parameters:
            None
        Returns:
            DX (real)
        There are some problematic cases with float representation:
            e.g. the sequence 1.1, 1.2, 1.3, ...
            would result in a dx between 0.09999999999999987
            and 0.10000000000000009
            (even worse with e.g. 1.000000001, 1.000000002, ...)

            Using Decimal instead of float would raise performance issues

            Solution: check dx with float operations (and almostequal)
            Then, in the end calculate a Decimal dx using the first two samples
            only.
        """
        # calculate dx
        if not self.data.DATA or not self.DATA[0] or len(self.DATA[0]) < 2:
            return 0
        if None in self.DATA[0]:
            raise NasaAmes1001Error(
                "missing values not allowed for x-values")
        if self.xmindig:
            # we need to round the values to xmindig
            magnitude = self.xmindig
            if magnitude > 0:
                magnitude -= 1
            magnitude *= -1
            data = [round(x, magnitude) for x in self.DATA[0]]
            # We test the average dx of all values (maybe rounded)
            # the result must be rounded to mindig.
            # In py3, we have additionally an issue when subtracting floats due
            # to number representation:
            # e.g. 309.625 - 309.583333 = 0.041667000000018106
            #      0.625-0.583333 = 0.04166700000000001
            # So rounding is even more crucial in python3.
            dx_ = round(
                sum([data[i]-data[i-1] for i in range(1, len(data))]) / \
                    (len(data)-1),
                magnitude)
        else:
            data = self.DATA[0]
            # We test the average dx of all values (unrounded, no xmindig)
            # I guess it will never be called w/o xmindig anyway
            dx_ = sum([data[i]-data[i-1] for i in range(1, len(data))]) / \
                (len(data)-1)
        for diff in zip(data, data[1:]):
            if not self._dx_equal(float(diff[1]-diff[0]), dx_):
                return 0
        return dx_

    def _dx_equal(self, dx1, dx2):
        """
        Compares two dx values, allowing differences according to the objects
        xmindig.
        Parameters:
            dx1, dx2    the two dx values to be compared
        Returns:
            True/False
        """
        # if x output precission is restricted by the caller, use this
        # precission as comp. criteria
        if self.xmindig:
            magnitude = self.xmindig
            if self.xmindig >= 1:
                # if magnitude is at least whole integers, we just compare
                # we had problems with monthly data (29-31 days), which
                # generated dx=30, because of allowing +- 1 in dx comparison,
                # which is wrong.
                return dx1 == dx2
            if abs(dx1 - dx2) >= 1.1 * 10 ** magnitude:
                # If difference is bigger than one digit difference in the
                # lowest represented digit, DX is different
                # This accommodates rounding issues in the last digit.
                return False
        else:
            return float_almostequal(dx1, dx2)
        return True

    def error(self, msg, lnum=True, exception=False, lnum_override=None,
              counter_increase=1):
        """
        Error handling for file read.
        Error will be logged, lnum included if passed.
        Parameters:
            msg         error message
            lnum        include line number (optional)
            exception   raises exception if true
            lnum_override
                        override the internal line number
        Returns:
            None
        Raises:
            NasaAmesError when parameter exception is True
        """
        self.errors += counter_increase
        if lnum:
            msg = "line {}: {}".format(
                lnum_override if lnum_override is not None else self.lnum, msg)
        self.logger.error(msg)
        if exception:
            raise NasaAmes1001Error(msg)

    def warning(self, msg, lnum=True, lnum_override=None, counter_increase=1):
        """
        Warning message for file read.
        Worning will be logged, lnum included if passed.
        Parameters:
            msg         warning message
            lnum        include line number (optional)
        Returns:
            None
        """
        self.warnings += counter_increase
        if lnum:
            msg = "line {}: {}".format(
                lnum_override if lnum_override is not None else self.lnum, msg)
        self.logger.warning(msg)
