"""
atmos_phys unit conversion routines for gasses.
"""

import re
from nilutility.datatypes import DataObject
from .base import ConvertBaseFactor
from .elements import ELEMENTS

R = 8.3144621  # Gas constant

MIXING = 0b00
MASSCONC_ELEM = 0b10
MASSCONC_TOTAL = 0b11

class ConvertGasBase(ConvertBaseFactor):  # pylint: disable=W0223
    # W0223: Method ... is abstract in base class but is not overridden
    """
    Base class for gas conversions (mixing ratio / mass concentration).

    The gas conversion classes have their own base class. A lot of the logic
    is generically handled here. The final classes (conversion for single
    coponens) are only implementing by setting those class attributes.

    Attributes:
        MASS_CONC_ELEMENT: For parameters where only the mass of one element of
                           a component is used as mass concentartion unit.
                           E.g. sulfor_dioxide, ug S/m3
                           (-> MASS_CONC_ELEMENT = 'S')
        MOLAR_MASS: molar mass of the component or, in case of
                    MASS_CONC_ELEMENT, the molar mass of that element
        COMP_NAME: The EBAS component name, can be used to doublecheck molar 
                   mass (using the parameter synonyms, parsing the chemical
                   formular)
    TODO: check COMP_NAME
    TODO: in case of MASS_CONC_ELEMENT, an additional type of conversion can be
          defined: from/to mass concentration using the whole molecule
          E.g. in case of sulfor_dioxide, ug S/m3, additional conversion to
          ug/m3
    """

    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = None
    MOLAR_MASS_ELEMENT = None
    COMP_NAME = None

    def __init__(self, from_unit, to_unit, roundoffset=0, maxround=None,
                 temperature=273.15, pressure=101325):
        # pylint: disable=R0913
        # R0913: Too many arguments
        """
        Set up conversion object.
        Parameters:
            from_unit:
            to_unit: conversion from and to unit. Must be checked in
                     _set_parameters of the final class.
            roundoffset: rounding offset (usually +1 for import and -1 for
                         export)
            maxround: maximum rounding threshold, do no round coarser then
                      this should be used for export conversion only
                      (rounding expressed like in round function, 0=integer,
                      1=1digit after comma)
            temperature: temperature (standard conditions)
            pressure: pressure (standard conditions)
        For gas conversions, temperature and pressure (standard conditions for
        mass concentrations) are additionally needed.
        """
        # additional attributes for standard conditions.
        self.temperature = temperature
        self.pressure = pressure
        # call base class init
        super(ConvertGasBase, self).__init__(
            from_unit, to_unit, roundoffset=roundoffset, maxround=maxround)

    @classmethod
    def _parse_unit(cls, unit):
        """
        Parses a unit string
        Returns:
            tuple (prefix_factor, conversion_type)
            prefix_factor   factor which accounts for yhe metrix prefix
                            m=1E-3, u=1E-6, n=1E-9, p=1E-12
            conversion type bit field from/to mass concentartion / mixing ratio
        Raises Value error
        """
        prefixes = {
            None: 1,
            'm': 1.0E-3,
            'u': 1.0E-6,
            'n': 1.0E-9,
            'p': 1.0E-12,
        }
        parts_per = {
            'ppm': 1.0E-6,
            'ppmv': 1.0E-6,
            'ppb': 1.0E-9,
            'ppbv': 1.0E-9,
            'ppt': 1.0E-12,
            'pptv': 1.0E-12,
        }
        if cls.MASS_CONC_ELEMENT:
            reg = re.match(
                '^([munp])?g{}/m3$'.format((' ' + cls.MASS_CONC_ELEMENT)),
                unit)
            if reg:
                return prefixes[reg.group(1)], MASSCONC_ELEM
        reg = re.match(
            '^([munp])?g/m3$',
            unit)
        if reg:
            return prefixes[reg.group(1)], MASSCONC_TOTAL
        
        reg = re.match('^([munp])?mol/mol$', unit)
        if reg:
            return prefixes[reg.group(1)], MIXING
        if unit in parts_per:
            return parts_per[unit], MIXING
        raise ValueError("Unit '{}' cannot be parsed".format(unit))

    @property
    def from_mixing(self):
        """
        Conversion from mixing ratio?
        Returns:
            bool
        """
        return self.parameters.conv_type & 0b1100 == 0

    @property
    def from_massconc(self):
        """
        Conversion from mass concentration?
        Returns:
            bool
        """
        return self.parameters.conv_type & 0b1000 == 0b1000

    @property
    def from_massconc_elem(self):
        """
        Conversion from mass concentration based on one element?
        Returns:
            bool
        """
        return self.parameters.conv_type & 0b1100 == 0b1000

    @property
    def from_massconc_total(self):
        """
        Conversion from mass concentration based on the whole molecule?
        Returns:
            bool
        """
        return self.parameters.conv_type & 0b1100 == 0b1100

    @property
    def to_mixing(self):
        """
        Conversion to mixing ratio?
        Returns:
            bool
        """
        return self.parameters.conv_type & 0b11 == 0

    @property
    def to_massconc(self):
        """
        Conversion to mass concentration?
        Returns:
            bool
        """
        return self.parameters.conv_type & 0b10 == 0b10

    @property
    def to_massconc_elem(self):
        """
        Conversion to mass concentration based on one element?
        Returns:
            bool
        """
        return self.parameters.conv_type & 0b11 == 0b10

    @property
    def to_massconc_total(self):
        """
        Conversion to mass concentration based on the whole molecule?
        Returns:
            bool
        """
        return self.parameters.conv_type & 0b11 == 0b11

    def _set_parameters(self):
        """
        Sets the conversion parameters.
        Called from base class init.
        Parameters:
            None
        Returns:
            None
        Raises ValueError when unit cannot be parsed
        """
        try:
            from_prefix, from_type = self._parse_unit(self.from_unit)
            to_prefix, to_type = self._parse_unit(self.to_unit)
        except ValueError:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))
        self.parameters = DataObject(factor=None)
        self.parameters.conv_type = (from_type << 2) + to_type
        if self.from_mixing and self.to_massconc:
            if self.to_massconc_elem:
                molar_mass = self.__class__.MOLAR_MASS_ELEMENT
            else:
                molar_mass = self.__class__.MOLAR_MASS_TOTAL
            if molar_mass is None:
                raise ValueError(
                    "Conversion to {} is not supported, missing molar "
                    "mass".format(self.to_unit))
            self.parameters.factor = (
                (molar_mass / (R*self.temperature/self.pressure)) *
                (from_prefix / to_prefix))
        elif self.from_massconc and self.to_mixing:
            if self.from_massconc_elem:
                molar_mass = self.__class__.MOLAR_MASS_ELEMENT
            else:
                molar_mass = self.__class__.MOLAR_MASS_TOTAL
            if molar_mass is None:
                raise ValueError(
                    "Conversion from {} is not supported, missing molar "
                    "mass".format(self.from_unit))
            self.parameters.factor = (
                ((R*self.temperature/self.pressure) / molar_mass) *
                (from_prefix / to_prefix))
        else:
            self.parameters.factor = from_prefix / to_prefix
            if self.from_massconc_elem and self.to_massconc_total:
                if (self.__class__.MOLAR_MASS_TOTAL is None or
                    self.__class__.MOLAR_MASS_ELEMENT is None):
                    raise ValueError(
                        "Conversion from {} to {} is not supported, missing "
                        "molar mass".format(self.from_unit, self.to_unit))
                self.parameters.factor *= (self.__class__.MOLAR_MASS_TOTAL /
                                           self.__class__.MOLAR_MASS_ELEMENT)
            elif self.from_massconc_total and self.to_massconc_elem:
                if (self.__class__.MOLAR_MASS_TOTAL is None or
                    self.__class__.MOLAR_MASS_ELEMENT is None):
                    raise ValueError(
                        "Conversion from {} to {} is not supported, missing "
                        "molar mass".format(self.from_unit, self.to_unit))
                self.parameters.factor *= (self.__class__.MOLAR_MASS_ELEMENT /
                                           self.__class__.MOLAR_MASS_TOTAL)

    def conversion_string(self, from_val=None, to_val=None):
        """
        Generates a conversion parameter string for the conversion.
        E.g. "from nmol/mol to ug/m3 273.15 K, 1013.25 hPa, using factor 1.234",
             "from nmol/mol to ug/m3 at 273.15 K, 1013.25 hPa, no conversion "
                 "factor used (no nonzero, valid values)"
        Parameters:
            from_val:
            to_val:
               If from_val and to_val are given, the values are included in the
               string (used to document conversion of uncertainty or detection
               limit values).
        Returns a string for documenting the conversion.
        """
        from_val = "{} ".format(from_val) if from_val is not None else ""
        to_val = "{} ".format(to_val) if to_val is not None else ""
        if self.rounding is None:
            convf = "no conversion factor (no nonzero, valid values)"
        else:
            convf = "conversion factor {:.{rdigits}f}".format(
                self.parameters.factor, rdigits=max(self.rounding+2, 0))

        if self.from_mixing and self.to_massconc:
            return ("from '{}{}' to '{}{}' at {} K, {} hPa, {}").format(
                from_val, self.from_unit, to_val, self.to_unit,
                self.temperature, self.pressure/100.0, convf)
        elif self.from_massconc and self.to_mixing:
            return ("from '{}{}' at {} K, {} hPa to '{}{}', {}").format(
                from_val, self.from_unit, self.temperature, self.pressure/100.0,
                to_val, self.to_unit, convf)
        return ("from '{}{}' to '{}{}', {}").format(
            from_val, self.from_unit, to_val, self.to_unit, convf)


