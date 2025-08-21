"""
$Id: sm.py 2466 2020-07-10 13:20:48Z pe $

EBAS Masterdata Class for standard methods

This module implements the class EbasMasterSM.
"""

from .offline_masterdata import SMOfflineMasterData
from .base import EbasMasterBase

class EbasMasterSM(EbasMasterBase, SMOfflineMasterData):
    """
    Domain Class for standard method masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling standard methods and checking them against master data.
    Standard method master data are retrieved from database or from offline
    storage when no database access is possible.
    """

    # read offline masterdata for SM (standard methods)
    # Those are fallback values, will be read from database as soon as possible.
    SMOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read sm masterdata if dbh is provided.
        """
        SMOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    @classmethod
    def exist_standardmethod(cls, standard_method):
        """
        Check if the standard_method exists (regardless of FT).
        Parameters:
            standard_method    standard method code to be checked
        Returns:
            True/False
        """
        if any([key[1] == standard_method for key in list(cls.META.keys())]):
            return True
        return False
