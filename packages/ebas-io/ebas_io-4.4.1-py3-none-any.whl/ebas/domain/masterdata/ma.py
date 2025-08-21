"""
$Id: ma.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for matrix

This module implements the class EbasMasterMA.

"""

from .offline_masterdata import MAOfflineMasterData
from .base import EbasMasterBase

class EbasMasterMA(EbasMasterBase, MAOfflineMasterData):
    """
    Domain Class for matrix masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for CC (charring correction)
    # Those are fallback values, will be read from database as soon as possible.
    MAOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read co masterdata if dbh is provided.
        """
        MAOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

