"""
$Id: it.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for inlet type masterdata

This module implements the class EbasMasterIT.

"""

from .offline_masterdata import ITOfflineMasterData
from .base import EbasMasterBase

class EbasMasterIT(EbasMasterBase, ITOfflineMasterData):
    """
    Domain Class for inlet type masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for IT (inlet type)
    # Those are fallback values, will be read from database as soon as possible.
    ITOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read IT masterdata if dbh is provided.
        """
        ITOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