class ConvertNOx(ConvertGasBase):
    """
    Conversion class for NOx (NO, NO2, NOx) conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug N/m3).
    """
    MASS_CONC_ELEMENT = 'N'
    MOLAR_MASS_ELEMENT = ELEMENTS['N']['MolarMass']


class ConvertCarbonMonoxide(ConvertGasBase):
    """
    Conversion class for CO:
    Mixing ratio (nmol/mol) / mmass concentration (mg/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        1 * ELEMENTS['C']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'carbon_monoxide'


class ConvertAmmonia(ConvertGasBase):
    """
    Conversion class for NH3
    Mixing ratio (nmol/mol) / mmass concentration (ug N/m3).
    """
    COMP_NAME = 'ammonia'
    MOLAR_MASS_TOTAL = (
        1 * ELEMENTS['N']['MolarMass'] +
        3 * ELEMENTS['H']['MolarMass'])
    MASS_CONC_ELEMENT = 'N'
    MOLAR_MASS_ELEMENT = ELEMENTS['N']['MolarMass']


class ConvertHydrochloricAcid(ConvertGasBase):
    """
    Conversion class for HCl
    Mixing ratio (nmol/mol) / mmass concentration (ug Cl/m3).
    """
    MASS_CONC_ELEMENT = 'Cl'
    MOLAR_MASS_ELEMENT = ELEMENTS['Cl']['MolarMass']


class ConvertNitricAcid(ConvertGasBase):
    """
    Conversion class for HNO3
    Mixing ratio (nmol/mol) / mmass concentration (ug N/m3).
    """
    MASS_CONC_ELEMENT = 'N'
    MOLAR_MASS_ELEMENT = ELEMENTS['N']['MolarMass']


class ConvertNitrousAcid(ConvertGasBase):
    """
    Conversion class for HNO3
    Mixing ratio (nmol/mol) / mmass concentration (ug N/m3).
    """
    MASS_CONC_ELEMENT = 'N'
    MOLAR_MASS_ELEMENT = ELEMENTS['N']['MolarMass']


class ConvertSulphurDioxide(ConvertGasBase):
    """
    Conversion class for NOx (NO, NO2, NOx) conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug N/m3).
    """
    MASS_CONC_ELEMENT = 'S'
    MOLAR_MASS_ELEMENT = ELEMENTS['S']['MolarMass']


class ConvertOzone(ConvertGasBase):
    """
    Conversion class for ozone conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = 3 * ELEMENTS['O']['MolarMass']
    COMP_NAME = 'ozone'


