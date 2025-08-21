"""
$Id: zt.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for zero/spancheck type masterdata

This module implements the class EbasMasterZT.

History:
V.1.1.0  2016-10-17  pe  initial version

"""

from .offline_masterdata import ZTOfflineMasterData
from .base import EbasMasterBase

class EbasMasterZT(EbasMasterBase, ZTOfflineMasterData):
    """
    Domain Class for zero/spancheck type masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling stations and checking them against master data.
    Stations master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for ZT (zero/spancheck type)
    # Those are fallback values, will be read from database as soon as possible.
    ZTOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read zt masterdata if dbh is provided.
        """
        ZTOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
