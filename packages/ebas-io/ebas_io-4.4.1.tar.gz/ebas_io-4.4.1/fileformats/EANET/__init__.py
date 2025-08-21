"""
NOAA NMHC Flask data file format

$Id: __init__.py 2725 2021-10-29 07:04:53Z pe $
"""

from .base import EanetError
from .read_filter import EanetFilterRead
from .read_precip import EanetPrecipRead

class EanetFilter(EanetFilterRead):
    """
    The final class EanetFilter inherits from read and possible more in the
    future?
    """
    pass

class EanetPrecip(EanetPrecipRead):
    """
    The final class EanetPrecip inherits from read and possible more in the
    future?
    """
    pass
