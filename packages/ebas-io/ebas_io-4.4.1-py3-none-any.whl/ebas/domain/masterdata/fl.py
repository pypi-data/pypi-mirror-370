"""
$Id: fl.py 2427 2020-03-19 23:09:09Z pe $

EBAS Masterdata Class for Flags

This module implements the class EbasMasterFL.

History:
V.1.0.0  2014-02-25  pe  initial version

"""

from .offline_masterdata import FLOfflineMasterData
from .base import EbasMasterBase

class EbasMasterFL(EbasMasterBase, FLOfflineMasterData):
    """
    Domain Class for flags.
    Objects of this class do not represent entities, this class provides class
    methods for flag handling.
    """

    # Problem: for checking validity of flags and consistency of flags vs.
    # values values without DB connection, we need an offline store of flag
    # masterdata.
    # read offline masterdata for FL (flags)
    # Those are fallback values, will be read from database if possible.
    FLOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read cached fl masterdata if dbh is provided.
        """
        FLOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
