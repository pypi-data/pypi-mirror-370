"""
ebas/domain/masterdata/pm.py
$Id: pm.py 2789 2022-03-18 12:42:26Z pe $

EBAS Masterdata Class for parameter masterdata

This module implements the class EbasMasterPM.

History:
V.1.0.0  2014-10-06  pe  initial version

"""

from .offline_masterdata import PMOfflineMasterData
from .base import EbasMasterBase
from .sc import EbasMasterSC
from .pg_pl import EbasMasterPL
from .co import PTR_MS_COMP
from nilutility.datatypes import DataObject

def _list_matrix_group(PM_META, regime, group, comp_name):
    """
    list all matrices within the group for which the regime and component
    are defined.
    This is used for mangling different unit on export conversions.
    See _exceptions_unit_exp above and
    ebas/domain/basic_domain_logic/unit_convert.py

    This method is needed on module level (for _exceptions_unit_exp) and as
    class methoid within EbasMasterPM. Implement here, use it in the class
    method.
    """
    groups = {
        'ALL_AEROSOL': (
            'aerosol', 'pm1', 'pm1_humidified', 'pm1_non_refractory',
            'pm25', 'pm25_humidified', 'pm25_volatile', 'pm25_non_volatile',
            'pm10', 'pm10_humidified', 'pm10_volatile', 'pm10_non_volatile',
            'pm10_pm1', 'pm10_pm25',
            'pm_eq25', 'pm_eq35', 'pm_eq50', 'pm_eq75')}
    mats = [x[1] for x in PM_META.keys()
            if x[0] == regime and x[2] == comp_name and
                x[1] in groups[group]]
    return mats