class ConvertEthanal(ConvertGasBase):
    """
    Conversion class for ethanal conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        4 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'ethanal'


class ConvertEthanol(ConvertGasBase):
    """
    Conversion class for ethanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'ethanol'


class ConvertMethanal(ConvertGasBase):
    """
    Conversion class for methanal conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        1 * ELEMENTS['C']['MolarMass'] +
        2 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'methanal'


class ConvertPropanone(ConvertGasBase):
    """
    Conversion class for propanone conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        3 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'propanone'

class ConvertPropanal(ConvertGasBase):
    """
    Conversion class for propanal conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        3 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'propanal'


class ConvertNPropanol(ConvertGasBase):
    """
    Conversion class for n-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        3 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'n-propanol'


class ConvertEthanedial(ConvertGasBase):
    """
    Conversion class for glyoxal conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        2 * ELEMENTS['H']['MolarMass'] +
        2 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'ethanedial'


class Convert2Oxopropanal(ConvertGasBase):
    """
    Conversion class for methylglyoxal conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        3 * ELEMENTS['C']['MolarMass'] +
        4 * ELEMENTS['H']['MolarMass'] +
        2 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = '2-oxopropanal'


class Convert2Propenal(ConvertGasBase):
    """
    Conversion class for 2-propenal conversions:
    Mixing ratio (pmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        3 * ELEMENTS['C']['MolarMass'] +
        4 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = '2-propenal'


class Convert3Buten2One(ConvertGasBase):
    """
    Conversion class for 3-buten-2-one conversions:
    Mixing ratio (pmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = '3-buten-2-one'


class ConvertButanone(ConvertGasBase):
    """
    Conversion class for butanone conversions:
    Mixing ratio (pmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'butanone'


class ConvertStyrene(ConvertGasBase):
    """
    Conversion class for styrene conversions:
    Mixing ratio (pmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        8 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'styrene'

class ConvertHexanal(ConvertGasBase):
    """
    Conversion class for haxanal conversions:
    Mixing ratio (pmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        6 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'hexanal'


class ConvertNButanal(ConvertGasBase):
    """
    Conversion class for n-butanal conversions:
    Mixing ratio (pmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'n-butanal'


class ConvertNaphthalene(ConvertGasBase):
    """
    Conversion class for naphthalene conversions:
    Mixing ratio (pmol/mol) / mmass concentration (ng/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'naphthalene'


class ConvertPentanal(ConvertGasBase):
    """
    Conversion class for pentanal conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        5 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'pentanal'


class Convert2Methylpropenal(ConvertGasBase):
    """
    Conversion class for 2-methylpropenal conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = '2-methylpropenal'


class ConvertBenzaldehyde(ConvertGasBase):
    """
    Conversion class for benzaldehyde conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        7 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'benzaldehyde'


class Convert2Propanol(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        3 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = '2-propanol'

class Convert123Trimethylbenzene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-2-3-trimethylbenzene'


class Convert124Trimethylbenzene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-2-4-trimethylbenzene'


class Convert135Trimethylbenzene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-3-5-trimethylbenzene'


class Convert1Ethyl3Methylbenzene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-ethyl-3-methylbenzene'


class Convert1Ethyl4Methylbenzene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-ethyl-4-methylbenzene'


class Convert3Carene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '3-carene'


class ConvertAcenaphthene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        12 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'acenaphthene'


class ConvertAcenaphthylene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        12 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'acenaphthylene'


class ConvertAnthracene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        14 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'anthracene'


class ConvertFluorene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        13 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'fluorene'


class ConvertAlphaPinene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'alpha-pinene'


class ConvertBenzene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        6 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'benzene'


class ConvertBetaPinene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'beta-pinene'


class ConvertCamphene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'camphene'


class ConvertEthylbenzene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        8 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'ethylbenzene'


class ConvertLimonene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'limonene'


class ConvertLinalool(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        18 * ELEMENTS['H']['MolarMass'] +
        ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'linalool'


class ConvertMPXylene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        8 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'm-p-xylene'


class ConvertMyrcene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'myrcene'


class ConvertNPropylbenzene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-propylbenzene'


class ConvertMethane(ConvertGasBase):
    """
    Conversion class for methane conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        ELEMENTS['C']['MolarMass'] +
        4 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'methane'


class ConvertEthane(ConvertGasBase):
    """
    Conversion class for ethane conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'ethane'


class ConvertPropane(ConvertGasBase):
    """
    Conversion class for propane conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        3 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'propane'


class ConvertNButane(ConvertGasBase):
    """
    Conversion class for n-butane conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-butane'


class ConvertNPentane(ConvertGasBase):
    """
   Conversion class for n-pentane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        5 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass']
    )
    COMP_NAME = 'n-pentane'

class ConvertNHexane(ConvertGasBase):
    """
   Conversion class for n-hexane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        6 * ELEMENTS['C']['MolarMass'] +
        14 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-hexane'

class ConvertNHeptane(ConvertGasBase):
    """
   Conversion class for n-heptane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        7 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-heptane'


class ConvertNOctane(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        8 * ELEMENTS['C']['MolarMass'] +
        18 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-octane'


class ConvertNNonane(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        20 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-nonane'


class ConvertNDecane(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        22 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-decane'


class ConvertNUndecane(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        11 * ELEMENTS['C']['MolarMass'] +
        24 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-undecane'


class ConvertNDodecane(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        12 * ELEMENTS['C']['MolarMass'] +
        26 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-dodecane'


class ConvertNTridecane(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        13 * ELEMENTS['C']['MolarMass'] +
        28 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-tridecane'


class ConvertNTetradecane(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        14 * ELEMENTS['C']['MolarMass'] +
        30 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-tetradecane'


class ConvertNPentadecane(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        15 * ELEMENTS['C']['MolarMass'] +
        32 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-pentadecane'


class ConvertNHexadecane(ConvertGasBase):
    """
    Conversion class for n-hexadecane conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        16 * ELEMENTS['C']['MolarMass'] +
        34 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'n-hexadecane'


class Convert2Methylpropane(ConvertGasBase):
    """
    Conversion class for 2-methylpropane conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '2-methylpropane'


class ConvertOXylene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        8 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'o-xylene'


class ConvertPCymene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        14 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'p-cymene'


class ConvertTertButylbenzene(ConvertGasBase):
    """
    Conversion class for tert-butylbenzene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        14 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'tert-butylbenzene'


class Convert1Butene(ConvertGasBase):
    """
    Conversion class for 1-butene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-butene'


class ConvertTrans2Butene(ConvertGasBase):
    """
    Conversion class for trans-2-butene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'trans-2-butene'


class ConvertCis2Butene(ConvertGasBase):
    """
    Conversion class for cis-2-butene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'cis-2-butene'


class Convert2Methyl2Butene(ConvertGasBase):
    """
    Conversion class for 2-methyl-2-butene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        5 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '2-methyl-2-butene'


class Convert1Ethyl2Methylbenzene(ConvertGasBase):
    """
    Conversion class for 1-ethyl-2-methylbenzene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-ethyl-2-methylbenzene'


class ConvertChloroethene(ConvertGasBase):
    """
    Conversion class for chloroethene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        3 * ELEMENTS['H']['MolarMass'] +
                  1 * ELEMENTS['Cl']['MolarMass'])
    COMP_NAME = 'chloroethene'


class Convert13Butadiene(ConvertGasBase):
    """
    Conversion class for 1-3-butadiene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        4 * ELEMENTS['C']['MolarMass'] +
        6 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-3-butadiene'




class Convert2Methylbutane(ConvertGasBase):
    """
   Conversion class for 2-methylbutane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        5 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass']
    )
    COMP_NAME = '2-methylbutane'


class Convert1Pentene(ConvertGasBase):
    """
   Conversion class for 1-pentene conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        5 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass']
    )
    COMP_NAME = '1-pentene'



class ConvertTrans2Pentene(ConvertGasBase):
    """
   Conversion class for trans-2-pentene conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        5 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass']
    )
    COMP_NAME = 'trans-2-pentene'


class ConvertIsoprene(ConvertGasBase):
    """
   Conversion class for isoprene conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        5 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass']
    )
    COMP_NAME = 'isoprene'


class ConvertCis2Pentene(ConvertGasBase):
    """
   Conversion class for cis-2-pentene conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        5 * ELEMENTS['C']['MolarMass'] +
        10 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'cis-2-pentene'


class ConvertDichloromethane(ConvertGasBase):
    """
   Conversion class for dichloromethane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        1 * ELEMENTS['C']['MolarMass'] +
        2 * ELEMENTS['H']['MolarMass'] +
        2 * ELEMENTS['Cl']['MolarMass'])
    COMP_NAME = 'dichloromethane'


class Convert2Methylpentane(ConvertGasBase):
    """
   Conversion class for 2-methylpentane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        6 * ELEMENTS['C']['MolarMass'] +
        14 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '2-methylpentane'


class Convert3Methylpentane(ConvertGasBase):
    """
   Conversion class for 3-methylpentane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        6 * ELEMENTS['C']['MolarMass'] +
        14 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '3-methylpentane'


class Convert1Hexene(ConvertGasBase):
    """
   Conversion class for 1-hexene conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        6 * ELEMENTS['C']['MolarMass'] +
        12 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '1-hexene'


class ConvertTrichloroethane(ConvertGasBase):
    """
   Conversion class for trichloroethane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        3 * ELEMENTS['H']['MolarMass'] +
        3 * ELEMENTS['Cl']['MolarMass'])
    COMP_NAME = 'trichloroethane'


class Convert12Dichloroethane(ConvertGasBase):
    """
   Conversion class for 1-2-dichloroethane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        4 * ELEMENTS['H']['MolarMass'] +
        2 * ELEMENTS['Cl']['MolarMass'])
    COMP_NAME = '1-2-dichloroethane'


class Convert224Trimethylpentane(ConvertGasBase):
    """
   Conversion class for 2-2-4-trimethylpentane conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        8 * ELEMENTS['C']['MolarMass'] +
        18 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = '2-2-4-trimethylpentane'


class ConvertTrichloroethene(ConvertGasBase):
    """
   Conversion class for trichloroethene conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        1 * ELEMENTS['H']['MolarMass'] +
        3 * ELEMENTS['Cl']['MolarMass'])
    COMP_NAME = 'trichloroethene'


