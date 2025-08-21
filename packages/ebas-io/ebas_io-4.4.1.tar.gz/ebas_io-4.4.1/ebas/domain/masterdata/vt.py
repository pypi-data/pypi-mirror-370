"""
$Id: vt.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for volume std temperature masterdata

This module implements the class EbasMasterVT.

"""

from .offline_masterdata import VTOfflineMasterData
from .base import EbasMasterBase

class EbasMasterVT(EbasMasterBase, VTOfflineMasterData):
    """
    Domain Class for volume std temperature masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling stations and checking them against master data.
    Stations master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for VT (volume std temperature)
    # Those are fallback values, will be read from database as soon as possible.
    VTOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read vt masterdata if dbh is provided.
        """
        VTOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
