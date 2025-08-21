"""
$Id: fp.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for filter prefiring masterdata

This module implements the class EbasMasterFP.

History:
V.1.1.0  2016-10-17  pe  initial version

"""

from .offline_masterdata import FPOfflineMasterData
from .base import EbasMasterBase

class EbasMasterFP(EbasMasterBase, FPOfflineMasterData):
    """
    Domain Class for filter prefiring masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling stations and checking them against master data.
    Master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for PR (projects)
    # Those are fallback values, will be read from database as soon as possible.
    FPOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read fp masterdata if dbh is provided.
        """
        FPOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
