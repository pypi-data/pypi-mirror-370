"""
$Id: im.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for inlettube material masterdata

This module implements the class EbasMasterIM.

History:
V.1.1.0  2016-10-12  pe  initial version

"""

from .offline_masterdata import IMOfflineMasterData
from .base import EbasMasterBase

class EbasMasterIM(EbasMasterBase, IMOfflineMasterData):
    """
    Domain Class for inlettube material masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for IM (inlettube material)
    # Those are fallback values, will be read from database as soon as possible.
    IMOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read im masterdata if dbh is provided.
        """
        IMOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

