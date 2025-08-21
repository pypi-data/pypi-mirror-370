"""
$Id: sp.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for sample preparation masterdata

This module implements the class EbasMasterSP.

History:
V.1.1.0  2016-10-12  pe  initial version

"""

from .offline_masterdata import SPOfflineMasterData
from .base import EbasMasterBase

class EbasMasterSP(EbasMasterBase, SPOfflineMasterData):
    """
    Domain Class for sample preparation masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling stations and checking them against master data.
    Stations master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for PR (projects)
    # Those are fallback values, will be read from database as soon as possible.
    SPOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read sp masterdata if dbh is provided.
        """
        SPOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