class _ProtoEbasMasterPM(EbasMasterBase, PMOfflineMasterData):
    """
    Helper class, just to get the initialisation of the class right...
    Especially the initialisation og the class member PM_EXCEPTIONALUNIT_EXP
    as it depends on anouther class member (META) which is initialized in
    read_pickle_file()
    We could use a metaclass for this (as well as for reading from the pickle
    file in PMOfflineMasterData)?
    Think this easier concept is better...
    """
    @classmethod
    def _exceptions(cls):
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
        exceptions['0'][('IMG', 'pm1_non_refractory', 'collection_efficiency')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'pm1_non_refractory',
                    'CO_COMP_NAME': 'collection_efficiency',
                    'PM_UNIT': 'no unit',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'pm25_non_refractory', 'collection_efficiency')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'pm25_non_refractory',
                    'CO_COMP_NAME': 'collection_efficiency',
                    'PM_UNIT': 'no unit',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'pm1_non_refractory',
                         'nitrogen_ion_flow_signal')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'pm1_non_refractory',
                    'CO_COMP_NAME': 'nitrogen_ion_flow_signal',
                    'PM_UNIT': 'A',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'pm25_non_refractory',
                         'nitrogen_ion_flow_signal')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'pm25_non_refractory',
                    'CO_COMP_NAME': 'nitrogen_ion_flow_signal',
                    'PM_UNIT': 'A',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        # TODO: nitrogen_ion_flow_signal or airbeam_signal? I think it's the same...
        exceptions['0'][('IMG', 'instrument',
                         'airbeam_signal')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'instrument',
                    'CO_COMP_NAME': 'airbeam_signal',
                    'PM_UNIT': 'A',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'instrument',
                         'frequency')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'instrument',
                    'CO_COMP_NAME': 'frequency',
                    'PM_UNIT': 'Hz',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'instrument',
                         'electric_power')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'instrument',
                    'CO_COMP_NAME': 'electric_power',
                    'PM_UNIT': 'W',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'pm1_non_refractory',
                         'ionization_efficiency')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'pm1_non_refractory',
                    'CO_COMP_NAME': 'ionization_efficiency',
                    'PM_UNIT': 'A/ug/m3',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'pm25_non_refractory',
                         'ionization_efficiency')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'pm25_non_refractory',
                    'CO_COMP_NAME': 'ionization_efficiency',
                    'PM_UNIT': 'A/ug/m3',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'pm1_non_refractory',
                         'relative_ionization_efficiency')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'pm1_non_refractory',
                    'CO_COMP_NAME': 'relative_ionization_efficiency',
                    'PM_UNIT': 'no unit',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'pm25_non_refractory',
                         'relative_ionization_efficiency')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'pm25_non_refractory',
                    'CO_COMP_NAME': 'relative_ionization_efficiency',
                    'PM_UNIT': 'no unit',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        # NOX lev 0
        basedict = {
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'air',
            'PM_CFNAME': None,
            'PM_CFNAME_OFFICIAL': None,
            'PM_CFUNIT': None,
            'PM_DESC': None,
            'PM_COMMENT': None,
        }
        for comb in (('NO_#counts', 'cps'),
                     ('NO_converter_#counts', 'cps'),
                     ('NO_sensitivity', '(pmol/mol)/cps'),
                     ('converter_efficiency', '%'),
                     ):
            dict_ = basedict.copy()
            dict_.update({'CO_COMP_NAME': comb[0], 'PM_UNIT': comb[1]})
            exceptions['0'][(dict_['RE_REGIME_CODE'], dict_['MA_MATRIX_NAME'],
                             dict_['CO_COMP_NAME'])] = dict_
        basedict['MA_MATRIX_NAME'] = 'instrument'
        dict_ = basedict.copy()
        dict_.update({'CO_COMP_NAME': 'status', 'PM_UNIT': 'no unit'})
        exceptions['0'][(dict_['RE_REGIME_CODE'], dict_['MA_MATRIX_NAME'],
                        dict_['CO_COMP_NAME'])] = dict_
    
        # xMPS lev0:
        basedict = {
            'RE_REGIME_CODE': 'IMG',
            'PM_CFNAME': None,
            'PM_CFNAME_OFFICIAL': None,
            'PM_CFUNIT': None,
            'PM_DESC': None,
            'PM_COMMENT': None,
        }
        for comb in (('flow_rate', 'l/min', ('instrument',)),
                     ('status', 'no_unit', ('instrument',)),
                     ('particle_number_concentration', '1/cm3',
                         ('pm1', 'pm10', 'aerosol','pm10_non_volatile',)),
                     ('particle_diameter', 'um',
                      ('pm1', 'pm10', 'aerosol','pm10_non_volatile',)),
                     ):
            for matrix in comb[2]:
                dict_ = basedict.copy()
                dict_.update({'CO_COMP_NAME': comb[0], 'PM_UNIT': comb[1],
                              'MA_MATRIX_NAME': matrix})
                exceptions['0'][(dict_['RE_REGIME_CODE'], dict_['MA_MATRIX_NAME'],
                                 dict_['CO_COMP_NAME'])] = dict_
    
        # filter_absorption_photometer lev0:
        basedict = {
            'RE_REGIME_CODE': 'IMG',
            'PM_CFNAME': None,
            'PM_CFNAME_OFFICIAL': None,
            'PM_CFUNIT': None,
            'PM_DESC': None,
            'PM_COMMENT': None,
        }
        for comb in (('equivalent_black_carbon_loading', 'ug',
                          ('pm1', 'pm10', 'pm25', 'aerosol',)),
                     ('biomass_burning_aerosol_fraction', '%',
                          ('pm1', 'pm10', 'pm25', 'aerosol',)),
                     ('filter_loading_compensation_parameter', 'no unit',
                          ('pm1', 'pm10', 'pm25', 'aerosol',)),
                     ('reference_beam_signal', 'no unit',
                          ('pm1', 'pm10', 'pm25', 'aerosol',)),
                     ('sensing_beam_signal', 'no unit',
                          ('pm1', 'pm10', 'pm25', 'aerosol',)),
                     ('sample_length_on_filter', 'm', ('instrument',)),
                     ('filter_number', 'no unit', ('instrument',)),
                     ):
            for matrix in comb[2]:
                dict_ = basedict.copy()
                dict_.update({'CO_COMP_NAME': comb[0], 'PM_UNIT': comb[1],
                              'MA_MATRIX_NAME': matrix})
                exceptions['0'][(dict_['RE_REGIME_CODE'], dict_['MA_MATRIX_NAME'],
                                 dict_['CO_COMP_NAME'])] = dict_
        # CCNC lev0:
        exceptions['0'][('IMG', 'instrument', 'supersaturation')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'instrument',
                    'CO_COMP_NAME': 'supersaturation',
                    'PM_UNIT': '%',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        exceptions['0'][('IMG', 'instrument', 'temperature_gradient')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'instrument',
                    'CO_COMP_NAME': 'temperature_gradient',
                    'PM_UNIT': 'K',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
    
        # CCNC lev1:
        exceptions['1'][('IMG', 'instrument', 'supersaturation')] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'instrument',
                    'CO_COMP_NAME': 'supersaturation',
                    'PM_UNIT': '%',
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }
        # cpc lev0:
        basedict = {
            'RE_REGIME_CODE': 'IMG',
            'PM_CFNAME': None,
            'PM_CFNAME_OFFICIAL': None,
            'PM_CFUNIT': None,
            'PM_DESC': None,
            'PM_COMMENT': None,
        }
        for comb in (('flow_rate', 'l/min', ('instrument',)),
                     ('pulse_width', 'us', ('instrument',)),):
            for matrix in comb[2]:
                dict_ = basedict.copy()
                dict_.update({'CO_COMP_NAME': comb[0], 'PM_UNIT': comb[1],
                              'MA_MATRIX_NAME': matrix})
                exceptions['0'][(dict_['RE_REGIME_CODE'], dict_['MA_MATRIX_NAME'],
                                 dict_['CO_COMP_NAME'])] = dict_
    
        # nephelometer lev0
        basedict = {
            'RE_REGIME_CODE': 'IMG',
            'PM_CFNAME': None,
            'PM_CFNAME_OFFICIAL': None,
            'PM_CFUNIT': None,
            'PM_DESC': None,
            'PM_COMMENT': None,
        }
        for comb in (
            ('aerosol_light_scattering_coefficient_zero_measurement', '1/Mm',
             ('pm1', 'pm10', 'aerosol',)),
            ('aerosol_light_backscattering_coefficient_zero_measurement', '1/Mm',
             ('pm1', 'pm10', 'aerosol',)),
            ('aerosol_light_rayleighscattering_coefficient_zero_measurement', '1/Mm',
             ('pm1', 'pm10', 'aerosol',)),
           ):
            for matrix in comb[2]:
                dict_ = basedict.copy()
                dict_.update({'CO_COMP_NAME': comb[0], 'PM_UNIT': comb[1],
                              'MA_MATRIX_NAME': matrix})
                exceptions['0'][(dict_['RE_REGIME_CODE'], dict_['MA_MATRIX_NAME'],
                                 dict_['CO_COMP_NAME'])] = dict_

        # VOC lev0:
        pl_ = EbasMasterPL()
        for comp in [x.CO_COMP_NAME for x in pl_.META['VOC']]:
            for ext in (('_peak_area', 'area_unit'),
                        ('_peak_width', 's'),
                        ('_retention_time', 's')):
                compmod = comp + ext[0]
                exceptions['0'][('IMG', 'air', compmod)] = {
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': compmod,
                    'PM_UNIT': ext[1],
                    'PM_CFNAME': None,
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }

        # PTR-MS lev0
        basedict = {
            'RE_REGIME_CODE': 'IMG',
            'MA_MATRIX_NAME': 'air',
            'PM_UNIT': '1/s',
            'PM_CFNAME': None,
            'PM_CFNAME_OFFICIAL': None,
            'PM_CFUNIT': None,
            'PM_DESC': None,
            'PM_COMMENT': None,
        }
        for comp in PTR_MS_COMP:
            dict_ = basedict.copy()
            dict_['CO_COMP_NAME'] = comp
            exceptions['0'][(dict_['RE_REGIME_CODE'], dict_['MA_MATRIX_NAME'],
                             dict_['CO_COMP_NAME'])] = dict_
        dict_ = basedict.copy()
        dict_.update({
            'CO_COMP_NAME': 'status',
            'MA_MATRIX_NAME': 'instrument',
            'PM_UNIT': 'no unit'
        })
        exceptions['0'][(dict_['RE_REGIME_CODE'], dict_['MA_MATRIX_NAME'],
                        dict_['CO_COMP_NAME'])] = dict_
    
        # Finally...
        cls.PM_EXCEPTIONAL = exceptions

    @classmethod
    def _exceptions_unit_exp(cls):
        """
        Generate dictionary of exceptions for unit conversions.
        We need one exception for each output conversion we do in 
        ebas.domain.basic_domain_logic.unit_convert.output_conv_params()
        
        Parameters:
            None
        Returns:
            exception dict
    
        IMPORTANT: Beacuse some exceptions use the META dict, this method
        needs to be re-run, when EbasMasterPM.META is changed
        e.g. after from_db
        """
        exceptions = {
            ('IMG', 'air', 'nitrogen_monoxide', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'nitrogen_monoxide',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_nitrogen_monoxide_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'nitrogen_dioxide', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'nitrogen_dioxide',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_nitrogen_dioxide_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'NOx', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'NOx',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_nox_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'ammonia', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'ammonia',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_ammonia_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'ammonium', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'aerosol',
                    'CO_COMP_NAME': 'ammonium',
                    'PM_UNIT': 'ug/m3',
                    'PM_CFNAME': 'mass_concentration_of_ammonium_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'hydrochloric_acid', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'hydrochloric_acid',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_hydrochloric_acid_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'nitric_acid', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'nitric_acid',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_nitric_acid_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'nitrous_acid', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'nitrous_acid',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_nitrous_acid_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'nitrous_acid', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'nitrous_acid',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_nitrous_acid_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'sulphur_dioxide', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'sulphur_dioxide',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_sulfur_dioxide_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'ozone', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'ozone',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_ozone_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'ethanal', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'ethanal',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_ethanal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'ethanol', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'ethanol',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_ethanol_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'hexanal', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'hexanal',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_hexanal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-butanal', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-butanal',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_n-butanal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'naphthalene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'naphthalene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_naphthalene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'pentanal', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'pentanal',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_pentanal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-methylpropenal', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-methylpropenal',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_2-methylpropenal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'benzaldehyde', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'benzaldehyde',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_benzaldehyde_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-propanol', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-propanol',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_2-propanol_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),

            ('IMG', 'air', 'methanal', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'methanal',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_methanal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'propanone', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'propanone',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_propanone_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'propanal', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'propanal',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_propanal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-propanol', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-propanol',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_n-propanol_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'ethanedial', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'ethanedial',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_ethanedial_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-oxopropanal', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-oxopropanal',
                    'PM_UNIT': 'nmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_2-oxopropanal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'tetrachloroethylene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'tetrachloroethylene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_tetrachloroethylene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-propenal', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-propenal',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_2-propenal_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '3-buten-2-one', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '3-buten-2-one',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_3-buten-2-one_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'butanone', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'butanone',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_butanone_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'styrene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'styrene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_styrene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-2-3-trimethylbenzene', 'ug/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-2-3-trimethylbenzene',
                    'PM_UNIT': 'ug/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-2-3-trimethylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-2-4-trimethylbenzene', 'ug/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-2-4-trimethylbenzene',
                    'PM_UNIT': 'ug/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-2-4-trimethylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-3-5-trimethylbenzene', 'ug/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-3-5-trimethylbenzene',
                    'PM_UNIT': 'ug/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-3-5-trimethylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-ethyl-3-methylbenzene', 'ug/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-ethyl-3-methylbenzene',
                    'PM_UNIT': 'ug/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-ethyl-3-methylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-ethyl-4-methylbenzene', 'ug/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-ethyl-4-methylbenzene',
                    'PM_UNIT': 'ug/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-ethyl-4-methylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '3-carene', 'ug/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '3-carene',
                    'PM_UNIT': 'ug/m3',
                    'PM_CFNAME': 'mass_concentration_of_3-carene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'acenaphthene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'acenaphthene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_acenaphthene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'acenaphthylene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'acenaphthylene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_acenaphthylene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'anthracene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'anthracene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_anthracene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'fluorene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'fluorene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_fluorene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'alpha-pinene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'alpha-pinene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_alpha-pinene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'benzene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'benzene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_benzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'beta-pinene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'beta-pinene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_beta-pinene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'camphene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'camphene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_camphene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'ethylbenzene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'ethylbenzene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_ethylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'limonene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'limonene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_limonene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'linalool', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'linalool',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_linalool_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'm-p-xylene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'm-p-xylene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_m-p-xylene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'myrcene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'myrcene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_myrcene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-decane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-decane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-decane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-dodecane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-dodecane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-dodecane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-nonane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-nonane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-nonane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-octane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-octane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-octane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-pentadecane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-pentadecane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-pentadecane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-propylbenzene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-propylbenzene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-propylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-tetradecane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-tetradecane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-tetradecane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-tridecane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-tridecane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-tridecane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-undecane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-undecane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_n-undecane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'o-xylene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'o-xylene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_o-xylene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'p-cymene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'p-cymene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_p-cymene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'tert-butylbenzene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'tert-butylbenzene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_tert-butylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-ethyl-2-methylbenzene', 'pmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-ethyl-2-methylbenzene',
                    'PM_UNIT': 'pmol/mol',
                    'PM_CFNAME': 'mole_fraction_of_1-ethyl-2-methylbenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-butene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-butene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-butene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'chloroethene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'chloroethene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_chloroethene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'methane', 'mg/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'methane',
                    'PM_UNIT': 'mg/m3',
                    'PM_CFNAME': 'mass_concentration_of_methane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'ethane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'ethane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_ethane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'propane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'propane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_propane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-methylpropane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-methylpropane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_2-methylpropane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-hexadecane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-hexadecane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_n-hexadecane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-butane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-butane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_n-butane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-3-butadiene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-3-butadiene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-3-butadiene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'trans-2-butene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'trans-2-butene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_trans-2-butene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'cis-2-butene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'cis-2-butene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_cis-2-butene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-methylbutane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-methylbutane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_2-methylbutane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-pentene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-pentene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-pentene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-pentane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-pentane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_n-pentane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'trans-2-pentene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'trans-2-pentene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_trans-2-pentene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'isoprene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'isoprene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_isoprene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'cis-2-pentene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'cis-2-pentene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_cis-2-pentene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-methyl-2-butene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-methyl-2-butene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_2-methyl-2-butene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'dichloromethane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'dichloromethane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_dichloromethane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-methylpentane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-methylpentane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_2-methylpentane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '3-methylpentane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '3-methylpentane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_3-methylpentane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-hexene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-hexene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-hexene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-hexane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-hexane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_n-hexane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'trichloroethane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'trichloroethane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_trichloroethane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-2-dichloroethane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-2-dichloroethane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_1-2-dichloroethane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '2-2-4-trimethylpentane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '2-2-4-trimethylpentane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_2-2-4-trimethylpentane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'n-heptane', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'n-heptane',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_n-heptane_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'trichloroethene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'trichloroethene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_trichloroethene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'tetrachloroethene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'tetrachloroethene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mass_concentration_of_tetrachloroethene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'sabinene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'sabinene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_sabinene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'terpinolene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'terpinolene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_terpinolene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'toluene', 'ng/m3'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'toluene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_toluene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', '1-4-dichlorobenzene', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': '1-4-dichlorobenzene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_1-4-dichlorobenzene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'eucalyptol', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'eucalyptol',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_eucalyptol_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'longicyclene', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'longicyclene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_longicyclene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'iso-longifolene', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'iso-longifolene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_iso-longifolene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'beta-caryophyllene', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'beta-caryophyllene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_beta-caryophyllene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'beta-farnesene', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'beta-farnesene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_beta-farnesene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'alpha-humulene', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'alpha-humulene',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_alpha-humulene_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'air', 'nopinone', 'nmol/mol'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'air',
                    'CO_COMP_NAME': 'nopinone',
                    'PM_UNIT': 'ng/m3',
                    'PM_CFNAME': 'mole_fraction_of_nopinone_in_air',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),

            #
            # Precip
            #
            ('IMG', 'precip', 'sulphate_total', 'mg/l'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'precip',
                    'CO_COMP_NAME': 'sulphate_total',
                    'PM_UNIT': 'mg/l',
                    'PM_CFNAME': 'mass_concentration_of_sulphate_total_in_precipitation',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'precip', 'sulphate_corrected', 'mg/l'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'precip',
                    'CO_COMP_NAME': 'sulphate_corrected',
                    'PM_UNIT': 'mg/l',
                    'PM_CFNAME': 'mass_concentration_of_sulphate_corrected_in_precipitation',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'precip', 'ammonium', 'mg/l'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'precip',
                    'CO_COMP_NAME': 'ammonium',
                    'PM_UNIT': 'mg/l',
                    'PM_CFNAME': 'mass_concentration_of_ammonium_in_precipitation',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            ('IMG', 'precip', 'nitrate', 'mg/l'):
                DataObject({
                    'RE_REGIME_CODE': 'IMG',
                    'MA_MATRIX_NAME': 'precip',
                    'CO_COMP_NAME': 'nitrate',
                    'PM_UNIT': 'mg/l',
                    'PM_CFNAME': 'mass_concentration_of_nitrate_in_precipitation',
                    'PM_CFNAME_OFFICIAL': None,
                    'PM_CFUNIT': None,
                    'PM_DESC': None,
                    'PM_COMMENT': None,
                }),
            }
    
        # Special case: parameters which are converted on output to a different unit
        # but the CF_NAME is the same. E.g. nitrate ("ug N/m3" -> "ug/m3"
    
        # all nitrogen aerosols: nitrate, ammonium
        # here we duplicate all entries with *any* aerosol matrix and insert it
        # with an alternative unit.
        # IMPORTANT: this needs to be repeated, when EbasMasterPM.META is changed
        # e.g. after from_db
        for comp in ('nitrate', 'nitrite', 'ammonium'):
            for mat in _list_matrix_group(cls.META, 'IMG', "ALL_AEROSOL", comp):
                dic = cls.META[('IMG', mat, comp)].copy()
                if dic['PM_UNIT'] != 'ug N/m3':
                    RuntimeError('export unit exceptions setup error')
                dic['PM_UNIT'] = 'ug/m3'
                if dic['PM_CFNAME']:
                    if '_expressed_as_nitrogen' not in dic['PM_CFNAME']:
                        RuntimeError('export cfname exceptions setup error')
                    dic['PM_CFNAME'] = dic['PM_CFNAME'].replace(
                        '_expressed_as_nitrogen', '')
                # add the same metadata, but with a different unit:
                exceptions[('IMG', mat, comp, 'ug/m3')] = dic
        # all sulphour aerosols: sulphate_total, sulphate_corrected
        # here we duplicate all entries with *any* aerosol matrix and insert it
        # with an alternative unit.
        # IMPORTANT: this needs to be repeated, when EbasMasterPM.META is changed
        # e.g. after from_db
        for comp in ('sulphate_total', 'sulphate_corrected'):
            for mat in _list_matrix_group(cls.META, 'IMG', "ALL_AEROSOL", comp):
                dic = cls.META[('IMG', mat, comp)].copy()
                if dic['PM_UNIT'] != 'ug S/m3':
                    RuntimeError('export unit exceptions setup error')
                dic['PM_UNIT'] = 'ug/m3'
                if dic['PM_CFNAME']:
                    if '_expressed_as_sulphur' not in dic['PM_CFNAME']:
                        RuntimeError('export cfname exceptions setup error')
                    dic['PM_CFNAME'] = dic['PM_CFNAME'].replace(
                        '_expressed_as_sulphur', '')
                # add the same metadata, but with a different unit:
                exceptions[('IMG', mat, comp, 'ug/m3')] = dic
        cls.PM_EXCEPTIONALUNIT_EXP = exceptions


class EbasMasterPM(_ProtoEbasMasterPM):
    """
    Domain Class for Parameter masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling parameter and checking them against master data.
    Parameter master data are retrieved from database or from offline storage
    when no database access is possible.
    """
    # read offline masterdata for PM (parameters)
    # Those are fallback values, will be read from database as soon as possible.
    _ProtoEbasMasterPM.read_pickle_file()
    # some hardcoded exceptional parameters (see method exceptional):
    _ProtoEbasMasterPM._exceptions()
    _ProtoEbasMasterPM._exceptions_unit_exp()

    def __init__(self, dbh=None):
        """
        Read pm masterdata if dbh is provided.
        """
        PMOfflineMasterData.__init__(self)
        self.sc_ = EbasMasterSC(dbh=dbh)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
            # this changes the META dict. _exceptions_unit_exp MUST be re-run
            # (beacuse some exceptions build on existing definitions
            # (e.g. nitrate)
            self._exceptions_unit_exp()

    def __getitem__(self, key):
        """
        Allows dictionary like access to metadata.
        Exception for PM:
            - some attributes will be overruled by statistics code
            - exceptional metadata lookup (non DB, data level dependent)
        Parameters:
            key    (regime, matrix, component, statistics, data_level)
                   Only the first 3 are used for regular lookup!
                   statistics is used in case of overrules
                   data_level is optional and is used for finding exceptional
                   data level dependent masterdata
        """
        # first try: use regular masterdata, ignore data level
        try:
            return self._override_sc(self.__class__.META[key[:3]], key[3])
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
            return self._override_sc(
                self.__class__.PM_EXCEPTIONAL[data_level][key[:3]],
                key[3])

    def _override_sc(self, pm_, statistics):
        """
        Handle the unit, cfname and cfunit overeride for statistic codes
        (e.g. sample count).
        Parameters:
            pm_          pm element which would be returnd by default
            statistics   statstics code
        Returns:
            modified pm_
        """
        sc_ = self.sc_[statistics]
        if sc_.SC_UNIT is not None or sc_.SC_CFNAME is not None or \
                sc_.SC_CFUNIT is not None:
            ret = pm_.copy()
            if sc_.SC_UNIT is not None:
                ret.PM_UNIT = sc_.SC_UNIT
            if sc_.SC_CFNAME is not None:
                ret.PM_CFNAME = sc_.SC_CFNAME
            if sc_.SC_CFUNIT is not None:
                ret.PM_CFUNIT = sc_.SC_CFUNIT
            return ret
        return pm_

    def exceptional_unit_exp(self, key_tupel):
        """
        Find exceptional parameters (with exceptional units).
        This is only relevant for export of variables which were converted to
        alternative units (e.g. ozone, VOCs etc).
        Those parameters are defined in the database with DIFFERENT UNITS, so
        the usual lookup fot the tuple (regime, matrix, comp) will give a
        WRONG CF standard name!
        Parameters:
            key_tupel  (regime, matrix, component, unit)
        """
        return self.__class__.PM_EXCEPTIONALUNIT_EXP[key_tupel]

    @classmethod
    def exist_unit(cls, unit, datalevel=None):
        """
        Check if the unit exists (regardless of PM (RE, MA, CO)).
        Parameters:
            unit        unit to be checked
            datalevel   optional, if given check exceptional masterdata as well
        Returns:
            True/False
        """
        if any([elem['PM_UNIT'] == unit for elem in list(cls.META.values())]):
            return True
        if datalevel:
            if datalevel in ('0a', '0b'):
                datalevel = '0'
            if datalevel not in cls.PM_EXCEPTIONAL:
                return False
            if any([elem['PM_UNIT'] == unit
                    for elem in list(cls.PM_EXCEPTIONAL[datalevel].values())]):
                return True
        return False

    @classmethod
    def list_matrix_group(cls, regime, group, comp_name):
        """
        list all matrices within the group for which the regime and component
        are defined.
        This is used for mangling different unit on export conversions.
        See _exceptions_unit_exp above and
        ebas/domain/basic_domain_logic/unit_convert.py
        """
        return _list_matrix_group(cls.META, regime, group, comp_name)

