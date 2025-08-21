"""
ebas/domain/masterdata/ps.py
$Id: ps.py 2379 2019-11-19 09:58:18Z pe $

EBAS Masterdata Class for Persons

This module implements the class EbasMasterPS.
"""

from .. import EbasDomainError
from .offline_masterdata import PSOfflineMasterData
from .base import EbasMasterBase

class EbasMasterPS(EbasMasterBase, PSOfflineMasterData):
    """
    Domain Class for person masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling persons and checking them against master data.
    Person master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for PS (persons)
    # Those are fallback values, will be read from database as soon as possible.
    PSOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read ps masterdata if dbh is provided.
        """
        PSOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

