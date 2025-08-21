"""
EANET filter file format
   base class

$Id: base.py 2762 2021-11-30 23:42:49Z pe $
"""

import logging
import re
import datetime
from collections import OrderedDict

def colnum_string(col):
    """
    Get the column strring for a spreadsheet adddress.
    Parameters:
        col    column number (0 based)
    Returns:
        Spreadsheet column address string A, B, ..., Z, AB, ...
    """
    col += 1
    string = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        string = chr(65 + remainder) + string
    return string

def column_string_to_num(string):
    """

    """
    col = ord(string[-1]) - 65
    if string[:-1]:
        return 26 * (column_string_to_num(string[:-1]) + 1) + col
    return col

def get_address(row, col):
    """
    Translate 0 based row and col to spreadsheet adddress, e.g D25.
    Parameters:
        row    row number (0 based)
        col    column number (0 based)
    Returns:
        Spreadsheet address (e.g. "A25")
    """
    return colnum_string(col) + str(row+1)

def from_address(address):
    """
    Converts spreadsheet notation (e.g. A1) to row and col number.
    Parameters:
        address    spreadsheet notation string, e.g. A1
    Returns:
        tuple, row and col number, both 0 based (row, col)
    """
    reg = re.match(r'^([A-Z]+)([0-9]+)$', address)
    if not re:
        raise ValueError('{} is not in spreadsheet notation'.format(address))
    return(int(reg.group(2))-1, column_string_to_num(reg.group(1)))


class EanetError(Exception):
    """
    Base error class for this module.
    """
    pass


class EanetFilterVariable(object):  # pylint: disable=R0903
    # R0903: Too few public methods
    #     --> this is a base class
    """
    One variable in a filer file.
    """

    def __init__(self, name, unit, samples, flags):
        """
        Initialize the object.
        """
        self.logger = logging.getLogger("EanetFilterVar")
        self.name = name
        self.unit = unit
        self.samples = samples
        self.flags = flags


class EanetPrecipVariable(object):  # pylint: disable=R0903
    # R0903: Too few public methods
    #     --> this is a base class
    """
    One variable in a filer file.
    """

    def __init__(self, name, unit, samples, flags):
        """
        Initialize the object.
        """
        self.logger = logging.getLogger("EanetFilterVar")
        self.name = name
        self.unit = unit
        self.samples = samples
        self.flags = flags

