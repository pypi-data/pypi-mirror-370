"""
$Id: wc.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for watervapor correction masterdata

This module implements the class EbasMasterWC.
"""

from .offline_masterdata import WCOfflineMasterData
from .base import EbasMasterBase

class EbasMasterWC(EbasMasterBase, WCOfflineMasterData):
    """
    Domain Class for water vapor correction masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for WC (watervapor correction)
    # Those are fallback values, will be read from database as soon as possible.
    WCOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read co masterdata if dbh is provided.
        """
        WCOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

