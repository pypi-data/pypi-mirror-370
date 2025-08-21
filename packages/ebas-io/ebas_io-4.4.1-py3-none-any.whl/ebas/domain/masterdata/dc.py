"""
ebas/domain/masterdata/dc.py
$Id: dc.py 2669 2021-06-28 15:01:46Z pe $

EBAS Base Class for Dataset Characteristics

This module implements the class DCBase.

History:
V.1.0.0  2013-11-27  pe  initial version

"""

from .offline_masterdata import CTOfflineMasterData
from ..base import EbasDomainError
from ebas.domain.masterdata.ip import EbasMasterIP
from ebas.domain.basic_domain_logic.datalevel import base_datalevel
from .co import PTR_MS_COMP

class DCError(EbasDomainError):
    """
    Exception class raised for invalid DC.
    """
    pass

class DCWarning(Exception):
    """
    Exception class raised for DC warnings.
    """
    def __init__(self, msg, ret=None):
        """
        Exception class used for warnings.
        Can hold a return value (used for warnings raised in DCBase).
        """
        Exception.__init__(self, msg)
        self.ret = ret


class DCListBase(CTOfflineMasterData):
    """
    Base class for handling a list of Dataset Characteristics.
    Used by EbasIO (without db context) and
    EbasDomDCList (with db context) - client classes

    A client class must feature following functionality:
     - list type (implement __item__ and __iter__ and append)
     - provide a class atrribute CLIENT_CLASS_ELEMENTS
    """
    # Needs to be set by client class.
    CLIENT_CLASS_ELEMENTS = None
    def __getitem__(self, name):
        """
        Needs to be implemented by client class.
        """
        raise NotImplementedError
    def __iter__(self):
        """
        Needs to be implemented by client class.
        """
        raise NotImplementedError
    def append(self, elem):
        """
        Needs to be implemented by client class.
        """
        raise NotImplementedError

    def sorted(self):
        """
        Sorts list of dc objects according to metadata sort order.
        Parameters:
            None
        Returns:
            generator: sorted list of objects
        """
        for ret in self.sorted_order():
            yield ret[1]

    def sorted_order(self):
        """
        Sorts list of dc objects according to metadata sort order and yields
        sortorder number and list element as tuples.
        Parameters:
            dc_list   list of dataset characteristics
        Returns:
            generator: sorted list of tuples (ordernumber, object)
        """
        return sorted([(self.META['SORTORDER'].index(k.CT_TYPE) \
                           if k.CT_TYPE in self.META['SORTORDER'] \
                            else 999,
                        k) for k in self])

    def as_str(self):
        """
        Generates a single string from a sorted list of DC.
        Parameters:
            None
        Returns:
            str comma separated, tag=value
        """
        return ", ".join(["{}={}".format(dc_.CT_TYPE, dc_.value_string())
                          for dc_ in self.sorted()])

    def as_dict(self):
        """
        Generates a single dictionary from a list of DC.
        The dictionary is constructed as CT_TYPE: CT_VAL_xxx pairs
        Parameters:
            list of dc objects
        Returns:
            dictionary
        """
        ret = {}
        for dc_ in self:
            if dc_.CT_DATATYPE == 'CHR':
                ret[dc_.CT_TYPE] = dc_.DC_VAL_CHR
            elif dc_.CT_DATATYPE == 'INT':
                ret[dc_.CT_TYPE] = dc_.DC_VAL_INT
            else:
                ret[dc_.CT_TYPE] = dc_.DC_VAL_DBL
        return ret

    def dc_by_ct_type(self, ct_type):
        """
        Get a dc objetc from the list by CT_TYPE
        Parameters:
            ct_type    ct_type for lookup
        Returns:
            DCBase object or None
        """
        for dc_ in self:
            if dc_.CT_TYPE == ct_type:
                return dc_
        return None

    def add_parse(self, ct_type, value, ft_type, co_comp_name, data_level=None):
        """
        Adds a new object by parsing a DC tag=value pair.
        Calls element classes parse method.
        Used for parsing and validity check without db connection (e.g. in
        nasa ames parsing)
        Parameters:
            ct_type       characteristics type (tag name)
            value         characteristics value, string including unit if needed
            ft_type       ft_type of the dataset
                          used for validity checks
            co_comp_name  compornent name of the dataset
                          used for validity checks
            data_level    data level, for exceptional DC (lev0 exceptions)
        Returns:
            None
        Raises:
            DCError, DCWarning
        """
        try:
            charac = self.__class__.CLIENT_CLASS_ELEMENTS.parse(
                ct_type, value, ft_type, co_comp_name, data_level=data_level)
        except DCWarning as excpt:
            if excpt.ret:
                self.append(excpt.ret)
            raise excpt

        # check if characteristic exists already:
        exist = 0
        for old in self:
            if old.CT_TYPE == charac.CT_TYPE:
                if old == charac and exist != 0:
                    exist = -1
                else:
                    exist = 1
        if exist == -1:
            self.append(charac)
            raise DCWarning(
                "multiple identical definitions for {}".format(ct_type))
        if exist == 1:
            raise DCError(
                "multiple different definitions for {}".format(ct_type))
        self.append(charac)

    def add(self, ct_type, value, ft_type, co_comp_name, data_level=None):
        """
        Add a new object to the list.
        Parameters:
            ct_type       characteristics type (tag name)
            value         characteristics value, string including unit if needed
            ft_type       ft_type of the dataset
                          used for validity checks
            co_comp_name  compornent name of the dataset
                          used for validity checks
            data_level    data level, for exceptional DC (lev0 exceptions)
        Returns:
            None
        Raises:
            DCError, DCWarning
        """
        charac = self.__class__.CLIENT_CLASS_ELEMENTS(
            self.__class__.CLIENT_CLASS_ELEMENTS.setup_dict(
                ct_type, value, ft_type, co_comp_name, data_level=data_level))
        charac.__dict__['data_level'] = data_level
        charac.check()
        # check if characteristic exists already:
        exist = 0
        for old in self:
            if old.CT_TYPE == ct_type:
                if old == charac and exist != 0:
                    exist = -1
                else:
                    exist = 1
        if exist == -1:
            raise DCWarning(
                "multiple identical definitions for {}".format(ct_type))
        if exist == 1:
            raise DCError(
                "multiple different definitions for {}".format(ct_type))
        self.append(charac)

    def delete_dc(self, ct_type):
        """
        Remove a characteristic from the list
        Parameters:
            ct_type       characteristics type (tag name)
        Returns:
            None
        """
        for i, char in reversed(list(enumerate(self))):
            if char.CT_TYPE == ct_type:
                del self[i]

