"""
$Id: ip.py 2660 2021-06-02 10:00:04Z pe $

EBAS Masterdata Class for instrument/parameter validity
"""

from .offline_masterdata import IPOfflineMasterData
from .base import EbasMasterBase
from .pg_pl import EbasMasterPL
from .co import PTR_MS_COMP

def _exceptions():
    """
    Generate dictionary for exceptions (special datalevels, not imported but
    should be just file format checked.
    Parameters:
        None
    Returns:
        exception dict
    """
    exceptions = {'0': {}, '1': {}}

    # ACSM lev0:
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'pm1_non_refractory',
        'collection_efficiency')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'pm1_non_refractory',
            'CO_COMP_NAME': 'collection_efficiency'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'pm1_non_refractory',
        'relative_ionization_efficiency')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'pm1_non_refractory',
            'CO_COMP_NAME': 'relative_ionization_efficiency'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'pm1_non_refractory',
        'nitrogen_ion_flow_signal')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'pm1_non_refractory',
            'CO_COMP_NAME': 'nitrogen_ion_flow_signal'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'pm1_non_refractory',
        'ionization_efficiency')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'pm1_non_refractory',
            'CO_COMP_NAME': 'ionization_efficiency'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'pm25_non_refractory',
        'collection_efficiency')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'pm25_non_refractory',
            'CO_COMP_NAME': 'collection_efficiency'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'pm25_non_refractory',
        'relative_ionization_efficiency')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'pm25_non_refractory',
            'CO_COMP_NAME': 'relative_ionization_efficiency'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'pm25_non_refractory',
        'nitrogen_ion_flow_signal')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'pm25_non_refractory',
            'CO_COMP_NAME': 'nitrogen_ion_flow_signal'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'pm25_non_refractory',
        'ionization_efficiency')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'pm25_non_refractory',
            'CO_COMP_NAME': 'ionization_efficiency'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'pressure')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'pressure'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'temperature')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'temperature'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'relative_humidity')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'relative_humidity'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'pressure')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'pressure'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'temperature')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'temperature'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'relative_humidity')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'relative_humidity'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'electric_tension')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'electric_tension'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'electric_current')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'electric_current'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'electric_power')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'electric_power'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'airbeam_signal')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'airbeam_signal'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'flow_rate')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'flow_rate'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'frequency')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'frequency'
        }
    exceptions['0'][('aerosol_mass_spectrometer', 'IMG', 'instrument',
        'status')] = {
            'FT_TYPE': 'aerosol_mass_spectrometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'status'
        }
    # NOX lev 0
    basedict = {
        'RE_REGIME_CODE': 'IMG',
        'MA_MATRIX_NAME': 'air',
    }
    for ft_ in ('chemiluminescence_photolytic',
                'chemiluminescence_molybdenum',
                'chemiluminescence_photometer'):
        for co_ in ('NO_#counts', 'NO_converter_#counts',
                    'NO_sensitivity', 'converter_efficiency'):
            dict_ = basedict.copy()
            dict_.update({'FT_TYPE': ft_, 'CO_COMP_NAME': co_})
            exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
                 dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_
        basedict['MA_MATRIX_NAME'] = 'instrument'
        dict_ = basedict.copy()
        dict_.update({'FT_TYPE': ft_, 'CO_COMP_NAME': 'status'})
        exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
             dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_


    # xMPS lev0:
    basedict = {
        'RE_REGIME_CODE': 'IMG',
    }
    for ft_ in ('dmps', 'smps', 'tdmps', 'tsmps', 'v-smps', 'v-tdmps'):
        for comb in (('flow_rate', ('instrument',)),
                     ('status', ('instrument',)),
                     ('particle_number_concentration',
                         ('pm1', 'pm10', 'aerosol',)),
                     ('particle_diameter', ('pm1', 'pm10', 'aerosol'))):
            for ma_ in comb[1]:
                dict_ = basedict.copy()
                dict_.update({'FT_TYPE': ft_, 'CO_COMP_NAME': comb[0],
                              'MA_MATRIX_NAME': ma_})
                exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
                     dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_
    for ft_ in ('v-smps', 'v-tdmps'):
        for comb in (('flow_rate', ('instrument',)),
                     ('status', ('instrument',)),
                     ('particle_number_concentration',
                         ('pm10_non_volatile',)),
                     ('particle_diameter', ('pm10_non_volatile',))):
            for ma_ in comb[1]:
                dict_ = basedict.copy()
                dict_.update({'FT_TYPE': ft_, 'CO_COMP_NAME': comb[0],
                              'MA_MATRIX_NAME': ma_})
                exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
                     dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_

    # filter_absorption_photometer lev 0 (AE33):
    basedict = {
        'RE_REGIME_CODE': 'IMG',
        'FT_TYPE': 'filter_absorption_photometer',
    }
    for comb in (('flow_rate', ('instrument',)),
                 ('status', ('instrument',)),
                 ('filter_number', ('instrument',)),
                 ('sample_length_on_filter', ('instrument',)),
                 ('equivalent_black_carbon_loading', ('pm1', 'pm10', 'pm25', 'aerosol')),
                 ('biomass_burning_aerosol_fraction', ('pm1', 'pm10', 'pm25', 'aerosol')),
                 ('filter_loading_compensation_parameter', ('pm1', 'pm10', 'pm25', 'aerosol')),
                 ('reference_beam_signal', ('pm1', 'pm10', 'pm25', 'aerosol')),
                 ('sensing_beam_signal', ('pm1', 'pm10', 'pm25', 'aerosol')),
                 ('transmittance', ('pm1', 'pm10', 'pm25', 'aerosol')),
                 ('sample_intensity', ('pm1', 'pm10', 'pm25', 'aerosol')),
                 ('reference_intensity', ('pm1', 'pm10', 'pm25', 'aerosol')),
                 ):
        for ma_ in comb[1]:
            dict_ = basedict.copy()
            dict_.update({'CO_COMP_NAME': comb[0], 'MA_MATRIX_NAME': ma_})
            exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
                 dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_

    # CCNC lev0:
    basedict = {
        'RE_REGIME_CODE': 'IMG',
        'MA_MATRIX_NAME': 'instrument',
    }
    for comp in ('supersaturation', 'temperature_gradient', 'flow_rate',
                 'electric_current', 'electric_tension', 'status'):
        for inst in ('CCNC', 'DMPS-CCNC'):
            dict_ = basedict.copy()
            dict_.update({'CO_COMP_NAME': comp, 'FT_TYPE': inst})
            exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
                 dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_
    # DMPS-CCNC only:
    basedict = {
        'RE_REGIME_CODE': 'IMG',
        'MA_MATRIX_NAME': 'pm10',
    }
    for comp in ('particle_diameter',
                 'cloud_condensation_nuclei_number_concentration'):
        dict_ = basedict.copy()
        dict_.update({'CO_COMP_NAME': comp, 'FT_TYPE': 'DMPS-CCNC'})
        exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
             dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_

    # CCNC lev1:
    basedict = {
        'RE_REGIME_CODE': 'IMG',
        'MA_MATRIX_NAME': 'instrument',
        'CO_COMP_NAME': 'supersaturation',
    }
    for ft_ in ('CCNC', 'DMPS-CCNC'):
        dict_ = basedict.copy()
        dict_.update({'FT_TYPE': ft_})
        exceptions['1'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
             dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_

    # nephelometer lev0
    basedict = {
        'RE_REGIME_CODE': 'IMG',
        'FT_TYPE': 'nephelometer',
    }
    for comb in (
        ('flow_rate', ('instrument',)),
        ('electric_tension', ('instrument',)),
        ('electric_current', ('instrument',)),
        ('status', ('instrument',)),
        ('aerosol_light_scattering_coefficient_zero_measurement',
         ('pm1', 'pm10', 'aerosol',)),
        ('aerosol_light_backscattering_coefficient_zero_measurement',
         ('pm1', 'pm10', 'aerosol',)),
        ('aerosol_light_rayleighscattering_coefficient_zero_measurement',
         ('pm1', 'pm10', 'aerosol',)),
       ):
        for ma_ in comb[1]:
            dict_ = basedict.copy()
            dict_.update({'CO_COMP_NAME': comb[0], 'MA_MATRIX_NAME': ma_})
            exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
                 dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_

    # cpc lev0:
    basedict = {
        'FT_TYPE': 'cpc',
        'RE_REGIME_CODE': 'IMG',
        'MA_MATRIX_NAME': 'instrument',
    }
    for comp in ('flow_rate', 'pulse_width'):
        dict_ = basedict.copy()
        dict_['CO_COMP_NAME'] = comp
        exceptions['0'][(dict_['FT_TYPE'], dict_['RE_REGIME_CODE'],
             dict_['MA_MATRIX_NAME'], dict_['CO_COMP_NAME'])] = dict_

    # VOC lev0:
    pl_ = EbasMasterPL()
    for comp in [x.CO_COMP_NAME for x in pl_.META['VOC']]:
        for ext in ('_peak_area', '_peak_width', '_retention_time'):
            compmod = comp + ext
            exceptions['0'][('online_gc', 'IMG', 'air', compmod)] = {
                'FT_TYPE': 'online_gc',
                'RE_REGIME_CODE': 'IMG',
                'MA_MATRIX_NAME': 'air',
                'CO_COMP_NAME': compmod,
            }
    exceptions['0'][('online_gc', 'IMG', 'instrument', 'status')] = {
        'FT_TYPE': 'online_gc',
        'RE_REGIME_CODE': 'IMG',
        'MA_MATRIX_NAME': 'air',
        'CO_COMP_NAME': 'status',
    }

    # PTR-MS lev0:
    for comp in PTR_MS_COMP:
        exceptions['0'][('PTR-MS', 'IMG', 'air', comp)] = {
            'FT_TYPE': 'PTR-MS',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'air',
            'CO_COMP_NAME': comp,
        }
    for comp in ('status', 'temperature', 'pressure', 'electric_tension'):
        exceptions['0'][('PTR-MS', 'IMG', 'instrument', comp)] = {
            'FT_TYPE': 'PTR-MS',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': comp,
        }
    # cloud_light_scattering_photometer
    exceptions['0'][('cloud_light_scattering_photometer', 'IMG', 'instrument',
        'electric_tension')] = {
            'FT_TYPE': 'cloud_light_scattering_photometer',
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'instrument',
            'CO_COMP_NAME': 'electric_tension',
        }

    # Finally:
    return exceptions

class EbasMasterIP(EbasMasterBase, IPOfflineMasterData):
    """
    Domain Class for Parameter masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling parameter and checking them against master data.
    Parameter master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for IP (parameters)
    # Those are fallback values, will be read from database as soon as possible.
    IPOfflineMasterData.read_pickle_file()
    # some hardcoded exceptional parameters (see method exceptional):
    IP_EXCEPTIONAL = _exceptions()

    def __init__(self, dbh=None):
        """
        Read ip masterdata if dbh is provided.
        """
        IPOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    def __getitem__(self, key):
        """
        Allows dictionary like access to metadata.
        Exception for IP:
            - exceptional metadata lookup (non DB, data level dependent)
        Parameters:
            key    (instr_type, regime, matrix, comp_name, data_level)
                   Only the first 4 are used for regular lookup!
                   data_level is optional and is used for finding exceptional
                   data level dependent masterdata
        """
        # first try: use regular masterdata, ignore data level
        try:
            return self.__class__.META[key[:4]]
        except KeyError:
            # don't exist: try exceptional masterdata (needs data level)
            # Those masterdata are NOT defined in the database, but might be
            # used e.g. in lev 0 files.
            # Thus they are accepted when reading the file, but the domain
            # layer will issue an error message.
            if len(key) != 5:
                raise
            data_level = key[4]
            if data_level in ('0a', '0b'):
                data_level = '0'
            return self.__class__.IP_EXCEPTIONAL[data_level][key[:4]]
