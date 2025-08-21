"""
Module atmos_phys.convert.aerosol: Unit conversion routines for aerosols.
"""

from nilutility import numeric
from nilutility.datatypes import DataObject
from .base import ConvertBaseFactor
from .elements import ELEMENTS

class ConvertNitrate(ConvertBaseFactor):
    """
    Conversion class for nitrate (NO3) conversions:
    Mass concentrationis "ug/m3" <-> "ug N/m3".

    Attributes:
        from_unit: The source unit of conversion
        to_unit: The result unit after conversion
        parameters: Parameters for the conversion
    """

    def _set_parameters(self):
        """
        Sets the conversion parameters.
        Called from base class init.
        Parameters:
            None
        Returns:
            None
        """
        if self.from_unit not in ('ug/m3', 'ug N/m3') or \
           self.to_unit not in ('ug/m3', 'ug N/m3') or \
           self.from_unit == self.to_unit:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

        self.parameters = DataObject(factor=None)
        if self.to_unit == 'ug N/m3':
            self.parameters.factor = \
                ELEMENTS['N']['MolarMass'] / \
                (ELEMENTS['N']['MolarMass'] + 3*ELEMENTS['O']['MolarMass'])
        else:
            self.parameters.factor = \
                (ELEMENTS['N']['MolarMass'] + 3*ELEMENTS['O']['MolarMass']) / \
                ELEMENTS['N']['MolarMass']


class ConvertNitrite(ConvertBaseFactor):
    """
    Conversion class for nitrite (NO2) conversions:
    Mass concentrationis "ug/m3" <-> "ug N/m3".
    """

    def _set_parameters(self):
        """
        Sets the conversion parameters.
        Called from base class init.
        Parameters:
            None
        Returns:
            None
        """
        if self.from_unit not in ('ug/m3', 'ug N/m3') or \
           self.to_unit not in ('ug/m3', 'ug N/m3') or \
           self.from_unit == self.to_unit:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

        self.parameters = DataObject(factor=None)
        if self.to_unit == 'ug N/m3':
            self.parameters.factor = \
                ELEMENTS['N']['MolarMass'] / \
                (ELEMENTS['N']['MolarMass'] + 2*ELEMENTS['O']['MolarMass'])
        else:
            self.parameters.factor = \
                (ELEMENTS['N']['MolarMass'] + 2*ELEMENTS['O']['MolarMass']) / \
                ELEMENTS['N']['MolarMass']


class ConvertAmmonium(ConvertBaseFactor):
    """
    Conversion class for ammonium (NH4) conversions:
    Mass concentrationis "ug/m3" <-> "ug N/m3".
    """

    def _set_parameters(self):
        """
        Sets the conversion parameters.
        Called from base class init.
        Parameters:
            None
        Returns:
            None
        """
        if self.from_unit not in ('ug/m3', 'ug N/m3') or \
           self.to_unit not in ('ug/m3', 'ug N/m3') or \
           self.from_unit == self.to_unit:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

        self.parameters = DataObject(factor=None)
        if self.to_unit == 'ug N/m3':
            self.parameters.factor = \
                ELEMENTS['N']['MolarMass'] / \
                (ELEMENTS['N']['MolarMass'] + 4*ELEMENTS['H']['MolarMass'])
        else:
            self.parameters.factor = \
                (ELEMENTS['N']['MolarMass'] + 4*ELEMENTS['H']['MolarMass']) / \
                ELEMENTS['N']['MolarMass']


class ConvertSulphate(ConvertBaseFactor):
    """
    Conversion class for nitrate (NO3) conversions:
    Mass concentrationis "ug/m3" <-> "ug N/m3".
    """

    def _set_parameters(self):
        """
        Sets the conversion parameters.
        Called from base class init.
        Parameters:
            None
        Returns:
            None
        """
        if self.from_unit not in ('ug/m3', 'ug S/m3') or \
           self.to_unit not in ('ug/m3', 'ug S/m3') or \
           self.from_unit == self.to_unit:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

        self.parameters = DataObject(factor=None)
        if self.to_unit == 'ug S/m3':
            self.parameters.factor = \
                ELEMENTS['S']['MolarMass'] / \
                (ELEMENTS['S']['MolarMass'] + 4*ELEMENTS['O']['MolarMass'])
        else:
            self.parameters.factor = \
                (ELEMENTS['S']['MolarMass'] + 4*ELEMENTS['O']['MolarMass']) / \
                ELEMENTS['S']['MolarMass']

