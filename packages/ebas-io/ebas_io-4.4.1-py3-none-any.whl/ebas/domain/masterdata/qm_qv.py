"""
$Id: qm_qv.py 2466 2020-07-10 13:20:48Z pe $

EBAS Masterdata Class for quality measure and -validity masterdata

This module implements the classes EbasMasterQM and EbasMasterQV.

History:
V.1.1.0  2016-10-17  pe  initial version

"""


from __future__ import absolute_import
# otherwise re is imported relative as masterdata.re

import re
import six
from .offline_masterdata import QMOfflineMasterData, QVOfflineMasterData, \
    QOOfflineMasterData
from .base import EbasMasterBase

class EbasMasterQM(EbasMasterBase, QMOfflineMasterData):
    """
    Domain Class for quality measure masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for QM (quality measure)
    # Those are fallback values, will be read from database as soon as possible.
    QMOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read qm masterdata if dbh is provided.
        """
        QMOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    def new_reference_calibration(self, name):
        """
        Check if the qa measure ID is generic (O#) reference calibration
        which must be generated on import.
        Parameters:
            mane    QM ID
        Returns:
            (or_code, date) if it is a new reference calibration
            None if it is no new reference calibration
        """
        try:
            self[name]
        except KeyError:
            if isinstance(name, six.string_types):
                reg = re.match(
                    r'(.....)_reference_calibration_(\d\d\d\d\d\d\d\d)',
                    name)
                if reg:
                    return (reg.group(1), reg.group(2))
        return None




