"""
$Id: ht.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for hymidity/temperature control masterdata

This module implements the class EbasMasterHT.
"""

from .offline_masterdata import HTOfflineMasterData
from .base import EbasMasterBase

class EbasMasterHT(EbasMasterBase, HTOfflineMasterData):
    """
    Domain Class for hymidity/temperature control masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling stations and checking them against master data.
    Stations master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for PR (projects)
    # Those are fallback values, will be read from database as soon as possible.
    HTOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read ht masterdata if dbh is provided.
        """
        HTOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
