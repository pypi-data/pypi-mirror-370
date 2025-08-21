"""
$Id: oc.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for ozone correction masterdata

This module implements the class EbasMasterOC.
"""

from .offline_masterdata import OCOfflineMasterData
from .base import EbasMasterBase

class EbasMasterOC(EbasMasterBase, OCOfflineMasterData):
    """
    Domain Class for ozone correction masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for OC (ozone correction)
    # Those are fallback values, will be read from database as soon as possible.
    OCOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read co masterdata if dbh is provided.
        """
        OCOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

