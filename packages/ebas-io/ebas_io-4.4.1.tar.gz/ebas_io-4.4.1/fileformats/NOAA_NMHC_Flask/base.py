"""
NOAA NMHC Flask data file format
   base class

$Id: base.py 2686 2021-08-18 11:24:59Z pe $
"""

import logging

class NOAA_NMHC_Flask_Error(Exception):
    """
    Base error class for this module.
    """
    pass


class NOAA_NMHC_Flask_Inconsistent(NOAA_NMHC_Flask_Error):
    """
    Exception class raised when the object is inconsistent.
    """
    pass


class NOAA_NMHC_Flask_Rawdata_Base(object):
    """
    Class for the file's raw data.
    """
    def __init__(self):
        """
        Set up the raw data object.
        Parameters:
            None
        """
        self._logger = logging.getLogger('NOAA_NMHC_Flask')

        self.num_hea_lines = None
        self.raw_data = [] # the full file as list of strings
        self.header = []   # the raw header from file as a list of strings
        self.data = []     # the raw data from the file as a list of strings


class NOAA_NMHC_Flask_HeaderContact_Base(object):
    """
    Class for the contact information in the file's header.
    """
    def __init__(self):
        """
        Set up the object.
        Parameters:
            None
        """
        self._logger = logging.getLogger('NOAA_NMHC_Flask')

        self.parameter = None
        self.name = None
        self.telephone = None
        self.email = None

    def check(self):
        """
        Check the contact information object's consistency.
        Parameters:
            None
        Returns:
            None
        Raises:
            NOAA_NMHC_Flask_Inconsistent on any inconsistency
        The syntax of all fields is checked on parsing. Here we just need to
        consistency between the fields.
        """
        # Nothing to do so far. The syntax of all fields is checked on parsing
        pass


class NOAA_NMHC_Flask_HeaderDescription_Base(object):
    """
    Class for the description information in the file's header.
    """
    def __init__(self):
        """
        Set up the header object.
        Parameters:
            None
        """
        self._logger = logging.getLogger('NOAA_NMHC_Flask')

        self.site_code = None
        self.project_abbr = None
        self.strategy_abbr = None
        self.sample_constraints = None
        self.creation_time = None  # datetime.datetime

    def check(self):
        """
        Check the description object's consistency.
        Parameters:
            None
        Returns:
            None
        Raises:
            NOAA_NMHC_Flask_Inconsistent on any inconsistency
        The syntax of all fields is checked on parsing. Here we just need to
        consistency between the fields.
        """
        # Nothing to do so far. The syntax of all fields is checked on parsing
        pass


class NOAA_NMHC_Flask_Header_Base(object):
    """
    Class for the file's header information.
    """
    def __init__(self):
        """
        Set up the header object.
        Parameters:
            None
        """
        self._logger = logging.getLogger('NOAA_NMHC_Flask')

        self.comments = []           # list of comment blocks (each list of str)
        self.contact = []            # list of contact objects
        self.collaborator_name = []  # list of collaborator names
        self.collaborator_comment = []  # list of collaborator comments
        self.collaborator_url = []   # list of collaborator url's
        self.collaborator_comment = []  # list of collaborator_comments
        self.description = None      # one description object
        self.data_fields = []        # list of data field names

    def check(self):
        """
        Check the header object's consistency.
        Parameters:
            None
        Returns:
            None
        Raises:
            NOAA_NMHC_Flask_Inconsistent on any inconsistency
        The syntax of all fields is checked on parsing. Here we just need to
        consistency between the fields.
        """
        if len(self.comments) != 4:
            raise NOAA_NMHC_Flask_Inconsistent(
                "expected {} comment blocks in header, found {}".format(
                    4, len(self.comments)))
            # This needs probably some change, when we understand the header
            # better...
        if len(self.contact) < 1:
            raise NOAA_NMHC_Flask_Inconsistent(
                "found no conatct metadata in header")
        for cont in self.contact:
            cont.check()
        if self.description is None:
            raise NOAA_NMHC_Flask_Inconsistent(
                "found no description meatdata in header")
        self.description.check()
        if len(self.data_fields) < 1:
            raise NOAA_NMHC_Flask_Inconsistent(
                "found no data_fields metadata in header")

