"""
$Id: re.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for regime codes

This module implements the class EbasMasterRE.
"""

from .offline_masterdata import REOfflineMasterData
from .base import EbasMasterBase

class EbasMasterRE(EbasMasterBase, REOfflineMasterData):
    """
    Domain Class for regime codes masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling regime codes and checking them against master data.
    Regime codes master data are retrieved from database or from offline
    storage when no database access is possible.
    """

    # read offline masterdata for RE (statistcs codes)
    # Those are fallback values, will be read from database as soon as possible.
    REOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read se masterdata if dbh is provided.
        """
        REOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