class DCBase(CTOfflineMasterData):
    """
    Base class for handling Dataset Characteristics.
    Used by nasa_ames.dataset_characteristic (without db context) and
    ebas.domain.dc (with db context) - client classes

    A client class must feature following functionality:
     - attribute access to data elements e.g. obj.CT_TYPE == __getattr__
     - key access to data elements e.g. obj['DC_VAL_INT'] == __item__
     - iteration over keys == __iter__
    All tree are implemented with classes based on DataObject (used in
    ebas.nasa_ames) and classes based on EbasDomainDictBase (used in
    ebas.domain.dc)
    """

    # some hardcoded exceptional components (lev 0 exceptions):
    CT_EXCEPTIONAL = {
        "0": {
            # aps lev0:
            'Size bin side scatter': {
                'CT_TYPE': 'Size bin side scatter',
                'CT_DATATYPE': 'DBL',
                'CT_SEQ': 20,
                'CT_UNIT': None,
                },
            'Size bin aerodynamic': {
                'CT_TYPE': 'Size bin aerodynamic',
                'CT_DATATYPE': 'DBL',
                'CT_SEQ': 20,
                'CT_UNIT': None,
                },
            # dmps lev 0:
            'Size bin': {
                'CT_TYPE': 'Size bin',
                'CT_DATATYPE': 'INT',
                'CT_SEQ': 20,
                'CT_UNIT': None,
                },
            # ccnc lev 0:
            'Actual/target': {
                'CT_TYPE': 'Actual/target',
                'CT_DATATYPE': 'CHR',
                'CT_SEQ': 20,
                'CT_UNIT': None,
                },
            # cpc lev 0:
            # online_gc lev 0:
            'Nominal/measured': {
                'CT_TYPE': 'Nominal/measured',
                'CT_DATATYPE': 'CHR',
                'CT_SEQ': 20,
                'CT_UNIT': None,
                },
            # cloud_light_scattering_photometer:
            'Channel': {
                'CT_TYPE': 'Channel',
                'CT_DATATYPE': 'INT',
                'CT_SEQ': 20,
                'CT_UNIT': None,
                },
            # PTR-MS lev0
            'k': {
                'CT_TYPE': 'k',
                'CT_DATATYPE': 'DBL',
                'CT_SEQ': 20,
                'CT_UNIT': None,
                },
            'XR': {
                'CT_TYPE': 'XR',
                'CT_DATATYPE': 'DBL',
                'CT_SEQ': 21,
                'CT_UNIT': None,
                },
            'accuracy': {
                'CT_TYPE': 'accuracy',
                'CT_DATATYPE': 'DBL',
                'CT_SEQ': 21,
                'CT_UNIT': '%',
                },
            'dwell_time': {
                'CT_TYPE': 'dwell_time',
                'CT_DATATYPE': 'DBL',
                'CT_SEQ': 22,
                'CT_UNIT': 's',
                },
            'background_method': {
                'CT_TYPE': 'background_method',
                'CT_DATATYPE': 'CHR',
                'CT_SEQ': 23,
                'CT_UNIT': None,
                },
            'calibration_method': {
                'CT_TYPE': 'calibration_method',
                'CT_DATATYPE': 'CHR',
                'CT_SEQ': 24,
                'CT_UNIT': None,
                },
            },
        }
    CV_EXCEPTIONAL = {
        "0": [
            # ACSM lev 0:
            ('Reference component', 'aerosol_mass_spectrometer',
             'ionization_efficiency'),
            ('Reference component', 'aerosol_mass_spectrometer',
             'relative_ionization_efficiency'),
            ('Location', 'aerosol_mass_spectrometer',
             'relative_humidity'),
            ('Location', 'aerosol_mass_spectrometer',
             'electric_tension'),
            ('Location', 'aerosol_mass_spectrometer',
             'electric_current'),
            ('Location', 'aerosol_mass_spectrometer',
             'flow_rate'),
            ('Location', 'aerosol_mass_spectrometer',
             'frequency'),
            ('Location', 'aerosol_mass_spectrometer',
             'electric_power'),
            ('Status type', 'aerosol_mass_spectrometer',
             'status'),
            # aps lev0:
            ('Status type', 'aps', 'status'),
            ('Size bin', 'aps', 'particle counts'),
            ('Size bin side scatter', 'aps', 'particle counts'),
            ('Size bin aerodynamic', 'aps', 'particle counts'),
            ('Dmin', 'aps', 'particle counts'),
            ('Dmax', 'aps', 'particle counts'),
            ('Location', 'aps', 'flow_rate'),
            ('Location', 'aps', 'electric_current'),
            ('Location', 'aps', 'electric_tension'),
            ('Location', 'aps', 'digital_input'),
            # dmps lev 0:
            ('Size bin', 'dmps', 'particle_diameter'),
            ('Size bin', 'dmps', 'particle_number_concentration'),
            ('Size bin', 'smps', 'particle_diameter'),
            ('Size bin', 'smps', 'particle_number_concentration'),
            ('Size bin', 'v-smps', 'particle_diameter'),
            ('Size bin', 'v-smps', 'particle_number_concentration'),
            ('Wavelength', 'filter_absorption_photometer',
                'equivalent_black_carbon_loading'),
            # filter_absorption_photometer (AE31) lev0:
            ('Location', 'filter_absorption_photometer',
                'sensing_beam_signal'),
            ('Location', 'filter_absorption_photometer',
                'equivalent_black_carbon'),
            ('Location', 'filter_absorption_photometer',
                'attenuation_coefficient'),
            ('Wavelength', 'filter_absorption_photometer',
                'filter_loading_compensation_parameter'),
            # neph lev0
            ('Location', 'nephelometer', 'flow_rate'),
            ('Wavelength', 'nephelometer',
             'aerosol_light_scattering_coefficient_zero_measurement'),
            ('Wavelength', 'nephelometer',
             'aerosol_light_backscattering_coefficient_zero_measurement'),
            ('Wavelength', 'nephelometer',
             'aerosol_light_rayleighscattering_coefficient_zero_measurement'),
            # neph lev0: special case for humidified neph measurements (NOAA)
            # here, two nephs are used (one dry ref and one humidified)
            # the scattering/backscattering data get a Location element
            # containing RefNeph or WetNeph
            ('Location', 'nephelometer', 'aerosol_light_scattering_coefficient'),
            ('Location', 'nephelometer', 'aerosol_light_backscattering_coefficient'),
            # CCNC lev 0:
            ('Actual/target', 'CCNC', 'supersaturation'),
            ('Actual/target', 'CCNC', 'temperature_gradient'),
            ('Actual/target', 'CCNC', 'temperature'),
            ('Actual/target', 'CCNC', 'flow_rate'),
            ('Actual/target', 'CCNC', 'electric_tension'),
            ('Location', 'CCNC', 'flow_rate'),
            ('Location', 'CCNC', 'electric_current'),
            ('Location', 'CCNC', 'electric_tension'),
            ('Status type', 'CCNC', 'status'),
            # cpc lev0:
            ('Nominal/measured', 'cpc', 'flow_rate'),
            ('Location', 'cpc', 'pulse_width'),

            # DMPS-CCNC lev 0:
            ('Actual/target', 'DMPS-CCNC', 'supersaturation'),
            ('Actual/target', 'DMPS-CCNC', 'temperature_gradient'),
            ('Actual/target', 'DMPS-CCNC', 'temperature'),
            ('Actual/target', 'DMPS-CCNC', 'flow_rate'),
            ('Actual/target', 'DMPS-CCNC', 'electric_tension'),
            ('Location', 'DMPS-CCNC', 'flow_rate'),
            ('Location', 'DMPS-CCNC', 'electric_current'),
            ('Location', 'DMPS-CCNC', 'electric_tension'),
            ('Status type', 'DMPS-CCNC', 'status'),

            # NOx lev0
            ('Status type', 'chemiluminescence_photolytic', 'status'),
            ('Status type', 'chemiluminescence_molybdenum', 'status'),
            ('Status type', 'chemiluminescence_photometer', 'status'),

            # VOC lev0:
            ('Status type', 'online_gc', 'status'),
            # Additional exceptions (Nominal/measured) depend on IP table
            # (all components). See below.

            # PTR-MS lev0
            ('Status type', 'PTR-MS', 'status'),
            ('Location', 'PTR-MS', 'electric_tension'),

            # cloud_light_scattering_photometer
            ('Channel', 'cloud_light_scattering_photometer', 'electric_tension'),
        ]}

    # online_gc, add for all components:
    EMI = EbasMasterIP()
    for ip_ in EMI:
        if ip_['RE_REGIME_CODE'] == 'IMG' and ip_['FT_TYPE'] == 'online_gc':
            CV_EXCEPTIONAL["0"].append(
                ('Nominal/measured', 'online_gc', ip_['CO_COMP_NAME']))

    # PTR-MS, add for all components:
    EMI = EbasMasterIP()
    for comp in PTR_MS_COMP:
        CV_EXCEPTIONAL["0"].append(('k', 'PTR-MS', comp))
        CV_EXCEPTIONAL["0"].append(('XR', 'PTR-MS', comp))
        CV_EXCEPTIONAL["0"].append(('accuracy', 'PTR-MS', comp))
        CV_EXCEPTIONAL["0"].append(('dwell_time', 'PTR-MS', comp))
        CV_EXCEPTIONAL["0"].append(('background_method', 'PTR-MS', comp))
        CV_EXCEPTIONAL["0"].append(('calibration_method', 'PTR-MS', comp))


    # Problem: for checking validity of DC values without DB connection, we
    # need an offline store of valid CT and CV data.
    # read offline masterdata for DC (dataset characteristics methods)
    # Those are fallback values, will be read from database if possible.
    CTOfflineMasterData.read_pickle_file()

    # must be implemented by derived classes:
    def __getattr__(self, name):
        raise NotImplementedError
    def __getitem__(self, name):
        raise NotImplementedError
    def __iter__(self):
        raise NotImplementedError

    def __lt__(self, other):
        """
        Less then operator method.
        Needed in py3 for sorting: DCList.sorted_order()
        Parameters:
            other   compare object
        Returns:
            Bool
        """
        return self.tuple() < other.tuple()

    def __init__(self, dbh):
        """
        Read cached ct masterdata if dbh is provided.
        """
        CTOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    @classmethod
    def get_ct(cls, ct_type, data_level=None):
        """
        Get the correct CT metadata element (regular or exceptional (if
        data_level is specified)).
        Parameters:
            ct_type       characteristics type (tag name)
            data_level    data level, for exceptional DC (lev0 exceptions)
        Returns:
            ct masterdata
        Raises:
            DCError if not found
        """
        data_level = base_datalevel(data_level)
        ct_ = None
        try:
            ct_ = cls.META['CHARACTERISTICS'][ct_type]
        except KeyError:
            try:
                if data_level is not None:
                    ct_ = cls.CT_EXCEPTIONAL[data_level][ct_type]
            except KeyError:
                pass
        if ct_ is None:
            raise DCError("unknown metadata element '{}'".format(ct_type))
            # wording needs to be 'metadata element' because misspelled
            # metadata elements will also end up here in characteristics
            # when reading a NasaAmes file
        return ct_

    @classmethod
    def validate_ct(cls, ct_type, data_level=None):
        """
        Check if ct_type is a characteristic at all.
        Parameters:
            ct_type       characteristics type (tag name)
            data_level    data level, for exceptional DC (lev0 exceptions)
        Returns:
            None
        Raises:
            DCError if not valid
        """
        data_level = base_datalevel(data_level)
        if ct_type not in cls.META['CHARACTERISTICS']:
            if data_level is None or \
               data_level not in cls.CT_EXCEPTIONAL or \
               ct_type not in cls.CT_EXCEPTIONAL[data_level]:
                raise DCError("unknown metadata element '{}'".format(ct_type))

    @classmethod
    def validate_cv(cls, ct_type, ft_type, co_comp_name, data_level=None):
        """
        Check if characteristic is valid for ft_type and co_comp_name.
        Parameters:
            ct_type       characteristics type (tag name)
            ft_type       ft_type of the dataset
            co_comp_name  compornent name of the dataset
            data_level    data level, for exceptional DC (lev0 exceptions)
        Returns:
            None
        Raises:
            DCError if not valid
        """
        data_level = base_datalevel(data_level)
        if (ct_type, ft_type, co_comp_name) not in cls.META['VALIDITY']:
            if data_level is None or \
               data_level not in cls.CV_EXCEPTIONAL or \
               (ct_type, ft_type, co_comp_name) not in \
               cls.CV_EXCEPTIONAL[data_level]:
                raise DCError(
                    "illegal metadata element '{}' for instrument '{}' and "
                    "component '{}'".format(ct_type, ft_type, co_comp_name))

    @classmethod
    def parse(cls, ct_type, value, ft_type, co_comp_name, data_level=None):
        # pylint: disable-msg=R0913
        # R0913: Too many arguments
        """
        Factory method. Creates a new object by parsing a DC tag=value pair.
        Check for validity.
        Used for parsing and validity check without db connection (e.g. in
        nasa ames parsing)
        Parameters:
            ct_type       characteristics type (tag name)
            value         characteristics value, string including unit if needed
            ft_type       ft_type of the dataset
                          used for validity checks
            co_comp_name  compornent name of the dataset
                          used for validity checks
            data_level    data level, for exceptional DC (lev0 exceptions)
        Returns:
            new DatasetCharacteristic object
        Raises:
            DCError
        """
        ct_ = cls.get_ct(ct_type, data_level=data_level)
        unit = ct_['CT_UNIT']
        if unit is not None:
            # this value needs the unit appended
            if not value.endswith(unit):
                raise DCError('metadata value {}: missing unit ({})'.
                              format(ct_type, unit))
            value = value[:-len(unit)].strip()
        dc_dict = cls.setup_dict(ct_type, value, ft_type, co_comp_name,
                                 data_level=data_level)
        obj = cls(dc_dict)
        obj.__dict__['data_level'] = data_level
        dependencies = []
        if ft_type is None:
            dependencies.append("instrument type")
        if co_comp_name is None:
            dependencies.append("component name")
        if dependencies:
            raise DCWarning(
                'metadata element {} could not be checked for validity because '
                '{} is not specified correctly'
                .format(ct_type, ' and '.join(dependencies)), obj)
        else:
            obj.check()
        return obj

    @classmethod
    def setup_dict(cls, ct_type, value, ft_type, co_comp_name, data_level=None):
        # pylint: disable-msg=R0913
        # R0913: Too many arguments
        """
        Setup a correct data dictionary from base attributes.
        Used for both parsing (e.g. in nasa ames) and object creation for domain
        Parameters:
            ct_type       characteristics type (tag name)
            value         characteristics value (may still be string, but
                          without unit)
            ft_type       ft_type of the dataset
                          used for validity checks
            co_comp_name  compornent name of the dataset
                          used for validity checks
            data_level    data level, for exceptional DC (lev0 exceptions)
        Returns:
            new DatasetCharacteristic object
        Raises:
            DCError
        """
        dc_dict = \
            {
                'CT_TYPE': ct_type,
                'FT_TYPE': ft_type,
                'CO_COMP_NAME': co_comp_name
            }
        ct_ = cls.get_ct(ct_type, data_level=data_level)
        ct_datatype = ct_['CT_DATATYPE']
        dc_dict['CT_DATATYPE'] = ct_datatype
        if ct_datatype == 'INT':
            try:
                value = int(value)
            except ValueError:
                raise DCError('metadata value {}: must be type int'.
                              format(ct_type))
        if ct_datatype == 'DBL':
            try:
                value = float(value)
            except ValueError:
                raise DCError('metadata value {}: must be type float'.
                              format(ct_type))
        dc_dict['DC_VAL_' + str(ct_datatype)] = value
        return dc_dict

    def check(self):
        """
        Checks the object for validity.
        Raises:
            DCError
        """
        # get data_level, only is object has been set up with data_level
        # i.e. with parse(), else data_level is ignored and no exceptional
        # CT will be accepted
        data_level = None
        if 'data_level' in self.__dict__:
            data_level = self.data_level
        ct_ = self.get_ct(self.CT_TYPE, data_level=data_level)
        self.validate_cv(self.CT_TYPE, self.FT_TYPE, self.CO_COMP_NAME,
                         data_level=data_level)
        
        if ct_['CT_DATATYPE'] != self.CT_DATATYPE:
            raise DCError("metadata element '{}' must be {}, not {}".format(
                self.CT_TYPE, ct_['CT_DATATYPE'], self.CT_DATATYPE))
        # The following are internal coding errors: raise TypeError
        if (self.CT_DATATYPE == 'INT' and \
            ('DC_VAL_INT' not in self or self.DC_VAL_INT is None)) or \
           (self.CT_DATATYPE == 'DBL' and
            ('DC_VAL_DBL' not in self or self.DC_VAL_DBL is None)) or \
           (self.CT_DATATYPE == 'CHR' and
            ('DC_VAL_CHR' not in self or self.DC_VAL_CHR is None)):
            raise TypeError("metadata element '{}': {} ".
                            format(self.CT_TYPE, self.CT_DATATYPE) +
                            'value must be provided')
        if (self.CT_DATATYPE == 'INT' and \
            (('DC_VAL_DBL' in self and self.DC_VAL_DBL != None) or \
             ('DC_VAL_CHR' in self  and self.DC_VAL_CHR != None))) or \
           (self.CT_DATATYPE == 'DBL' and
            (('DC_VAL_INT' in self and self.DC_VAL_INT != None) or \
             ('DC_VAL_CHR' in self  and self.DC_VAL_CHR != None))) or \
           (self.CT_DATATYPE == 'CHR' and
            (('DC_VAL_INT' in self and self.DC_VAL_INT != None) or \
             ('DC_VAL_DBL' in self  and self.DC_VAL_DBL != None))):
            raise TypeError("metadata element '{}': ".format(self.CT_TYPE) +\
                          'multiple values with different datatypes')

    def tuple(self):
        """
        Generates a tag/value tuple.
        Parameters:
            None
        Returns:
            value tuple for a characteristic (<tag>, <value>[, <unit>])
        """
        # get data_level, only is object has been set up with data_level
        # i.e. with parse(), else data_level is ignored and no exceptional
        # CT will be accepted
        data_level = None
        if 'data_level' in self.__dict__:
            data_level = self.data_level
        ct_ = self.get_ct(self.CT_TYPE, data_level=data_level)
        return (self.CT_TYPE, self['DC_VAL_' + self.CT_DATATYPE], ct_['CT_UNIT'])

    @property
    def value(self):
        """
        Get the value for a DC.
        Parameters:
            None
        Returns:
            value
        """
        return self['DC_VAL_' + self.CT_DATATYPE]

    @property
    def unit(self):
        """
        Get the unit for a DC.
        Parameters:
            None
        Returns:
            unit
        """
        # get data_level, only is object has been set up with data_level
        # i.e. with parse(), else data_level is ignored and no exceptional
        # CT will be accepted
        data_level = None
        if 'data_level' in self.__dict__:
            data_level = self.data_level
        ct_ = self.get_ct(self.CT_TYPE, data_level=data_level)
        if ct_['CT_UNIT']:
            return ct_['CT_UNIT']
        return None

    def value_string(self):
        """
        Generates a value string ("<value> <unit>") that can be used for output.
        Parameters:
            None
        Returns:
            value string
        """
        ret = "{}".format(self.value)
        if self.unit is not None:
            ret += ' ' + self.unit
        return ret
