"""
$Id: md.py 2466 2020-07-10 13:20:48Z pe $

EBAS Masterdata Class for medium

This module implements the class EbasMasterMD.
"""

from .offline_masterdata import MDOfflineMasterData
from .base import EbasMasterBase

class EbasMasterMD(EbasMasterBase, MDOfflineMasterData):
    """
    Domain Class for medium masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for CC (charring correction)
    # Those are fallback values, will be read from database as soon as possible.
    MDOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read MD masterdata if dbh is provided.
        """
        MDOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    @classmethod
    def exist_medium(cls, medium):
        """
        Check if the medium exists (regardless of FT).
        Parameters:
            medium    sensor type code to be checked
        Returns:
            True/False
        """
        if any([key[1] == medium for key in list(cls.META.keys())]):
            return True
        return False
