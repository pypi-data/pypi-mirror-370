"""
NOAA NMHC Flask data file format

$Id: __init__.py 1796 2017-10-11 11:53:47Z pe $
"""

from .base import NOAA_NMHC_Flask_Error, NOAA_NMHC_Flask_Inconsistent
from .read import NOAA_NMHC_Flask_ReadError

from .read import NOAA_NMHC_Flask_Read, NOAA_NMHC_Flask_Rawdata_Read, \
    NOAA_NMHC_Flask_Header_Read, NOAA_NMHC_Flask_Data_Read, \
    NOAA_NMHC_Flask_HeaderContact_Read, NOAA_NMHC_Flask_HeaderDescription_Read

class NOAA_NMHC_Flask_Rawdata(NOAA_NMHC_Flask_Rawdata_Read):
    """
    Construct the final class.
    """
    pass

class NOAA_NMHC_Flask_HeaderContact(NOAA_NMHC_Flask_HeaderContact_Read):
    """
    Construct the final class.
    """
    pass

class NOAA_NMHC_Flask_HeaderDescription(NOAA_NMHC_Flask_HeaderDescription_Read):
    """
    Construct the final class.
    """
    pass

class NOAA_NMHC_Flask_Header(NOAA_NMHC_Flask_Header_Read):
    """
    Construct the final class.
    """
    pass

class NOAA_NMHC_Flask_Data(NOAA_NMHC_Flask_Data_Read):
    """
    Construct the final class.
    """
    pass


class NOAA_NMHC_Flask(NOAA_NMHC_Flask_Read):
    """
    Construct the final class.
    """
    pass
