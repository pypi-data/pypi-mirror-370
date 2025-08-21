"""
EBAS Masterdata Class for absorption_crosssection metadata

This module implements the class EbasMasterAX.
"""

from .offline_masterdata import AXOfflineMasterData
from .base import EbasMasterBase

class EbasMasterAX(EbasMasterBase, AXOfflineMasterData):
    """
    Domain Class for analyticalinstrument type masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for AX (ax_absorption_crosssection)
    # Those are fallback values, will be read from database as soon as possible.
    AXOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read at masterdata if dbh is provided.
        """
        AXOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    @classmethod
    def exist_absorption_crosssection(cls, absorption_crosssection):
        """
        Check if the absorption crosssection exists (regardless of CO).
        Parameters:
            absorption_crosssection    absorption crosssection code to be checked
        Returns:
            True/False
        """
        if any([key[1] == absorption_crosssection
                for key in list(cls.META.keys())]):
            return True
        return False
