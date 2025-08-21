"""
$Id: dl.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for data level masterdata

This module implements the class EbasMasterDL.
"""

from .offline_masterdata import DLOfflineMasterData
from .base import EbasMasterBase

class EbasMasterDL(EbasMasterBase, DLOfflineMasterData):
    """
    Domain Class for data level masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling data levels and checking them against master data.
    Data level master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for DL (data levels)
    # Those are fallback values, will be read from database as soon as possible.
    DLOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read co masterdata if dbh is provided.
        """
        DLOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
