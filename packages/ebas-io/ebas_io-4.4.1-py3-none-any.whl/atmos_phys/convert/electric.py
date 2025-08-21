"""
atmos_phys unit conversion routines for electrical quantities.
"""

from nilutility.datatypes import DataObject
from .base import ConvertBaseFactor


class ConvertElectricCurrent(ConvertBaseFactor):
    """
    Conversion class for electric current.
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
        factors = {
            ('mA', 'A'): 0.001,
            ('A', 'mA'): 1000.0,
        }

        if self.from_unit not in \
               ('A', 'mA') or \
           self.to_unit not in \
               ('A', 'mA') or \
           self.from_unit == self.to_unit:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

        self.parameters = DataObject(
            factor=factors[(self.from_unit, self.to_unit)])

class ConvertConductivity(ConvertBaseFactor):
    """
    Conversion class for electric conductivity.
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
        factors = {
            ('mS/m', 'uS/cm'): 10.0,
            ('uS/cm', 'mS/m'): 0.1,
        }

        if self.from_unit not in \
               ('mS/m', 'uS/cm') or \
           self.to_unit not in \
               ('mS/m', 'uS/cm') or \
           self.from_unit == self.to_unit:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

        self.parameters = DataObject(
            factor=factors[(self.from_unit, self.to_unit)])