class ConvertTetrachloroethene(ConvertGasBase):
    """
   Conversion class for tetrachloroethene conversions:
    Mixing ratio (nmol/mol) / mass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        2 * ELEMENTS['C']['MolarMass'] +
        4 * ELEMENTS['Cl']['MolarMass'])
    COMP_NAME = 'tetrachloroethene'


class ConvertSabinene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'sabinene'


class ConvertTerpinolene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        16 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'terpinolene'


class ConvertToluene(ConvertGasBase):
    """
    Conversion class for 2-propanol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        7 * ELEMENTS['C']['MolarMass'] +
        8 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'toluene'


class Convert14Dichlorobenzene(ConvertGasBase):
    """
    Conversion class for 1-4-dichlorobenzene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        6 * ELEMENTS['C']['MolarMass'] +
        4 * ELEMENTS['H']['MolarMass'] +
        2 * ELEMENTS['Cl']['MolarMass'])
    COMP_NAME = '1-4-dichlorobenzene'


class ConvertEucalyptol(ConvertGasBase):
    """
    Conversion class for eucalyptol conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        10 * ELEMENTS['C']['MolarMass'] +
        18 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'eucalyptol'


class ConvertLongicyclene(ConvertGasBase):
    """
    Conversion class for longicyclene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        15 * ELEMENTS['C']['MolarMass'] +
        24 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'longicyclene'


class ConvertIsoLongifolene(ConvertGasBase):
    """
    Conversion class for iso-longifolene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        15 * ELEMENTS['C']['MolarMass'] +
        24 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'iso-longifolene'


