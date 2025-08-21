"""
ebas/domain/masterdata/co.py
$Id: co.py 2660 2021-06-02 10:00:04Z pe $

EBAS Masterdata Class for component masterdata

This module implements the class EbasMasterCO.

History:
V.1.0.0  2014-02-25  pe  initial version

"""

from __future__ import absolute_import
import re
from .offline_masterdata import COOfflineMasterData
from .base import EbasMasterBase
from .pg_pl import EbasMasterPL

PTR_MS_COMP = (
    # not only organics
    'mass_21_species_count_rate', 'mass_25_species_count_rate',
    'mass_30_species_count_rate', 'mass_32_species_count_rate',
    'mass_37_species_count_rate', 'mass_55_species_count_rate',
    # organics by m/z (may be different comps)
    'mass_47_organic_compounds_count_rate',
    'mass_57_organic_compounds_count_rate',
    'mass_59_organic_compounds_count_rate',
    'mass_61_organic_compounds_count_rate',
    'mass_69_organic_compounds_count_rate',
    'mass_71_organic_compounds_count_rate',
    'mass_73_organic_compounds_count_rate',
    'mass_93_organic_compounds_count_rate',
    'mass_107_organic_compounds_count_rate',
    'mass_121_organic_compounds_count_rate',
    # specific organic compounds
    'methanal_count_rate', 'methanol_count_rate', 'acetonitrile_count_rate',
    'ethanal_count_rate', 'dimethylsulfide_count_rate',
    'methyl_acetate_count_rate', 'benzene_count_rate', 'styrene_count_rate',
    'chlorobenzene_count_rate', 'monoterpenes_count_rate',
    # NEW styrene, chlorobenzene
    # ToF mass_47_organic_compounds_count_rate:
    'formic_acid_count_rate', 'ethanol_count_rate',
    # ToF mass_61_organic_compounds_count_rate:
    'mass_61.028_organic_compounds_count_rate',
    'mass_61.065_organic_compounds_count_rate',
    # ToF mass_69_organic_compounds_count_rate:
    # 'furan_count_rate',  # TODO: furan not in regular components
    'isoprene_count_rate',
    # ToF mass_73_organic_compounds_count_rate:
    'mass_73.028_organic_compounds_count_rate',
    'mass_73.065_organic_compounds_count_rate',
    # ToF mass_93_organic_compounds_count_rate:
    # 'chloroacetone_count_rate',  # TODO: chloroacetone not in regular components
    # 'epoxybenzene_count_rate',  # TODO: epoxybenzene not in regular components
    'mass_93.06_organic_compounds_count_rate',
    'mass_93.070_organic_compounds_count_rate',
    'mass_93.091_organic_compounds_count_rate',
    # ToF mass_107_organic_compounds_count_rate:
    'benzaldehyde_count_rate',
    'mass_107.086_organic_compounds_count_rate')

