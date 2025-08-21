"""
$Id: vp.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for volume std pressure masterdata

This module implements the class EbasMasterVP.

"""

from .offline_masterdata import VPOfflineMasterData
from .base import EbasMasterBase

class EbasMasterVP(EbasMasterBase, VPOfflineMasterData):
    """
    Domain Class for volume std pressure masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling stations and checking them against master data.
    Stations master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for VP (volume std pressure)
    # Those are fallback values, will be read from database as soon as possible.
    VPOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read vp masterdata if dbh is provided.
        """
        VPOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