class ConvertBetaCaryophyllene(ConvertGasBase):
    """
    Conversion class for beta-caryophyllene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        15 * ELEMENTS['C']['MolarMass'] +
        24 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'beta-caryophyllene'


class ConvertBetaFarnesene(ConvertGasBase):
    """
    Conversion class for beta-farnesene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        15 * ELEMENTS['C']['MolarMass'] +
        24 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'beta-farnesene'


class ConvertAlphaHumulene(ConvertGasBase):
    """
    Conversion class for alpha-humulene conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        15 * ELEMENTS['C']['MolarMass'] +
        24 * ELEMENTS['H']['MolarMass'])
    COMP_NAME = 'alpha-humulene'


class ConvertNopinone(ConvertGasBase):
    """
    Conversion class for nopinone conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug/m3).
    """
    MASS_CONC_ELEMENT = None
    MOLAR_MASS_TOTAL = (
        9 * ELEMENTS['C']['MolarMass'] +
        14 * ELEMENTS['H']['MolarMass'] +
        1 * ELEMENTS['O']['MolarMass'])
    COMP_NAME = 'nopinone'


def convf_volume_standard(temp1=273.15, pres1=101325, temp2=273.15,
                          pres2=101325):
    """
    Conversion factor for converting concentrations from one condition to
    another.
    Parameters:
        temp1: temperature to convert from
        pres1: pressure to convert from
        temp2: temperature to convert to
        pres2: pressure to convert to
    Returns:
        conversion factor
    Attention:
        all temperatures in K, all pressures in Pa (not hPa!!!)
    """
    return (temp1 * pres2) / (temp2 * pres1)
