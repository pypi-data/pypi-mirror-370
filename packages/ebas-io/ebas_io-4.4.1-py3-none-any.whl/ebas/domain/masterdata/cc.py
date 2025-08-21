"""
$Id: cc.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for charring correction masterdata

This module implements the class EbasMasterCC.

History:
V.1.0.0  2014-02-25  pe  initial version

"""

from .offline_masterdata import CCOfflineMasterData
from .base import EbasMasterBase

class EbasMasterCC(EbasMasterBase, CCOfflineMasterData):
    """
    Domain Class for charring correction masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for CC (charring correction)
    # Those are fallback values, will be read from database as soon as possible.
    CCOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read co masterdata if dbh is provided.
        """
        CCOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

