"""
atmos_phys unit conversion routines for pressure.
"""

from nilutility.datatypes import DataObject
from .base import ConvertBaseFactor


class ConvertPressure(ConvertBaseFactor):
    """
    Conversion class for NOx (NO, NO2, NOx) conversions:
    Mixing ratio (nmol/mol) / mmass concentration (ug N/m3).
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
            ('hPa', 'Pa'): 100.0,
            ('Pa', 'hPa'): 0.01,
            ('hPa', 'mbar'): 1.0,
            ('mbar', 'hPa'): 1.0,
            ('hPa', 'bar'): 0.001,
            ('bar', 'hPa'): 1000.0,
            ('hPa', 'psi'): 0.014503773773,
            ('psi', 'hPa'): 68.947572931783,
            ('hPa', 'Torr'): 0.75006375541921,
            ('Torr', 'hPa'): 1.3332236842108,

            ('Pa', 'mbar'): 0.01,
            ('mbar', 'Pa'): 100.0,
            ('Pa', 'bar'): 0.00001,
            ('bar', 'Pa'): 100000.0,
            ('Pa', 'psi'): 0.00014503773773,
            ('psi', 'Pa'): 6894.7572931783,
            ('Pa', 'Torr'): 0.0075006375541921,
            ('Torr', 'Pa'): 133.32236842108,

            ('mbar', 'bar'): 0.001,
            ('bar', 'mbar'): 1000.0,
            ('mbar', 'psi'): 0.014503773773,
            ('psi', 'mbar'): 68.947572931783,
            ('mbar', 'Torr'): 0.75006375541921,
            ('Torr', 'mbar'): 1.3332236842108,

            ('bar', 'psi'): 14.503773773,
            ('psi', 'bar'): 0.068947572931783,
            ('bar', 'Torr'): 750.06375541921,
            ('Torr', 'bar'): 0.0013332236842108,

            ('psi', 'Torr'): 51.71493257157,
            ('Torr', 'psi'): 0.0193367747046,
        }

        if self.from_unit not in \
               ('hPa', 'Pa', 'mbar', 'bar', 'psi', 'Torr') or \
           self.to_unit not in \
               ('hPa', 'Pa', 'mbar', 'bar', 'psi', 'Torr') or \
           self.from_unit == self.to_unit:
            raise ValueError("Conversion from {} to {} is not supported".format(
                self.from_unit, self.to_unit))

        self.parameters = DataObject(
            factor=factors[(self.from_unit, self.to_unit)])

