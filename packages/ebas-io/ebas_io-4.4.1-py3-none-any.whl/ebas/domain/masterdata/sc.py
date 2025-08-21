"""
$Id: sc.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for statistics codes

This module implements the class EbasMasterSC.
"""

from .offline_masterdata import SCOfflineMasterData
from .base import EbasMasterBase

class EbasMasterSC(EbasMasterBase, SCOfflineMasterData):
    """
    Domain Class for statistics codes masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling statistics codes and checking them against master data.
    Statistics codes master data are retrieved from database or from offline
    storage when no database access is possible.
    """

    # read offline masterdata for SC (statistcs codes)
    # Those are fallback values, will be read from database as soon as possible.
    SCOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read sc masterdata if dbh is provided.
        """
        SCOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
