"""
/Xml/base.py
$Id: base.py 2561 2020-12-07 23:09:30Z pe $

Base class for XML.
Has (still) all attributes as base class for Nasa Ames 1001.

History:
V.1.0.0  2014-08-05  toh  initial version

"""
import logging
from nilutility.ndecimal import Decimal
from nilutility.float_helper import float_almostequal
from nilutility.datatypes import DataObject

class XmlError(Exception):
    """
    Error class for XML.
    """
    pass
    
class XmlBase(object):
    # pylint: disable-msg=R0902
    # R0902: Too many instance attributes
    """
    Partial class Xml: Base class used by Parts.
    """

    # all data attibutes (set on read, getattr implemented)
    # toh: all attributes are lists as every variable will be
    #      written into a separate result set; thus attributes
    #      might vary with variables
    #      (although it's not necessary/implemented for every attribute yet)
    DATA_ATTRIBS = [
        'SAMPLE_TIMES',     # list of time tuples; local: sample_times
        'STATION_CODE',     # list of str; XML: StationCode,    EBAS: ST_STATION_CODE,   local: [variables[vnum].]metadata.station_code
        'STATION_NAME',     # list of str; XML: StationName,    EBAS: ST_NAME,           local: [variables[vnum].]metadata.station_name
        'INST_TYPE',        # list of str; XML: InstrumentType, EBAS: FT_TYPE,           local: [variables[vnum].]metadata.instr_type
        'COMP_NAME',        # list of str; XML: ComponentName,  EBAS: CO_COMP_NAME,      local: [variables[vnum].]metadata.comp_name
        'CHARACTERISTICS',  # list of dic; XML: Characteristics EBAS: CT_TYPE ,          local: [variables[vnum].]metadata.characteristics
        'MATRIX_NAME',      # list of str; XML: Matrix,         EBAS: MA_MATRIX_NAME,    local: [variables[vnum].]metadata.matrix
        'UNIT',             # list of str; XML: Unit,           EBAS: PM_UNIT,           local: [variables[vnum].]metadata.unit
        'STATISTIC_CODE',   # list of str; XML: Statistics,     EBAS: SC_STATISTIC_CODE, local: [variables[vnum].]metadata.statistics
        'RESCODE',          # list of str; XML: ResolutionCode, EBAS: DS_RESCODE,        local: [variables[vnum].]metadata.resolution
        'DATA_LEVEL',       # list of str; XML: DataLevel,      EBAS: DL_DATA_LEVEL,     local: [variables[vnum].]metadata.datalevel; optional
        'UNCERTAINTY',      # list of str; XML: MeasurementUncertainty, EBAS: HVM_UNCERTAINTY, local: [variables[vnum].]metadata.uncertainty
        'POSITION',         # list of str; XML: Position,       EBAS: ST_LATITUDE, ST_LONGITUDE, ST_ALTITUDE_ASL; local: station_latitude, station_longitude, station_altitude
        'HEIGHT_AGL',       # list of str; XML: HeightAGL,      EBAS: HVM_HEIGHT_AGL,    local: [variables[vnum].]metadata.mea_height; optional
        'DATA',             # list of lists of float/decimal; XML: Values
        'SETKEY',           # list of str; XML: setkey,         EBAS: DS_SETKEY          local: [variables[vnum].]metadata.setkey
        'FLAGS',            # list of lists of str;             toh: flags are not required yet
        'NV',               # int;           number of primary dependent variables
        # used by write only:
        ]

    # attributes that can be set (before write), others will be calculated
    SETABLE_DATA_ATTRIBS = [
                            'SAMPLE_TIMES',
                            'STATION_CODE',
                            'STATION_NAME',
                            'INST_TYPE',
                            'COMP_NAME',
                            'CHARACTERISTICS',
                            'MATRIX_NAME',
                            'UNIT',
                            'STATISTIC_CODE',
                            'RESCODE',
                            'DATA_LEVEL',
                            'UNCERTAINTY',
                            'POSITION',
                            'HEIGHT_AGL',
                            'DATA',
                            'SETKEY',
                            'FLAGS'
                            ]
    # read/write states
    # toh: ignore all items that are not required by XML
    # SAMPLE_TIMES will be written by default
    SECTIONS = [
                # 'SAMPLE_TIMES', # will be written by default
                'STATION_CODE',
                'STATION_NAME',
                'INST_TYPE',
                'COMP_NAME',
                'CHARACTERISTICS',
                'MATRIX_NAME',
                'UNIT',
                'STATISTIC_CODE',
                'RESCODE',
                'DATA_LEVEL',
                'UNCERTAINTY',
                'POSITION',
                'HEIGHT_AGL',
                'DATA',
                'SETKEY'
                ]
    
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

    def __init__(self, resultset_id, strictness=0):
        """
        Paramaters:
            resultset_id    increasing number (id for the resultset to be
                            generated) - needed only in _set_pos()
            strictness      bit field for strictness on read
                            (currently only STRICT_NUMFORMAT)
        Returns:
            None
        Raises:
            IOError on file open problems
            NasaAmesError
        """
        self.file = None
        self.state = -1
        self.errors = 0
        self.warnings = 0
        self.resultset_id = resultset_id
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
        
        # min/max vmindig: minimum digit to be used for each var (order of magnitude)
        # can be set by the caller to restrict the precision
        # eg. minvmindig =-4, maxvmindig=-1: variable will have at least 1
        # digit after comma, but not more than 4
        self.minvmindig = None
        self.maxvmindig = None
        
        # self.minvmiss: caller can request to generate a minimal VMISS value
        # for the respective variable (do not add one order of magnitude)
        self.minvmiss = None
        
        # the main data attribute, which represents the file's content
        self.data = None
        self.init_data()
        
        self.logger = logging.getLogger("Xml")

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
        if not self.data.DATA:
            return 0
        totaldiff = None
        for diff in zip(self.data.DATA[0], self.data.DATA[0][1:]):
            if diff[0] is None or diff[1] is None:
                raise XmlError(
                    "missing values not allowed for x-values")
            if not totaldiff:
                totaldiff = float(diff[1] - diff[0])
            # if x output precission is restricted by the caller, use this
            # precission as comp. criteria
            if self.xmindig:
                magnitude = self.xmindig
                if self.xmindig >= 1:
                    # xmindig is != order of magnitude
                    magnitude = self.xmindig - 1
                if abs(diff[0] + totaldiff - diff[1]) >= \
                   0.5* 10 ** magnitude:
                    totaldiff = None
                    break
            elif not float_almostequal(float(diff[0] + totaldiff),
                                       float(diff[1])):
                totaldiff = None
                break
        # covers also special case: none ore one sample:
        if totaldiff is None:
            return 0
        return float(Decimal(str(self.data.DATA[0][1])) - \
                     Decimal(str(self.data.DATA[0][0])))

    def error(self, msg, lnum=True, exception=False):
        """
        Error handling for file read.
        Error will be logged, lnum included if passed.
        Parameters:
            msg         error message
            lnum        include line number (optional)
            exception   raises exception if true
        Returns:
            None
        Raises:
            NasaAmesError when parameter exception is True
        """
        self.errors += 1
        if lnum:
            msg = "line {}: {}".format(self.lnum, msg)
        self.logger.error(msg)
        if exception:
            raise XmlError(msg)

    def warning(self, msg, lnum=True):
        """
        Warning message for file read.
        Worning will be logged, lnum included if passed.
        Parameters:
            msg         warning message
            lnum        include line number (optional)
        Returns:
            None
        """
        self.warnings += 1
        if lnum:
            msg = "line {}: {}".format(self.lnum, msg)
        self.logger.warning(msg)

