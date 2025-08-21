"""
atmos_phys unit conversion routines for temperature.
"""

from nilutility.datatypes import DataObject
from .base import ConvertBase

_CELSIUS = 1
_KELVIN = 2
_MAXCONST = 2

UNIT_LOOKUP = {
    'deg C': _CELSIUS,
    'K': _KELVIN
    }

def _encode_direction(from_const, to_const):
    """
    Calculates the parameter encoding.
    """
    return from_const * _MAXCONST + to_const

_CELSIUS_TO_KELVIN = _encode_direction(_CELSIUS, _KELVIN)
_KELVIN_TO_CELSIUS = _encode_direction(_KELVIN, _CELSIUS)


class ConvertTemperature(ConvertBase):
    """
    Conversion class for temperatures.
    """

    def __init__(self, from_unit, to_unit):
        """
        Set up conversion object.
        Parameters:
            from_unit:
            to_unit: conversion from and to unit. Must be checked in
                     _set_parameters of the final class.
        """
        super(ConvertTemperature, self).__init__(from_unit, to_unit)

    def _set_parameters(self):
        """
        Sets the conversion parameters.
        Called from base class init.
        Parameters:
            None
        Returns:
            None
        Raises:
            ValueError on unknown or wrong units
        """
        try:
            from_const = UNIT_LOOKUP[self.from_unit]
            to_const = UNIT_LOOKUP[self.to_unit]
        except KeyError:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

        direction = _encode_direction(from_const, to_const)
        self.parameters = DataObject(direction=direction)

    def conversion_string(self, from_val=None, to_val=None):
        """
        Generates a conversion parameter string for the conversion.
        E.g. "from 'K' to 'dec C', subtracting 273.15",
             "from 'deg C' to 'K', adding 273.15"
        Parameters:
            from_val:
            to_val:
                If from_val and to_val are given, the values are included in the
                string (used to document conversion of uncertainty or detection
                limit values).
        Returns:
            a string for documenting the conversion.
        """
        from_val = "{} ".format(from_val) if from_val is not None else ""
        to_val = "{} ".format(to_val) if to_val is not None else ""

        if self.parameters.direction == _CELSIUS_TO_KELVIN:
            action = 'adding'
        else:
            action = 'subtracting'

        if self.rounding is None:
            convadd = " (no nonzero, valid values)"
        else:
            convadd = ", {} {:.{rdigits}f}"\
                    .format(action, 273.15, rdigits=self.rounding)
        return "from '{}{}' to '{}{}'{}".format(from_val, self.from_unit,
                                                to_val, self.to_unit,
                                                convadd)

    def convert_data(self, values):
        """
        Convert values using the conversion factor.
        Parameters:
            values: list of values (list of float)
        Returns:
            None
        """
        rnd = self.get_rounding(values)
        # avoid some float representation / rounding issues:
        if rnd == 1:
            abs_ = 273.15000000000001
        else:
            abs_ = 273.15
        if self.parameters.direction == _CELSIUS_TO_KELVIN:
            offset = abs_
        else:
            offset = -abs_

        for i, val in enumerate(values):
            if val is not None:
                values[i] = round(val+offset, rnd)
