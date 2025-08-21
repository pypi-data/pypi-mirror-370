"""
Unit conversion for ebas input and output
"""

import re
import atmos_phys.convert.gas as gas
import atmos_phys.convert.aerosol as aerosol
import atmos_phys.convert.precipitation as precipitation
import atmos_phys.convert.electric as electric
from atmos_phys.convert.temperature import ConvertTemperature
from atmos_phys.convert.pressure import ConvertPressure
from ebas.domain.masterdata.pm import EbasMasterPM


class NoConversion(Exception):
    """
    Exception raised when no conversion is possible.
    """
    def __init__(self, msgs):
        """
        Init the object
        """
        self.msgs = msgs

class UnitConvert(object):
    """
    Unit conversion for ebas input and output
    """

    # Configuration for EBAS unit conversion on import/export
    # regime, matrix, comp_name (and ebas_unit on export) identify the parameter
    # import: import conversion should be done
    #     units: accepted units for conversion on import
    #     need_stdcond: True: only converted if std conditions are given
    #                         (no conversion if not given in metadata)
    #                   False: not needed, conversion is possible anyway
    #     use_stdcond: standard conditions to be used for import conversion
    #                  (pressuer hPa, temp K) or (None, None) (no std cond used)
    #                  if need_stdcond: this is overruled
    #     set_stdcond: std condistions will be set to after conversion
    #                  (pressuer hPa, temp K)
    #                  (None, None) set to none
    #                  None: do not change
    #     roundoffset: round offset used for import conversion
    # export: export conversion should be done
    #     unit: unit to be converted on export
    #     need_stdcond: True: only converted if std conditions are given
    #                         (no conversion if not given in metadata)
    #                   False: not needed, conversion is possible anyway
    #     use_stdcond: standard conditions to be used for export conversion
    #                  (pressuer hPa, temp K) or (None, None) (no std cond used)
    #                  if need_stdcond: this is overruled
    #     set_stdcond: std condistions will be set to after export conversion
    #                  (pressuer hPa, temp K)
    #                  (None, None) set to none
    #                  None: do not change
    #     roundoffset: round offset used for export conversion
    #     maxround: maxround used for export conversion
    # cvt_class: conversion class to be used
    CONVERSIONS = [
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'carbon_monoxide',
            "ebas_unit": 'nmol/mol',
            "import": {
                "units": ['mg/m3', 'ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": gas.ConvertCarbonMonoxide
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "nitrogen_monoxide",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNOx
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "nitrogen_dioxide",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNOx
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "NOx",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNOx
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "ammonia",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertAmmonia
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'ammonia',
            "ebas_unit": 'ug N/m3',
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset, will not be re-exported
            },
            "cvt_class": gas.ConvertAmmonia
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "sulphur_dioxide",
            "ebas_unit": "ug S/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertSulphurDioxide
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "hydrochloric_acid",
            "ebas_unit": "ug Cl/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertHydrochloricAcid
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "nitric_acid",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNitricAcid
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "nitrous_acid",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNitrousAcid
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "ozone",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb'],
                "need_stdcond": False,
                # ozone: exceptional std cond.: 293.15 K
                "use_stdcond": (1013.25, 293.15),
                "set_stdcond": (1013.25, 293.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertOzone
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "ethanal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertEthanal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "ethanol",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertEthanol
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "hexanal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertHexanal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "n-butanal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNButanal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "naphthalene",
            "ebas_unit": "ng/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                # special case convert from ug/m3 to ng/m3 SEE BELOW
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNaphthalene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'naphthalene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            "cvt_class": gas.ConvertNaphthalene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "pentanal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertPentanal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "2-methylpropenal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert2Methylpropenal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "benzaldehyde",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertBenzaldehyde
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "2-propanol",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert2Propanol
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "methanal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertMethanal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "propanone",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertPropanone
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "propanal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertPropanal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "n-propanol",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNPropanol
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "ethanedial",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertEthanedial
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "2-oxopropanal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert2Oxopropanal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "2-propenal",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert2Propenal
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "3-buten-2-one",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert3Buten2One
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "butanone",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertButanone
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": "styrene",
            "ebas_unit": "ug/m3",
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertStyrene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-2-3-trimethylbenzene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert123Trimethylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-2-4-trimethylbenzene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert124Trimethylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-3-5-trimethylbenzene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert135Trimethylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-ethyl-3-methylbenzene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert1Ethyl3Methylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-ethyl-4-methylbenzene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert1Ethyl4Methylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '3-carene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert3Carene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'acenaphthene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertAcenaphthene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'acenaphthene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            "cvt_class": gas.ConvertAcenaphthene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'acenaphthylene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertAcenaphthylene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'acenaphthylene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            "cvt_class": gas.ConvertAcenaphthylene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'anthracene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertAnthracene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'anthracene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            "cvt_class": gas.ConvertAnthracene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'fluorene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertFluorene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'fluorene',
            "ebas_unit": 'ng/m3',
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            "cvt_class": gas.ConvertFluorene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'alpha-pinene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertAlphaPinene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'benzene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertBenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'beta-pinene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertBetaPinene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'camphene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertCamphene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'ethylbenzene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertEthylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'limonene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertLimonene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'linalool',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertLinalool
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'm-p-xylene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertMPXylene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'myrcene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertMyrcene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-decane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNDecane
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-dodecane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNDodecane
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-nonane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNNonane
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-octane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNOctane
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-pentadecane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNPentadecane
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-propylbenzene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNPropylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-tetradecane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNTetradecane
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-tridecane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNTridecane
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-undecane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNUndecane
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'o-xylene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertOXylene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'p-cymene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertPCymene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'tert-butylbenzene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                # special case convert from ng/m3 to ug/m3 SEE BELOW
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertTertButylbenzene,
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'tert-butylbenzene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            "cvt_class": gas.ConvertTertButylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-ethyl-2-methylbenzene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                # special case convert from ng/m3 to ug/m3 SEE BELOW
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "pmol/mol",
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert1Ethyl2Methylbenzene,
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-ethyl-2-methylbenzene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            "cvt_class": gas.Convert1Ethyl2Methylbenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-butene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert1Butene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'chloroethene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertChloroethene,
        },

        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'methane',
            "ebas_unit": 'nmol/mol',
            "import": {
                "units": ['mg/m3', 'ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "mg/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertMethane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'ethane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertEthane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'propane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertPropane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '2-methylpropane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert2Methylpropane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-hexadecane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNHexadecane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-butane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNButane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-3-butadiene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert13Butadiene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'trans-2-butene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertTrans2Butene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'cis-2-butene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertCis2Butene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '2-methylbutane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert2Methylbutane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-pentene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert1Pentene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-pentane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNPentane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'trans-2-pentene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertTrans2Pentene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'isoprene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertIsoprene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'cis-2-pentene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertCis2Pentene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '2-methyl-2-butene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert2Methyl2Butene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'dichloromethane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertDichloromethane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '2-methylpentane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert2Methylpentane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '3-methylpentane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert3Methylpentane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-hexene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert1Hexene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-hexane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNHexane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'trichloroethane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertTrichloroethane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-2-dichloroethane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert12Dichloroethane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '2-2-4-trimethylpentane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert224Trimethylpentane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'n-heptane',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNHeptane,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'trichloroethene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertTrichloroethene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'tetrachloroethene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertTetrachloroethene,
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'sabinene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertSabinene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'terpinolene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertTerpinolene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'toluene',
            "ebas_unit": 'pmol/mol',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": True,
                "use_stdcond": (None, None),
                "set_stdcond": (None, None),
                "roundoffset": 1,
            },
            "export": {
                "unit": "ng/m3",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertToluene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-4-dichlorobenzene',
            "ebas_unit": 'pg/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.Convert14Dichlorobenzene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": '1-4-dichlorobenzene',
            "ebas_unit": 'pg/m3',
            "import": {
                "units": ['ug/m3', 'ng/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            # no export conversion
            "cvt_class": gas.Convert14Dichlorobenzene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'eucalyptol',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertEucalyptol
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'eucalyptol',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3', 'pg/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            # no export conversion
            "cvt_class": gas.ConvertEucalyptol
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'longicyclene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertLongicyclene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'longicyclene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3', 'pg/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            # no export conversion
            "cvt_class": gas.ConvertLongicyclene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'iso-longifolene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertIsoLongifolene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'iso-longifolene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3', 'pg/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            # no export conversion
            "cvt_class": gas.ConvertIsoLongifolene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'beta-caryophyllene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertBetaCaryophyllene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'beta-caryophyllene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3', 'pg/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            # no export conversion
            "cvt_class": gas.ConvertBetaCaryophyllene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'beta-farnesene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertBetaFarnesene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'beta-farnesene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3', 'pg/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            # no export conversion
            "cvt_class": gas.ConvertBetaFarnesene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'alpha-humulene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertAlphaHumulene
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'alpha-humulene',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3', 'pg/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            # no export conversion
            "cvt_class": gas.ConvertAlphaHumulene
        },
        {
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'nopinone',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['nmol/mol', 'ppbv', 'ppb', 'pmol/mol', 'pptv', 'ppt'],
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": 1,
            },
            "export": {
                "unit": "nmol/mol",
                "need_stdcond": False,
                "use_stdcond": (1013.25, 273.15),
                "set_stdcond": (1013.25, 273.15),
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": gas.ConvertNopinone
        },
        {   # additional option for import conversion massconc -> massconc
            "regime": "IMG",
            "matrix": "air",
            "comp_name": 'nopinone',
            "ebas_unit": 'ug/m3',
            "import": {
                "units": ['ng/m3', 'pg/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 0,  # no roundoffset needed, factor 1000.0
            },
            # no export conversion
            "cvt_class": gas.ConvertNopinone
        },


        #
        # Aerosols
        #
        {
            "regime": "IMG",
            "matrix": "ALL_AEROSOL",
            "comp_name": "nitrate",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": aerosol.ConvertNitrate
        },

        {
            "regime": "IMG",
            "matrix": "ALL_AEROSOL",
            "comp_name": "nitrite",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": aerosol.ConvertNitrite
        },

        {
            "regime": "IMG",
            "matrix": "ALL_AEROSOL",
            "comp_name": "ammonium",
            "ebas_unit": "ug N/m3",
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": aerosol.ConvertAmmonium
        },

        {
            "regime": "IMG",
            "matrix": "ALL_AEROSOL",
            "comp_name": "sulphate_total",
            "ebas_unit": "ug S/m3",
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": aerosol.ConvertSulphate
        },
        {
            "regime": "IMG",
            "matrix": "ALL_AEROSOL",
            "comp_name": "sulphate_corrected",
            "ebas_unit": "ug S/m3",
            "import": {
                "units": ['ug/m3'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "ug/m3",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": aerosol.ConvertSulphate
        },

        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "sulphate_total",
            "ebas_unit": "mg S/l",
            "import": {
                "units": ['mg/l', 'umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "mg/l",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": precipitation.ConvertSulphate
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "sulphate_corrected",
            "ebas_unit": "mg S/l",
            "import": {
                "units": ['mg/l', 'umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "mg/l",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": precipitation.ConvertSulphate
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "nitrate",
            "ebas_unit": "mg N/l",
            "import": {
                "units": ['mg/l', 'umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "mg/l",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": precipitation.ConvertNitrate
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "ammonium",
            "ebas_unit": "mg N/l",
            "import": {
                "units": ['mg/l', 'umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            "export": {
                "unit": "mg/l",
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": -1,
                "maxround": 0,
            },
            "cvt_class": precipitation.ConvertAmmonium
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "bicarbonate",
            "ebas_unit": "mg/l",
            "import": {
                "units": ['umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": precipitation.ConvertBicarbonate
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "calcium",
            "ebas_unit": "mg/l",
            "import": {
                "units": ['umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": precipitation.ConvertCalcium
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "chloride",
            "ebas_unit": "mg/l",
            "import": {
                "units": ['umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": precipitation.ConvertChloride
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "fluoride",
            "ebas_unit": "mg/l",
            "import": {
                "units": ['umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": precipitation.ConvertFluoride
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "magnesium",
            "ebas_unit": "mg/l",
            "import": {
                "units": ['umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": precipitation.ConvertMagnesium
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "phosphate",
            "ebas_unit": "mg/l",
            "import": {
                "units": ['umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": precipitation.ConvertPhosphate
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "potassium",
            "ebas_unit": "mg/l",
            "import": {
                "units": ['umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": precipitation.ConvertPotassium
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "sodium",
            "ebas_unit": "mg/l",
            "import": {
                "units": ['umol/l'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                "roundoffset": 1,
            },
            # no export conversion
            "cvt_class": precipitation.ConvertSodium
        },
        {
            "regime": "IMG",
            "matrix": "precip",
            "comp_name": "conductivity",
            "ebas_unit": "uS/cm",
            "import": {
                "units": ['mS/m'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                # no roundoffset and maxround, conversion is just factor 1000
            },
            # no export conversion
            "cvt_class": electric.ConvertConductivity
        },

        {
            "regime": "IMG",
            "matrix": "met",
            "comp_name": "temperature",
            "ebas_unit": "deg C",
            "import": {
                "units": ['K'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                # no roundoffset and maxround, conversion is just an addition
            },
            # no export conversion
            "cvt_class": ConvertTemperature
        },
        {
            "regime": "IMG",
            "matrix": "instrument",
            "comp_name": "temperature",
            "ebas_unit": "K",
            "import": {
                "units": ['deg C'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                # no roundoffset and maxround, conversion is just an addition
            },
            # no export conversion
            "cvt_class": ConvertTemperature
        },
        {
            "regime": "IMG",
            "matrix": "instrument",
            "comp_name": "pressure",
            "ebas_unit": "hPa",
            "import": {
                "units": ['Torr'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                # no roundoffset and maxround, conversion is just an addition
            },
            # no export conversion
            "cvt_class": ConvertPressure
        },

        {
            "regime": "IMG",
            "matrix": "instrument",
            "comp_name": "electric_current",
            "ebas_unit": "A",
            "import": {
                "units": ['mA'],
                "need_stdcond": False,
                "use_stdcond": (None, None),
                "set_stdcond": None,
                # no roundoffset and maxround, conversion is just an addition
            },
            # no export conversion
            "cvt_class": electric.ConvertElectricCurrent
        }
    ]

    CONVERSIONS_CHECKED = False

    def __init__(self):
        """
        Set up the object.
        Parameters:
            None
        Returns:
            None
        """
        self._check_conversions()

    @classmethod
    def converted_units(cls):
        """
        List all units which could be converted on import.
        This method is used for checking valid units in ebas.io
        """
        converted_units = []
        for cvt in cls.CONVERSIONS:
            if 'import' in cvt:
                converted_units += cvt['import']['units']
        return converted_units

    def _check_conversions(self):
        """
        Sanity checks for the CONVERSIONS configuration.
         - Check if parameter exists
         - Check if ebas_unit is correct
         - Check if conversion class name is correct
         - Check if masterdata.pm has exceptional masterdata for the converted
           unit on export: If not checked here, an exception will only be raised
           when the conversion in question is actually used on an export. Thus
           bugs might be hidden for a long time and then crash the export
           process at inconvenient times.
        Here we precheck if the masterdata are in place, raising an exception
        even if the conversion is not nedded now.
        Parametrs:
            None
        Returns:
            None
        Raises:
            KeyError if masterdata are not found
            RuntimeError if ebas_unit is not found
        """

        def generic_cvt_name(comp):
            """
            Generate a generic class name for conversion objects.
            Generic class names are 'Convert' + camel case on - and _
            Parameters:
                component name
            Returns:
                the generic name for a conversion name (convention)
            """
            parts = ('Convert ' + re.sub(r"(_|-)+", " ", comp)).split()
            return "".join([part[0].upper()+part[1:] for part in parts])

        if self.__class__.CONVERSIONS_CHECKED:
            return
        mpm = EbasMasterPM()

        # replace ALL_AEROSOL matrix with all defined matices:
        i = 0
        while i < len(self.__class__.CONVERSIONS):
            cvt = self.__class__.CONVERSIONS[i]
            if cvt['matrix'] == "ALL_AEROSOL":
                mats = mpm.list_matrix_group(cvt['regime'], cvt['matrix'],
                                             cvt['comp_name'])
                if not mats:
                    raise RuntimeError(
                        "No areosol parameters for conversion {}".format(cvt))
                for mat in mats:
                    new = cvt.copy()
                    new['matrix'] = mat
                    self.__class__.CONVERSIONS.append(new)
                del self.__class__.CONVERSIONS[i]
                # del element, do not incremet i
            else:
                i += 1

        for cvt in self.__class__.CONVERSIONS:
            # check existence of original parameter
            # (e.g. comp name renamed in ebas?)
            pm_ = mpm[(cvt['regime'], cvt['matrix'], cvt['comp_name'],
                       'arithmetic mean')]
            # raise KeyError if not extsts
            # (e.g. component renamed in the database)
            if pm_.PM_UNIT != cvt['ebas_unit']:
                raise RuntimeError("PM unit error ({})".format(cvt))

            # check class name for conversion class (avoid copy/paste errors,
            # make sure the class names are up to date when component names are
            # changed in ebas):
            if cvt['cvt_class'].__name__ != generic_cvt_name(cvt['comp_name']):
                if cvt['comp_name'] in \
                       ('nitrogen_monoxide', 'nitrogen_dioxide') and \
                   cvt['cvt_class'].__name__ == 'ConvertNOx':
                    pass  # exception OK
                elif cvt['comp_name'] in \
                       ('sulphate_total', 'sulphate_corrected') and \
                   cvt['cvt_class'].__name__ == 'ConvertSulphate':
                    pass  # exception OK
                else:
                    raise RuntimeError(
                        "Unconventional conversion class name '{}' "
                        "(should be '{}'?)".format(
                            cvt['cvt_class'].__name__,
                            generic_cvt_name(cvt['comp_name'])))

            # check exceptional PM for converted unit on export:
            # raises KeyError if not exists
            if 'export' in cvt:
                mpm.exceptional_unit_exp(
                    (cvt['regime'], cvt['matrix'], cvt['comp_name'],
                     cvt['export']['unit']))
        self.__class__.CONVERSIONS_CHECKED = True

    def import_conv_params(self, regime, matrix,  # pylint: disable=R0913
                           comp_name, unit, std_pres, std_temp):
        # R0913: Too many arguments
        # --> acceptable here
        """
        Get input converison object.
        Parameters:
            regime       }
            matrix       } source parameter definition
            comp_name    }
            unit         }
            std_pres     standard pressure from metadata (None if not set)
            std_temp     standard temperature from metadata (None if not set)
        Returns:
            tupel (conv_obj, set_stdcond)
                Conversion object (from atmos_phys.convert, e.g. ConvertNOx,
                    ConvertOzone etc).
                set_stscond: (volume standard pressure,
                              volume standard temperature) to be set after
                             conversion
                             None if no change is needed
        Raises:
            NoConversion if no conversion possible
        """
        msgs = []
        for cvt in self.__class__.CONVERSIONS:
            # loop through all defined coversions and choose if one is
            # applicable.
            # pylint: disable=R0916
            # R0916: Too many boolean expressions in if statement
            # --> not much to do about it?
            if 'import' in cvt and \
               cvt['regime'] == regime and \
               cvt['matrix'] == matrix and \
               cvt['comp_name'] == comp_name and \
               unit in cvt['import']['units']:
                if cvt['import']['need_stdcond'] and \
                       (std_pres is None or std_temp is None):
                    msgs.append(
                        ("Regime/Matrix/Component combination '{}'/'{}'/'{}': "
                         "unit '{}' cannot be converted to '{}' "
                         "(standard conditions missing)").format(
                             regime, matrix, comp_name, unit, cvt['ebas_unit']))
                else:
                    args = [unit, cvt['ebas_unit']]  # from_unit, to_unit
                    kwargs = {}
                    if "roundoffset" in cvt['import']:
                        kwargs["roundoffset"] = cvt['import']["roundoffset"]
                    if "maxround" in cvt['import']:
                        kwargs["maxround"] = cvt['import']["maxround"]
                    if cvt['import']['need_stdcond']:
                        kwargs["pressure"] = std_pres*100
                        kwargs["temperature"] = std_temp
                    elif cvt['import']['use_stdcond']:
                        if cvt['import']['use_stdcond'][0] is not None:
                            kwargs["pressure"] = \
                                cvt['import']['use_stdcond'][0] * 100
                        if cvt['import']['use_stdcond'][1] is not None:
                            kwargs["temperature"] = cvt['import']['use_stdcond'][1]
                    return (cvt['cvt_class'](*args, **kwargs),
                            cvt['import']['set_stdcond'])
        raise NoConversion(msgs)

    def export_conv_params(self, regime, matrix,  # pylint: disable=R0913
                           comp_name, unit, std_pres, std_temp):
        # R0913: Too many arguments
        # --> acceptable here
        """
        Get output converison object.
        Parameters:
            regime       }
            matrix       } source parameter definition
            comp_name    }
            unit         }
            std_pres     standard pressure from metadata (None if not set)
            std_temp     standard temperature from metadata (None if not set)
        Returns:
            tupel (conv_obj, set_stdcond)
                Conversion object (from atmos_phys.convert, e.g. ConvertNOx,
                    ConvertOzone etc).
                set_stscond: (volume standard pressure,
                              volume standard temperature) to be set after
                             conversion
                             None if no change is needed
        Raises:
            NoConversion if no conversion possible
        """
        msgs = []
        for cvt in self.__class__.CONVERSIONS:
            # loop through all defined coversions and choose if one is
            # applicable.
            # pylint: disable=R0916
            # R0916: Too many boolean expressions in if statement
            # --> not much to do about it?
            if 'export' in cvt and \
               cvt['regime'] == regime and \
               cvt['matrix'] == matrix and \
               cvt['comp_name'] == comp_name and \
               cvt['ebas_unit'] == unit:
                if cvt['export']['need_stdcond'] and \
                        (std_pres is None or std_temp is None):
                    msgs.append(
                        ("Regime/Matrix/Component combination '{}'/'{}'/'{}': "
                         "unit '{}' cannot be converted to '{}' "
                         "(standard conditions missing)").format(
                             regime, matrix, comp_name, unit,
                             cvt['export']['unit']))
                else:
                    args = [unit, cvt['export']['unit']]  # from_unit, to_unit
                    kwargs = {}
                    if "roundoffset" in cvt['export']:
                        kwargs["roundoffset"] = cvt['export']["roundoffset"]
                    if "maxround" in cvt['export']:
                        kwargs["maxround"] = cvt['export']["maxround"]
                    if cvt['export']['need_stdcond']:
                        kwargs["pressure"] = std_pres*100
                        kwargs["temperature"] = std_temp
                    elif cvt['export']['use_stdcond']:
                        if cvt['export']['use_stdcond'][0] is not None:
                            kwargs["pressure"] = \
                                cvt['export']['use_stdcond'][0] * 100
                        if cvt['export']['use_stdcond'][1] is not None:
                            kwargs["temperature"] = cvt['export']['use_stdcond'][1]
                    return (cvt['cvt_class'](*args, **kwargs),
                            cvt['export']['set_stdcond'])
        raise NoConversion(msgs)
