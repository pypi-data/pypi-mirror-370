"""
$Id: sw.py 2466 2020-07-10 13:20:48Z pe $

EBAS Masterdata Class for Station WMO Region

This module implements the class EbasMasterSW.
"""

from .offline_masterdata import SWOfflineMasterData
from .base import EbasMasterBase

class EbasMasterSW(EbasMasterBase, SWOfflineMasterData):
    """
    Domain Class for station masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling WMO region codes and checking them against master data.
    WMO region master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for SW (station WMO region code)
    # Those are fallback values, will be read from database as soon as possible.
    SWOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read st masterdata if dbh is provided.
        """
        SWOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
