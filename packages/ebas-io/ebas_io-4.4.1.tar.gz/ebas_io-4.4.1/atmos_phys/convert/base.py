"""
Module atmos_phys.convert.base: Base clas for all unit conversions.
"""

from nilutility import numeric


class ConvertBase(object):
    """Base class for conversions.

    Attributes:
        from_unit: source unit of conversion
        to_unit: target unit for conversion
        roundoffset: rounding offset
        maxround: maximum rounding threshold
        rounding: actual rounding digits used
        parameters: additional parameters for the conversion
    """

    def __init__(self, from_unit, to_unit, roundoffset=0, maxround=None):
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
                      1=1digit after comma).
                      Background: Historical data for some components have a
                      rounding issue: e.g. ozone, historical data have
                      been converted on user side, but reported only in
                      integer precission ug/m3. Now the exporter converts
                      back to nmol/mol, but dropps one decimal in rounding,
                      resulting in nmol/mol rounded to 10.
                      In order to avoid this, it's possible to specify a
                      threshold for rounding on export depending on
                      component.
                      Use an integer acording to the round function
                      (0=rounded to integer 1=round 1 decimal after the
                      comma, etc.). Alternatively specify None if no
                      threshold is needed.
        """
        self.from_unit = from_unit
        self.to_unit = to_unit
        self.roundoffset = roundoffset
        self.maxround = maxround
        self.rounding = None
        self.parameters = None
        self._set_parameters()

    def _set_parameters(self):
        """
        Checks frokm and to unit. Sets the conversion parameters.
        Must be implemented in derived class.
        Parameters:
            None
        Returns:
            None
        """
        raise NotImplementedError()

    def conversion_string(self, from_val=None, to_val=None):
        """
        Generates a conversion parameter string for the conversion.
        E.g. "from nmol/mol to ug/m3 at standard conditions (273.15 K, 1013.25 "
                 "hPa), using factor 1.234.",
             "from nmol/mol to ug/m3 at standard conditions (273.15 K, 1013.25 "
                 "hPa), no conversion factor used (no nonzero, valid values)."
        Parameters:
            from_val:
            to_val:
                If from_val and to_val are given, the values are included in the
                string (used to document conversion of uncertainty or detection
                limit values).
        Returns:
            a string for documenting the conversion.

        Must be implemented in derived class.
        """
        raise NotImplementedError()

    def _calc_base_rounding(self, values, add_offset=0):
        """
        Calculate the right number of digits for rounding according to the
        actual values' precision.
        Default implementation (without taking into account effects of e.g.
        conversion factors. See _calc_rounding and the use of add_offset.
        Parameters:
            values: list of data values to be converted
            add_offset: additional rounding offset for effects not taken into
                        account in this default implementation (e.g. conversion
                        factor)
        Returns:
            rounding needed (digits relative to the comma)
            e.g. 0 --> rounding to integer, 1 --> rounding to 10s,
            -1 --> rounding to 1 dicit after comma

            None in case of all values None
        """
        digstat = numeric.digits_stat(values)
        if digstat[2] == 0:
            # special case, all values were 0.0: double check and return
            if [x for x in values if x != 0.0 and x is not None] != []:
                raise RuntimeError("digits_stat returned unexpected value")
        if digstat[2] is None:
            # special case, all values were None: double check and return
            if [x for x in values if x is not None] != []:
                raise RuntimeError("digits_stat returned unexpected value")
            return None

        if digstat[2] > 0:
            rnd = digstat[2] * -1 + 1
        else:  # < 0
            rnd = digstat[2] * -1

        # add additinal offset depending on client class:
        rnd += add_offset

        # add or subtract on digit for rounding as specified by caller:
        rnd += self.roundoffset

        if self.maxround is not None and rnd < self.maxround:
            rnd = self.maxround
        return rnd

    def _calc_rounding(self, values):
        """
        Calculate the number of digits for rounding. This method is meant to be
        overridden by client implementations which need to take care of
        additional effects (e.g. conversion factor).
        """
        # Default, add_offset=0; override this method if needed
        return self._calc_base_rounding(values, add_offset=0)

    def get_rounding(self, values):
        """
        Calculate and store the right number of digits for rounding according
        to the actual values' precision.
        """
        if self.rounding is None:
            self.rounding = self._calc_rounding(values)
        return self.rounding

    def convert_data(self, values):
        """
        Convert values using the conversion factor.
        Parameters:
            values: list of values (list of float)
        Returns:
            None
        Must be implemented in derived class.
        """
        raise NotImplementedError()



class ConvertBaseFactor(ConvertBase):  # pylint: disable=W0223
    # W0223: Method ... is abstract in base class but is not overridden
    """
    Base class for conversions with only a factor.
    """

    def conversion_string(self, from_val=None, to_val=None):
        """
        Generates a conversion parameter string for the conversion.
        E.g. "from Torr to hPa, using factor 1.33322",
             "from Torr to hPa, no conversion factor used (no nonzero, "
             "valid values)"
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
        if self.rounding is None:
            convf = "no conversion factor (no nonzero, valid values)"
        else:
            convf = "conversion factor {:.{rdigits}f}"\
                    .format(self.parameters.factor, rdigits=self.rounding+2)
        return ("from '{}{}' to '{}{}', {}").format(
            from_val, self.from_unit, to_val, self.to_unit, convf)

    def _calc_rounding(self, values):
        """
        Calculate and store the right number of digits for rounding according
        to the actual values' precision.
        """
        # add order of magnitude for conversion factor:
        offs = 0
        (mant, ordm) = numeric.frexp10(self.parameters.factor)
        if mant >= 5:
            ordm += 1
        offs -= ordm
        return super(ConvertBaseFactor, self)._calc_base_rounding(
            values, add_offset=offs)

    def convert_data(self, values):
        """
        Convert values using the conversion factor.
        Parameters:
            values: list of values (list of float)
        Returns:
            None
        """
        rnd = self.get_rounding(values)

        for i, val in enumerate(values):
            if val is not None:
                values[i] = \
                    round(val*self.parameters.factor, rnd)
