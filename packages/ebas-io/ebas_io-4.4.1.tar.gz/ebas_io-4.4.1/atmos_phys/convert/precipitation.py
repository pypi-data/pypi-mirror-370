"""
atmos_phys unit conversion routines for water solutions.
"""

from nilutility import numeric
from nilutility.datatypes import DataObject
from .base import ConvertBaseFactor
from .elements import ELEMENTS

class ConvertSulphate(ConvertBaseFactor):
    """
    Conversion class for sulphate in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'mg S/l':
            self.parameters.factor = \
                ELEMENTS['S']['MolarMass'] / \
                (ELEMENTS['S']['MolarMass'] + 4*ELEMENTS['O']['MolarMass'])
        elif self.from_unit == 'mg S/l' and self.to_unit == 'mg/l':
            self.parameters.factor = \
                (ELEMENTS['S']['MolarMass'] + 4*ELEMENTS['O']['MolarMass']) / \
                ELEMENTS['S']['MolarMass']
        elif self.from_unit == 'mg S/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['S']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg S/l':
            self.parameters.factor = ELEMENTS['S']['MolarMass'] / 1000.0
        elif self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = \
                1000.0 / (ELEMENTS['S']['MolarMass'] +
                          4 * ELEMENTS['O']['MolarMass'])
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = \
                (ELEMENTS['S']['MolarMass'] + 4 * ELEMENTS['O']['MolarMass']) \
                / 1000
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertAmmonium(ConvertBaseFactor):
    """
    Conversion class for ammonium in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'mg N/l':
            self.parameters.factor = \
                ELEMENTS['N']['MolarMass'] / \
                (ELEMENTS['N']['MolarMass'] + 4*ELEMENTS['H']['MolarMass'])
        elif self.from_unit == 'mg N/l' and self.to_unit == 'mg/l':
            self.parameters.factor = \
                (ELEMENTS['N']['MolarMass'] + 4*ELEMENTS['H']['MolarMass']) / \
                ELEMENTS['N']['MolarMass']
        elif self.from_unit == 'mg N/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['N']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg N/l':
            self.parameters.factor = ELEMENTS['N']['MolarMass'] / 1000.0
        elif self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = \
                1000.0 / (ELEMENTS['N']['MolarMass'] +
                          4 * ELEMENTS['H']['MolarMass'])
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = \
                (ELEMENTS['N']['MolarMass'] + 4 * ELEMENTS['H']['MolarMass']) \
                / 1000
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertNitrate(ConvertBaseFactor):
    """
    Conversion class for ammonium in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'mg N/l':
            self.parameters.factor = \
                ELEMENTS['N']['MolarMass'] / \
                (ELEMENTS['N']['MolarMass'] + 3*ELEMENTS['O']['MolarMass'])
        elif self.from_unit == 'mg N/l' and self.to_unit == 'mg/l':
            self.parameters.factor = \
                (ELEMENTS['N']['MolarMass'] + 3*ELEMENTS['O']['MolarMass']) / \
                ELEMENTS['N']['MolarMass']
        elif self.from_unit == 'mg N/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['N']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg N/l':
            self.parameters.factor = ELEMENTS['N']['MolarMass'] / 1000.0
        elif self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = \
                1000.0 / (ELEMENTS['N']['MolarMass'] +
                          3 * ELEMENTS['O']['MolarMass'])
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = \
                (ELEMENTS['N']['MolarMass'] + 3 * ELEMENTS['O']['MolarMass']) \
                / 1000
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertBicarbonate(ConvertBaseFactor):
    """
    Conversion class for bicarbonate (HCO3-) in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = \
                1000.0 / (ELEMENTS['H']['MolarMass'] + \
                          ELEMENTS['C']['MolarMass'] + \
                          3 * ELEMENTS['O'])
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = \
                (ELEMENTS['H']['MolarMass'] + ELEMENTS['C']['MolarMass'] + \
                 3 * ELEMENTS['O']['MolarMass']) / 1000.0
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertFluoride(ConvertBaseFactor):
    """
    Conversion class for fluoride (F-) in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['F']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = ELEMENTS['F']['MolarMass'] / 1000.0
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertCalcium(ConvertBaseFactor):
    """
    Conversion class for calcium in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['Ca']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = ELEMENTS['Ca']['MolarMass'] / 1000.0
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertChloride(ConvertBaseFactor):
    """
    Conversion class for chloride in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['Cl']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = ELEMENTS['Cl']['MolarMass'] / 1000.0
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertMagnesium(ConvertBaseFactor):
    """
    Conversion class for magnesium in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['Mg']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = ELEMENTS['Mg']['MolarMass'] / 1000.0
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertPhosphate(ConvertBaseFactor):
    """
    Conversion class for phosphate (PO4) in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = \
                1000.0 / (ELEMENTS['P']['MolarMass'] + \
                          4 * ELEMENTS['O']['MolarMass'])
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = \
                (ELEMENTS['P']['MolarMass'] + 4 * ELEMENTS['O']['MolarMass']) \
                / 1000.0
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertPotassium(ConvertBaseFactor):
    """
    Conversion class for potassium in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['K']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = ELEMENTS['K']['MolarMass'] / 1000.0
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

class ConvertSodium(ConvertBaseFactor):
    """
    Conversion class for potassium in precipitation
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
        self.parameters = DataObject(factor=None)
        if self.from_unit == 'mg/l' and self.to_unit == 'umol/l':
            self.parameters.factor = 1000.0 / ELEMENTS['Na']['MolarMass']
        elif self.from_unit == 'umol/l' and self.to_unit == 'mg/l':
            self.parameters.factor = ELEMENTS['Na']['MolarMass'] / 1000.0
        else:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