class EanetBase(object):
    """
    Base class for all EANET files.
    """
    def __init__(self):
        """
        Initialize the object.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.errors = 0
        self.warnings = 0

    def message(self, severity, errtxt, *args, **kwargs):
        """
        Log a message with reference to row and column
        Parameters:
            severity  logging severity
            errtxt    error text
            *args     optional additional arguments passed to logger.log
            row       row number (0 based)
            col       col number (0 based)
        Note: using kwargs instead og row=None, col=None because this form is
        not allowed in py2.
        Returns:
            None
        """
        # some manual parameter handling (see above, restrictions in py2)
        illegal = [x for x in kwargs if x not in ('row', 'col')]
        if illegal:
            raise TypeError('unexpected keyword arguments {}'.format(
                ', '.join(illegal)))
        row = kwargs.get("row", None)
        col = kwargs.get("col", None)

        spec = ''
        if row is not None:
            spec += "Row {}".format(row+1)
            if col is not None:
                spec += ', col {} [{}]: '.format(col+1, get_address(row, col))
        elif col is not None:
            spec += "Col %s [%s]: ".format(col+1, colnum_string(col))
        if 'row' in kwargs:
            del kwargs['row']
        if 'col' in kwargs:
            del kwargs['col']
        self.logger.log(severity, "%s"+errtxt, spec, *args, **kwargs)

    def error(self, errtxt, *args, **kwargs):
        """
        Log an error with reference to row and column
        Parameters:
            errtxt    error text
            *args     optional additional arguments passed to logger.log
            row       row number (0 based)
            col       col number (0 based)
        Returns:
            None
        """
        self.errors += 1
        self.message(logging.ERROR, errtxt, *args, **kwargs)

    def warning(self, errtxt, *args, **kwargs):
        """
        Log a warning with reference to row and column
        Parameters:
            errtxt    error text
            *args     optional additional arguments passed to logger.log
            row       row number (0 based)
            col       col number (0 based)
        Returns:
            None
        """
        self.warnings += 1
        self.message(logging.WARNING, errtxt, *args, **kwargs)

    def info(self, errtxt, *args, **kwargs):
        """
        Log an info with reference to row and column
        Parameters:
            errtxt    error text
            *args     optional additional arguments passed to logger.log
            row       row number (0 based)
            col       col number (0 based)
        Returns:
            None
        """
        self.message(logging.INFO, errtxt, *args, **kwargs)

    def _parse_datetime(self, row, col):
        """
        Parse date/time object form row,col (date) and row,col+1 (time)
        Parameters:
            row   row in rawdata
            col   column in rawdata (date), col+1 is time
        Expected date format: YYYY/MM/DD
        Expected time format: HH:MI
        """
        reg = re.match(
            r'^(\d+)\/(\d+)\/(\d+)$', self._rawdata[row][col])
        if not reg:
            self.error(
                "Date format error '%s'", self._rawdata[row][col],
                row=row, col=col)
            return None
        else:
            year, mon, day = (int(x) for x in reg.groups())

        if not self._rawdata[row][col+1]:
            # interpret empty as 00:00
            hour = 0
            minute = 0
        else:
            reg = re.match(
                r'^(\d+):(\d+)$', self._rawdata[row][col+1])
            if not reg:
                self.error(
                    "Time format error '%s'", self._rawdata[row][col],
                    row=row, col=col+1)
                return None
            else:
                hour, minute = (int(x) for x in reg.groups())

        try:
            return datetime.datetime(year, mon, day, hour, minute)
        except ValueError as excpt:
            self.error(
                "Datet time error: '%s'", excpt,
                row=row, col=col+1)
            return None


class EanetFilterBase(EanetBase):  # pylint: disable=R0902, R0903
    # R0902: Too many instance attributes
    # R0903: Too few public methods
    #     --> this is a base class
    """
    Base class for EANET filter files.
    """

    def __init__(self):
        """
        Initialize the object.
        """
        super(EanetFilterBase, self).__init__()
        self.file_name = None
        self.country_name = None
        self.site_code = None
        self.site_name = None
        self.sample_times = []
        self.variables = []  # list of EanetFilterVariable
        self.notes = None  # None if no notes col in file, [] if notes
        self._hasnotes = None
        self._lastcol = None

class EanetPrecipForm(object):
    """
    Object representing a form in the document.
    """

    def __init__(self, parent, index_in_file, name, layout):
        """
        Set up the object.
        Parameters:
            parent         The parent file object
            index_in_file  Index of this object in the parent
            name           Name of this form
            layout         The layout of the form (part from file's LAYOUT)
        Returns:
            None
        """
        self.file = parent
        self.index_in_file = index_in_file
        self.name = name
        self.layout = layout
        self.variables = []

    def var_by_name(self, name):
        """
        Get a variable by name.
        (Variable name are unique withing a form (this is checked at class
        creation).
        Parameters:
            name    variable name from the LAYOUT
        Returns:
            EantePrecipVariable object
        Raises:
            KeyError
        """
        for var in self.variables:
            if var.name == name:
                return var
        raise KeyError("No variable named " + name)


class EanetPrecipBase(EanetBase):  # pylint: disable=R0902, R0903
    # R0902: Too many instance attributes
    # R0903: Too few public methods
    #     --> this is a base class
    """
    Base class for EANET filter files.
    """

    LAYOUT = OrderedDict([
        (
            u'Form (Wet A)  No. 1   Results of wet deposition analysis '
            u'(Anion)',
            {
                'header': "B2",
                'start': "B11",
                'sample_number': "Sample No.",
                'sample_times': True,
                'vars': [  # --> OrderedDict
                    # will be changed to OrderedDict after checking for
                    # uniqueness of keys!
                    (u"SO42-",
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'NO3-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Cl-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'HCO3-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'F-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Br-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'NO2-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'PO43-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 1>',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 2>',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Date of analysis',
                     {
                         'flags': 0,
                         'merge': 'concat',
                     }),
                    (u'Note',
                     {
                         'flags': 0,
                         'merge': 'concat',
                     }),
                ],
            }
        ),

        (
            u'Form (Wet A)  No. 2   Results of wet deposition analysis '
            u'(Cation)',
            {
                'header': "AX2",
                'start': "AX11",
                'sample_number': "Sample No.",
                'sample_times': True,
                'vars': [  # --> OrderedDict
                    # will be changed to OrderedDict after checking for
                    # uniqueness of keys!
                    (u'NH4+',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Na+',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'K+',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Ca2+',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Mg2+',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 1>',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 2>',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Date of analysis',
                     {
                         'flags': 0,
                         'merge': 'concat',
                     }),
                    (u'Note',
                     {
                         'flags': 0,
                         'merge': 'concat',
                     }),
                ],
            }
        ),

        (
            u'Form (Wet A)  No. 3   Results of wet deposition analysis '
            u'(EC, pH, R1, R2, Precipitation)',
            {
                'header': "CH2",
                'start': "CH11",
                'sample_number': "Sample No.",
                'sample_times': True,
                'vars': [  # --> OrderedDict
                    # will be changed to OrderedDict after checking for
                    # uniqueness of keys!
                    (u'EC',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'pH',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'R1',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'R2',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Amount of sample',
                     {
                         'flags': 3,
                         'merge': 'sum',
                     }),
                    (u'Amount of precipitation',
                     {
                         'flags': 0,
                         'merge': 'sum',
                         'is_amount': True,
                     }),
                    (u'Method Code',
                     {
                         'flags': 3,
                         'merge': 'first',
                     }),
                    (u'Date of analysis',
                     {
                         'flags': 0,
                         'merge': 'concat',
                     }),
                    (u'Note',
                     {
                         'flags': 0,
                         'merge': 'concat',
                     }),
                ],
            }
        ),

        (
            u'Form (Wet A)  No. 4   Results of wet deposition analysis '
            u'(Organic ions)',
            {
                'header': "DO2",
                'start': "DO11",
                'sample_number': "Sample No.",
                'sample_times': True,
                'vars': [  # --> OrderedDict
                    # will be changed to OrderedDict after checking for
                    # uniqueness of keys!
                    (u'HCOO-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'CH3COO-',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'(COO- )2',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 1>',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 2>',
                     {
                         'flags': 3,
                         'merge': 'mean',
                     }),
                    (u'Date of analysis',
                     {
                         'flags': 0,
                         'merge': 'concat',
                     }),
                    (u'Note',
                     {
                         'flags': 0,
                         'merge': 'concat',
                     }),
                ],
            }
        ),

        (
            u'Summary 1',
            {
                'header': "EQ2",
                'start': "EQ11",
                'sample_number': "Sample\n No.",
                'sample_times': False,
                'vars': [  # --> OrderedDict
                    # will be changed to OrderedDict after checking for
                    # uniqueness of keys!
                    (u'nss-SO42-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'nss-Ca2+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'H+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'HCOO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'CH3COO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'   COOH\n   COO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'(COO- )2',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 1>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 2>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                ],
            }
        ),

        (
            u'Summary 2',
            {
                'header': "FB2",
                'start': "FB11",
                'sample_number': "Sample\n No.",
                'sample_times': False,
                'vars': [  # --> OrderedDict
                    # will be changed to OrderedDict after checking for
                    # uniqueness of keys!
                    (u'SO42-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NO3-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Cl-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'HCO3-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'F-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Br-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NO2-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'PO43-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 1>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 2>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'HCOO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'CH3COO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'(COO- )2',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 3>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 4>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Anion',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NH4+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Na+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'K+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Ca2+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Mg2+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 5>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 6>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'H+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Cation',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'C+A',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'nss-SO42-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'nss-Ca2+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'EC x ppt.',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                ],
            }
        ),

        (
            u'Summary 3',
            {
                'header': "GG2",
                'start': "GG11",
                'sample_number': "Sample\n No.",
                'sample_times': False,
                'vars': [  # --> OrderedDict
                    # will be changed to OrderedDict after checking for
                    # uniqueness of keys!
                    (u'SO42-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NO3-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Cl-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'HCO3-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'F-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Br-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NO2-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'PO43-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 1>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 2>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'HCOO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'CH3COO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'(COO- )2',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 3>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 4>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Anion',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NH4+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Na+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'K+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Ca2+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Mg2+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 5>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 6>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'H+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Cation',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'C+A',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Req. R1',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'R1',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                ],
            }
        ),

        (
            u'Summary 4',
            {
                'header': "HK2",
                'start': "HK11",
                'sample_number': "Sample No.",
                'sample_times': False,
                'vars': [  # --> OrderedDict
                    # will be changed to OrderedDict after checking for
                    # uniqueness of keys!
                    (u'SO42-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NO3-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Cl-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'HCO3-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'F-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Br-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NO2-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'PO43-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 1>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 2>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'HCOO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'CH3COO-',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'(COO- )2',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 3>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 4>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Anion',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'NH4+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Na+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'K+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Ca2+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Mg2+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 5>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'<EMPTY 6>',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'H+',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Cation',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'ECcal',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'ECmes',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Req. R2',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'R2',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Amount of ppt. (cal)',
                     {
                         'flags': 0,
                         'merge': 'sum',
                     }),
                    (u'Amount of ppt.',
                     {
                         'flags': 0,
                         'merge': 'sum',
                     }),
                    (u'%CE  (M/R)',
                     {
                         'flags': 0,
                         'merge': 'mean',
                     }),
                    (u'Sampling period',
                     {
                         'flags': 0,
                         'merge': 'sum',
                     }),
                ],
            }
        ),
    ])
    for _, form in LAYOUT.items():
        # Make sure var names are unique!
        names = [var[0] for var in form['vars']]
        if len(names) != len(set(names)):
            raise RuntimeError(
                "EanetPrecipBase.LAYOUT misconfigured (non unique var name)")
        # Then make an OrderedDict.
        form['vars'] = OrderedDict(form['vars'])


    def __init__(self):
        """
        Initialize the object.
        """
        super(EanetPrecipBase, self).__init__()
        self.file_name = None
        self.site_code = None
        self.forms = []  # different forms of the sheet

        self.country_name = None
        self.site_name = None
        self.laboratory = None
        self.reporter = None
        self.funnel_diameter = None

        self.sample_numbers = []
        self.sample_times = []