class NOAA_NMHC_Flask_Data_Base(object):
    """
    Class for the file's header information.
    """

    DATA_FIELDS = [
        'sample_site_code', 'sample_year', 'sample_month',
        'sample_day', 'sample_hour', 'sample_minute',
        'sample_seconds', 'sample_id', 'sample_method',
        'parameter_formula', 'analysis_group_abbr',
        'analysis_value', 'analysis_uncertainty', 'analysis_flag',
        'analysis_instrument', 'analysis_year', 'analysis_month',
        'analysis_day', 'analysis_hour', 'analysis_minute',
        'analysis_seconds', 'sample_latitude', 'sample_longitude',
        'sample_altitude', 'sample_elevation',
        'sample_intake_height', 'event_number']
    EXTRA_FIELDS = ['sample_time', 'analysis_time']

    def __init__(self, lnum_offset):
        """
        Set up the data object.
        Parameters:
            None
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._lnum_offset = lnum_offset

        # A long list of attributes
        # Do not construct something like self.__dict__.append of DATA_FIELDS...
        # Rather list the attributes explicitly to not confuse pylint, and to
        # make editor completition work.

        # one attribute for each data_field (lists):
        self.sample_site_code = []      # list of strings
        self.sample_year = []          # list of int
        self.sample_month = []          # list of int
        self.sample_day = []            # list of int
        self.sample_hour = []           # list of int
        self.sample_minute = []         # list of int
        self.sample_seconds = []        # list of int
        self.sample_id = []             # list of strings
        self.sample_method = []         # list of strings
        self.parameter_formula = []     # list of strings
        self.analysis_group_abbr = []   # list of strings
        self.analysis_value = []        # list of float/None
        self.analysis_uncertainty = []  # list of float/None
        self.analysis_flag = []         # list of strings
        self.analysis_instrument = []   # list of strings
        self.analysis_year = []        # list of int
        self.analysis_month = []        # list of int
        self.analysis_day = []          # list of int
        self.analysis_hour = []         # list of int
        self.analysis_minute = []       # list of int
        self.analysis_seconds = []      # list of int
        self.sample_latitude = []       # list of float
        self.sample_longitude = []      # list of float
        self.sample_altitude = []       # list of float
        self.sample_elevation = []      # list of float
        self.sample_intake_height = []  # list of float
        self.event_number = []          # list of strings

        # some extra fields:
        self.sample_time = []           # list of datetimme.datetime
        self.analysis_time = []         # list of datetimme.datetime

        # check class attributes are consistent with instance attributes:
        if set([x for x in list(self.__dict__.keys()) if not x.startswith('_')]) != \
           set(self.__class__.DATA_FIELDS+self.__class__.EXTRA_FIELDS):
            raise RuntimeError(
                "Class {} internal error: attribute inconsistency".format(
                    self.__class__.__name__))

    def check(self):
        """
        Check the file object's consistency.
        Parameters:
            None
        Returns:
            None
        Raises:
            NOAA_NMHC_Flask_Inconsistent on any inconsistency
        """
        # consistent list lengths
        lens = [len(self.__dict__[att])for att in self.__class__.DATA_FIELDS+\
                                                  self.__class__.EXTRA_FIELDS]
        if len(set(lens)) != 1:
            raise NOAA_NMHC_Flask_Inconsistent(
                'data variables have non-equal number of elements')
        # minimum 1 sample
        if lens[0] < 1:
            raise NOAA_NMHC_Flask_Inconsistent('no data')

        # only one site per file
        if len(set(self.sample_site_code)) > 1:                                    
            raise NOAA_NMHC_Flask_Inconsistent(
                'data from {} different sites'.format(
                    len(set(self.sample_site_code))))
        if len(set(self.sample_latitude)) > 1:                                     
            raise NOAA_NMHC_Flask_Inconsistent(
                '{} different latitude values (should be only one)'.format(
                    len(set(self.sample_latitude))))
        if len(set(self.sample_longitude)) > 1:
            raise NOAA_NMHC_Flask_Inconsistent(
                '{} different longitude values (should be only one)'.format(
                    len(set(self.sample_longitude))))
        if len(set(self.sample_elevation)) > 1:
            raise NOAA_NMHC_Flask_Inconsistent(
                '{} different elevation values (should be only one)'.format(
                    len(set(self.sample_elevation))))

        # only one parameter per file
        if len(set(self.parameter_formula)) > 1:
            raise NOAA_NMHC_Flask_Inconsistent(
                'data of {} different parameters'.format(
                    len(set(self.parameter_formula))))
        # only one analysis_group_abbr and analysis_instrument per file
        if len(set(self.analysis_group_abbr)) > 1:
            raise NOAA_NMHC_Flask_Inconsistent(
                'data of {} different analysis_group_abbr'.format(
                    len(set(self.analysis_group_abbr))))
        if len(set(self.analysis_instrument)) > 1:
            raise NOAA_NMHC_Flask_Inconsistent(
                'data of {} different analysis_instrument'.format(
                    len(set(self.analysis_instrument))))

    def split(self):
        """
        Splits into multiple timeseries, if there are multiple samples per
        time instant. Thus rendereng the timeseries strictly monotonically
        increasing.
        Parameters:
            None
        Returns:
            list of objects (same class).
        """
        series = []
        for i in range(len(self.sample_site_code)):
            for j in range(len(series)):
                if self.sample_time[i] not in series[j].sample_time:
                    # add sample
                    for key in self.__class__.DATA_FIELDS + \
                               self.__class__.EXTRA_FIELDS:
                        series[j].__dict__[key].append(self.__dict__[key][i])
                    break
            else:
                # new series needed:
                new_series = self.__class__()
                for key in self.__class__.DATA_FIELDS + \
                           self.__class__.EXTRA_FIELDS:
                    new_series.__dict__[key].append(self.__dict__[key][i])
                series.append(new_series)
        return series

    def aggregate(self):
        """
        Multiple samples per sample time are aggregated.
        Parameters:
            None
        Returns:
            list of tuple (sample_time, [{}
        """
        return NOAA_NMHC_Flask_Data_Aggregated(self, self._lnum_offset)


class NOAA_NMHC_Flask_Data_Aggregated(NOAA_NMHC_Flask_Data_Base):
    """
    Class for aggregeated data
    Same as NOAA_NMHC_Flask_Data, but some attibutes elements are lists:
        sample_id, event_number,
        analysis_value, analysis_uncertainty, analysis_flag,
        analysis_year, analysis_month, analysis_day,
        analysis_hour, analysis_minute, analysis_seconds,
    Those lists contain the analysis elements of the original, unaggregated data.

    Attention: 
    analysis_group_abbr and analysis_instrument must be constant in file and thus
    also within one aggregated sample
    """

    AGGREGATED_FIELDS = [
        'sample_id', 'event_number',
        'analysis_value', 'analysis_uncertainty', 'analysis_flag',
        'analysis_year', 'analysis_month', 'analysis_day',
        'analysis_hour', 'analysis_minute', 'analysis_seconds']

    def _unaggregated_fields(aggregated_fields):
        """
        Problem with list comprehensiopns in python class code, see
        https://stackoverflow.com/a/13913933/1522205
        We use a temp. method as workaround:
        """
        return [k for k in NOAA_NMHC_Flask_Data_Base.DATA_FIELDS+\
                           NOAA_NMHC_Flask_Data_Base.EXTRA_FIELDS
                if k not in aggregated_fields]

    UNAGGREGATED_FIELDS = _unaggregated_fields(AGGREGATED_FIELDS)

    def __init__(self, data, lnum_offset):
        """
        Set up the aggrege=ated data object.
        Parameters:
            data   the original (unaggrgated) data object
        Returns:
            None
        Raises:
            NOAA_NMHC_Flask_Inconsistent on any inconsistency
        """
        super(NOAA_NMHC_Flask_Data_Aggregated, self).__init__(lnum_offset)
        aggr_att = [att for att in self.__class__.DATA_FIELDS
                    if att.startswith('analysis_')]
        self._line_numbers = []
        for i in range(len(data.sample_time)):
            if data.sample_time[i] in self.sample_time:
                j = self.sample_time.index(data.sample_time[i])
                self._line_numbers[j].append(lnum_offset + i)
                for att in self.__class__.AGGREGATED_FIELDS:
                    self.__dict__[att][j].append(data.__dict__[att][i])
                # check if all unaggregated data do not vary:
                if self.__dict__[att][j][-1] != data.__dict__[att][i]:
                    raise NOAA_NMHC_Flask_Inconsistent(
                        "Aggregation inconsistency in sample {}"
                        .format(self.sample_id))
            else:
                self._line_numbers.append([lnum_offset + i])
                for att in self.__class__.UNAGGREGATED_FIELDS:
                    self.__dict__[att].append(data.__dict__[att][i])
                for att in self.__class__.AGGREGATED_FIELDS:
                    self.__dict__[att].append([data.__dict__[att][i]])
        self.check()

    def check(self):
        """
        Check the file object's consistency.
        Parameters:
            None
        Returns:
            None
        Raises:
            NOAA_NMHC_Flask_Inconsistent on any inconsistency
        """
        super(NOAA_NMHC_Flask_Data_Aggregated, self).check()
        for i in range(len(self.sample_site_code)):
            # consistent list lengths for aggregated elements:
            lens = [len(self.__dict__[att][i])
                    for att in self.__class__.AGGREGATED_FIELDS]
            if len(set(lens)) != 1:
                raise NOAA_NMHC_Flask_Inconsistent(
                    'aggregated variables have non-equal number of elements in '
                    'element {}'.format(i))


class NOAA_NMHC_Flask_Base(object):
    """
    Base class for the file format.
    """
    def __init__(self):
        """
        Set up object.
        Parameters:
            None
        Returns:
            None
        """
        self._logger = logging.getLogger('NOAA_NMHC_Flask')
        self.filename = None
        self.file = None
        self.raw = None
        self.header = None
        self.data = None
        # will be NOAA_NMHC_Flask_Data in the final class

    def check(self):
        """
        Check the file object's consistency.
        Parameters:
            None
        Returns:
            None
        Raises:
            NOAA_NMHC_Flask_Inconsistent on any inconsistency
        """
        self.header.check()
        self.data.check()