class EbasMasterCO(EbasMasterBase, COOfflineMasterData):
    """
    Domain Class for components masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for CO (components)
    # Those are fallback values, will be read from database as soon as possible.
    COOfflineMasterData.read_pickle_file()
    # some hardcoded exceptional components (see method exceptional):
    CO_EXCEPTIONAL = {
        "0": {
            # ACSM lev0:
            'collection_efficiency': {
                'CO_COMP_NAME': 'collection_efficiency',
                'CO_CAPTION': None,
                'CO_DESC': None,
            },
            'nitrogen_ion_flow_signal': {
                'CO_COMP_NAME': 'nitrogen_ion_flow_signal',
                'CO_CAPTION': None,
                'CO_DESC': None,
            },
            'relative_ionization_efficiency': {
                'CO_COMP_NAME': 'relative_ionization_efficiency',
                'CO_CAPTION': None,
                'CO_DESC': None,
            },
            'airbeam_signal': {
                'CO_COMP_NAME': 'airbeam_signal',
                'CO_CAPTION': None,
                'CO_DESC': None,
            },
            'frequency': {
                'CO_COMP_NAME': 'frequency',
                'CO_CAPTION': None,
                'CO_DESC': None,
            },
            'electric_power': {
                'CO_COMP_NAME': 'electric_power',
                'CO_CAPTION': None,
                'CO_DESC': None,
            },
            'ionization_efficiency': {
                'CO_COMP_NAME': 'ionization_efficiency',
                'CO_CAPTION': None,
                'CO_DESC': None,
            },
            # NOX lev 0:
            'NO_#counts': {
                'CO_COMP_NAME': 'NO_#counts',
                'CO_CAPTION': 'NO_count',
                'CO_DESC': None,
            },
            'NO_converter_#counts':{
                'CO_COMP_NAME': 'NO_converter_#counts',
                'CO_CAPTION': 'NOc_count',
                'CO_DESC': None,
            },
            'NO_sensitivity':{
                'CO_COMP_NAME': 'NO_sensitivity',
                'CO_CAPTION': 'NO_sens',
                'CO_DESC': None,
            },
            'converter_efficiency':{
                'CO_COMP_NAME': 'converter_efficiency',
                'CO_CAPTION': 'converter_eff',
                'CO_DESC': None,
            },

            # dmps lev 0:
            'particle_diameter': {
                'CO_COMP_NAME': 'particle_diameter',
                'CO_CAPTION': 'p_diam',
                'CO_DESC': None,
            },
            # filter_absorption_photometer lev 0:
            'equivalent_black_carbon_loading': {
                'CO_COMP_NAME': 'equivalent_black_carbon_loading',
                'CO_CAPTION': 'BCmass',
                'CO_DESC': None,
            },
            # filter_absorption_photometer lev 0 (clap):
            'sample_length_on_filter': {
                'CO_COMP_NAME': 'sample_length_on_filter',
                'CO_CAPTION': 'smpllen',
                'CO_DESC': None,
            },
            # filter_absorption_photometer lev 0 (AE33):
            'filter_number': {
                'CO_COMP_NAME': 'filter_number',
                'CO_CAPTION': 'tpcnt',
                'CO_DESC': None,
            },
            # filter_absorption_photometer lev 0 (AE33):
            'biomass_burning_aerosol_fraction': {
                'CO_COMP_NAME': 'biomass_burning_aerosol_fraction',
                'CO_CAPTION': 'BB',
                'CO_DESC': None,
            },
            # filter_absorption_photometer lev 0 (AE33):
            'filter_loading_compensation_parameter': {
                'CO_COMP_NAME': 'filter_loading_compensation_parameter',
                'CO_CAPTION': 'k',
                'CO_DESC': None,
            },
            # nephelometer lev0
            'aerosol_light_scattering_coefficient_zero_measurement': {
                'CO_COMP_NAME':
                    'aerosol_light_scattering_coefficient_zero_measurement',
                'CO_CAPTION': 'scat0',
                'CO_DESC': None,
            },
            'aerosol_light_backscattering_coefficient_zero_measurement': {
                'CO_COMP_NAME':
                    'aerosol_light_backscattering_coefficient_zero_measurement',
                'CO_CAPTION': 'bscat0',
                'CO_DESC': None,
            },
            'aerosol_light_rayleighscattering_coefficient_zero_measurement': {
                'CO_COMP_NAME':
                    'aerosol_light_rayleighscattering_coefficient_'
                    'zero_measurement',
                'CO_CAPTION': 'rscat0',
                'CO_DESC': None,
            },
            # CCNC, DMPS-CCNC lev0:
            'supersaturation': {
                'CO_COMP_NAME': 'supersaturation',
                'CO_CAPTION': 'SS',
                'CO_DESC': None,
            },
            'temperature_gradient': {
                'CO_COMP_NAME': 'temperature_gradient',
                'CO_CAPTION': 'dT',
                'CO_DESC': None,
            },
            # cpc lev0:
            'pulse_width': {
                'CO_COMP_NAME': 'pulse_width',
                'CO_CAPTION': 'pulse',
                'CO_DESC': None,
            },
        },
        "1": {
            # CCNC, DMPS-CCNC lev1:
            'supersaturation': {
                'CO_COMP_NAME': 'supersaturation',
                'CO_CAPTION': 'SS',
                'CO_DESC': None,
            },
        },
    }
    # VOC lev0:
    pl_ = EbasMasterPL()
    for comp in [x.CO_COMP_NAME for x in pl_.META['VOC']]:
        for ext in ('_peak_area', '_peak_width', '_retention_time'):
            compmod = comp + ext
            CO_EXCEPTIONAL['0'][compmod] = {
                'CO_COMP_NAME': compmod,
                'CO_CAPTION': None,
                'CO_DESC': None,
            }
    # PTR-MS lev0:
    for comp in PTR_MS_COMP:
        reg = re.match(r'mass_(.*)(_organic_compounds)?_count_rate', comp)
        if reg:
            capt = 'mz' + reg.group(1)
        else:
            reg = re.match(r'^(.*)_count_rate', comp)
            if reg:
                capt = COOfflineMasterData.META[reg.group(1)].CO_CAPTION
            else:
                RuntimeError(comp + ' missing caption')
        CO_EXCEPTIONAL['0'][comp] = {
            'CO_COMP_NAME': comp,
            'CO_CAPTION': capt,
            'CO_DESC': None,
        }

    def __init__(self, dbh=None):
        """
        Read co masterdata if dbh is provided.
        """
        COOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)


    def __getitem__(self, key):
        """
        Allows dictionary like access to metadata.
        Exception for CO:
            - exceptional metadata lookup (non DB, data level dependent)
        Parameters:
            key    component (string) or tuple (component, data_level)
                   Only component is used for regulat lookup!
                   data_level is optional and is used for finding exceptional
                   data level dependent masterdata
        """
        if isinstance(key, (tuple, list)):
            component = key[0]
            data_level = key[1]
            if data_level in ['0a', '0b']:
                data_level = '0'
        else:
            component = key
            data_level = None
        # first try: use regular masterdata, ignore data level
        try:
            return self.__class__.META[component]
        except KeyError:
            if not data_level:
                raise
        # don't exist: try exceptional masterdata (needs data level)
        # Those masterdata are NOT defined in the database, but might be
        # used e.g. in lev 0 files.
        # Thus they are accepted when reading the file, but the domain
        # layer will issue an error message.
        return self.__class__.CO_EXCEPTIONAL[data_level][component]