class EbasMasterQV(QVOfflineMasterData):
    """
    Domain Class for qualitymeasure validity masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for QV (qualitymeasure validity)
    # Those are fallback values, will be read from database as soon as possible.
    QVOfflineMasterData.read_pickle_file()
    # some hardcoded exceptional parameters (see method exceptional):
    #QV_EXCEPTIONAL = EbasMasterQV._qv_exceptions()

    def __getitem__(self, key):
        """
        Allows dictionary like access to metadata.
        Exception for QV:
            - exceptional metadata lookup (non DB, data level dependent)
        Parameters:
            key    (qm_id, ft_type, comp_name, data_level)
                   Only the first 3 are used for regular lookup!
                   data_level is optional and is used for finding exceptional
                   data level dependent masterdata
        """
        # first try: use regular masterdata, ignore data level
        try:
            return self.__class__.META[key[:3]]
        except KeyError:
            # don't exist: try exceptional masterdata (needs data level)
            # Those masterdata are NOT defined in the database, but might be
            # used e.g. in lev 0 files.
            # Thus they are accepted when reading the file, but the domain
            # layer will issue an error message.
            if len(key) != 4:
                raise
            data_level = key[3]
            if data_level in ('0a', '0b'):
                data_level = '0'
            return self.__class__.QV_EXCEPTIONAL[data_level][key[:3]]

    def __init__(self, dbh=None):
        """
        Read qv masterdata if dbh is provided.
        """
        QVOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
        # recalculate exceptional masterdata after db read:
        self.__class__.QV_EXCEPTIONAL = self._qv_exceptions()

    def list(self, qm_id=None, ft_type=None, co_comp_name=None):
        """
        Generates a list of matching masterdata.
        Parameters:
            qm_id             quality measure ID
            ft_type           fieldinstrument type
            co_comp_name      component name
        Returns:
            generator of QV dictionaries with matching criteria
        """
        for qv_ in list(self.__class__.META.values()):
            if (qm_id is None or qv_['QM_ID'] == qm_id) and \
               (ft_type is None or qv_['FT_TYPE'] == ft_type) and \
               (co_comp_name is None or qv_['CO_COMP_NAME'] == co_comp_name):
                yield qv_

    @classmethod
    def _qv_exceptions(cls):
        """
        Generate dictionary for exceptions (special datalevels, not imported but
        should be just file format checked.
        Parameters:
            None
        Returns:
            exception dict
        """
        exceptions = {'0': {}, '1': {}}

        # NOxy lev0: same QM_ID's as defined for NO, NO2 and NOx
        qm_list = list(set([qv_['QM_ID'] for qv_ in list(cls.META.values())
                            if qv_['FT_TYPE'] in
                            ('chemiluminescence_photolytic',
                             'chemiluminescence_molybdenum',
                             'chemiluminescence_photometer') and
                            qv_['CO_COMP_NAME'] in
                            ('nitrogen_monoxide', 'nitrogen_dioxide',
                             'NOx')]))
        basedict = {
        }
        for qm_id in qm_list:
            for inst in ('chemiluminescence_molybdenum',
                         'chemiluminescence_photolytic',
                         'chemiluminescence_photometer'):
                for comp in ('NO_#counts', 'NO_converter_#counts',
                             'NO_sensitivity', 'converter_efficiency',
                             'temperature', 'pressure', 'status'):
                    dict_ = basedict.copy()
                    dict_.update({'CO_COMP_NAME': comp, 'QM_ID': qm_id,
                                  'FT_TYPE': inst})
                    exceptions['0'][(dict_['QM_ID'], dict_['FT_TYPE'],
                                     dict_['CO_COMP_NAME'])] = dict_
        # NOxy lev1: same QM_ID's as defined for NO, NO2 and NOx
        qm_list = list(set([qv_['QM_ID'] for qv_ in list(cls.META.values())
                            if qv_['FT_TYPE'] in
                            ('chemiluminescence_photolytic',
                             'chemiluminescence_molybdenum',
                             'chemiluminescence_photometer') and
                            qv_['CO_COMP_NAME'] in
                            ('nitrogen_monoxide', 'nitrogen_dioxide',
                             'NOx')]))
        basedict = {
        }
        for qm_id in qm_list:
            for inst in ('chemiluminescence_molybdenum',
                         'chemiluminescence_photolytic',
                         'chemiluminescence_photometer'):
                for comp in ('temperature', 'pressure'):
                    dict_ = basedict.copy()
                    dict_.update({'CO_COMP_NAME': comp, 'QM_ID': qm_id,
                                  'FT_TYPE': inst})
                    exceptions['1'][(dict_['QM_ID'], dict_['FT_TYPE'],
                                     dict_['CO_COMP_NAME'])] = dict_
        # VOC (online_gc)
        for inst in ('online_gc',):
            qv_list = list(set([(qv_['QM_ID'], qv_['CO_COMP_NAME'])
                                for qv_ in list(cls.META.values())
                                if qv_['FT_TYPE'] == inst]))
            for qv_ in qv_list:
                basedict = {
                    'QM_ID': qv_[0],
                    'FT_TYPE': inst,
                }
                for ext in ('_peak_area', '_peak_width', '_retention_time'):
                    dict_ = basedict.copy()
                    dict_.update({'CO_COMP_NAME': qv_[1] + ext})
                    exceptions['0'][(dict_['QM_ID'], dict_['FT_TYPE'],
                                     dict_['CO_COMP_NAME'])] = dict_
            # distinct QM_ID:
            qm_list = list(set([x[0] for x in qv_list]))
            for qm_ in qm_list:
                for comp in ('status',):
                    exceptions['0'][(qm_, inst, comp)] = {
                        'QM_ID': qm_,
                        'FT_TYPE': inst,
                        'CO_COMP_NAME': comp}

        # filter_absorption_photometer (magee AE31, AE33) lev 0:
        # allow the same QM_ID's as defined for filter absorption_photometer
        qm_list = list(set([qv_['QM_ID'] for qv_ in list(cls.META.values())
                            if qv_['FT_TYPE'] == 'filter_absorption_photometer'
                            and qv_['CO_COMP_NAME'] ==
                            'aerosol_absorption_coefficient']))
        basedict = {
            'FT_TYPE': 'filter_absorption_photometer',
        }
        for qm_id in qm_list:
            # for each of those QM_IDs allow all components from AE31 and AE33
            # lev0 template
            for comp in ('flow_rate', 'status',
                         'equivalent_black_carbon', 'relative_humidity',
                         'filter_number', 'biomass_burning_aerosol_fraction',
                         'reference_beam_signal', 'sensing_beam_signal',
                         'filter_loading_compensation_parameter',
                         'equivalent_black_carbon_loading',
                         'attenuation_coefficient', 'sensing_zero_signal',
                         'reference_zero_signal', 'bypass_fraction',
                         'transmittance', 'sample_intensity',
                         'reference_intensity', 'sample_length_on_filter'):
                dict_ = basedict.copy()
                dict_.update({'CO_COMP_NAME': comp, 'QM_ID': qm_id})
                exceptions['0'][(dict_['QM_ID'], dict_['FT_TYPE'],
                                 dict_['CO_COMP_NAME'])] = dict_

        # nephelometer lev 0:
        # allow the same QM_ID's as defined for nephelometer
        qm_list = list(set([qv_['QM_ID'] for qv_ in list(cls.META.values())
                            if qv_['FT_TYPE'] == 'nephelometer' and
                            qv_['CO_COMP_NAME'] in
                            ('aerosol_light_backscattering_coefficient',
                             'aerosol_light_scattering_coefficient')]))
        basedict = {
            'FT_TYPE': 'nephelometer',
        }
        for qm_id in qm_list:
            for comp in (
                    'flow_rate', 'electric_tension', 'electric_current',
                    'status',
                    'aerosol_light_scattering_coefficient_zero_measurement',
                    'aerosol_light_backscattering_coefficient_zero_measurement',
                    'aerosol_light_rayleighscattering_coefficient_zero_measurement'):
                dict_ = basedict.copy()
                dict_.update({'CO_COMP_NAME': comp, 'QM_ID': qm_id})
                exceptions['0'][(dict_['QM_ID'], dict_['FT_TYPE'],
                                 dict_['CO_COMP_NAME'])] = dict_

        # dmps lev 0:
        # allow the same QM_ID's as defined for dmps
        qm_list = list(set([(qv_['FT_TYPE'], qv_['QM_ID'])
                            for qv_ in list(cls.META.values())
                            if qv_['FT_TYPE'].endswith('mps') and
                                qv_['CO_COMP_NAME'] ==
                                    'particle_number_size_distribution']))
        for ft_type, qm_id in qm_list:
            for comp in ('flow_rate', 'status', 'particle_diameter',
                         'particle_number_concentration'):
                dict_ = {
                    'FT_TYPE': ft_type,
                    'QM_ID': qm_id,
                    'CO_COMP_NAME': comp,
                    }
                exceptions['0'][(dict_['QM_ID'], dict_['FT_TYPE'],
                                 dict_['CO_COMP_NAME'])] = dict_

        # CCNC, DMPS-CCNC lev 0:
        # allow the same QM_ID's as defined for CCNC
        qm_list = list(set([qv_['QM_ID'] for qv_ in list(cls.META.values())
                            if qv_['FT_TYPE'] == 'CCNC' and
                            qv_['CO_COMP_NAME'] in
                            ('cloud_condensation_nuclei_number_concentration',)]))
        for qm_id in qm_list:
            for comp in ('supersaturation', 'electric_tension',
                         'electric_current', 'status', 'flow_rate',
                         'temperature_gradient'):
                for inst in ('CCNC', 'DMPS-CCNC'):
                    dict_ = {
                        'FT_TYPE': inst,
                        'CO_COMP_NAME': comp,
                        'QM_ID': qm_id,
                        }
                    exceptions['0'][(dict_['QM_ID'], dict_['FT_TYPE'],
                                 dict_['CO_COMP_NAME'])] = dict_
            # only DMPS-CCNC
            for comp in ('particle_diameter',
                         'cloud_condensation_nuclei_number_concentration'):
                    dict_ = {
                        'FT_TYPE': 'DMPS-CCNC',
                        'CO_COMP_NAME': comp,
                        'QM_ID': qm_id,
                        }
                    exceptions['0'][(dict_['QM_ID'], dict_['FT_TYPE'],
                                 dict_['CO_COMP_NAME'])] = dict_

        # cpc lev0
        # allow the same QM_ID's as defined for cpc
        qm_list = list(set([qv_['QM_ID'] for qv_ in list(cls.META.values())
                            if qv_['FT_TYPE'] == 'cpc' and
                            qv_['CO_COMP_NAME'] in
                            ('particle_number_concentration',)]))
        for qm_id in qm_list:
            for comp in ('pulse_width', 'flow_rate', 'relative_humidity'):
                dict_ = {
                    'FT_TYPE': 'cpc',
                    'CO_COMP_NAME': comp,
                    'QM_ID': qm_id,
                    }
                exceptions['0'][(dict_['QM_ID'], dict_['FT_TYPE'],
                             dict_['CO_COMP_NAME'])] = dict_

        return exceptions


class EbasMasterQO(QOOfflineMasterData):
    """
    Domain Class for quality assurance outcome masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for QM (quality measure)
    # Those are fallback values, will be read from database as soon as possible.
    QOOfflineMasterData.read_pickle_file()

    def __getitem__(self, name):
        """
        Allows dictionary like access to metadata
        """
        return self.__class__.META[name]

    def __init__(self, dbh=None):
        """
        Read qm masterdata if dbh is provided.
        """
        QOOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
