"""
$Id: eanet_precip.py 2749 2021-11-25 00:34:17Z pe $

Basic EANET Precipitation functionality is implemented in the EanetPrecip class
in fileformats/EANET.
The ebas/io/eanet_precip (this) module is about mapping the EANET files to the
ebas IO data model.
"""

from .read_precip import EanetPrecipPartialRead

class EbasEanetPrecip(EanetPrecipPartialRead):
    """
    EANET Precip I/O object.
    """

