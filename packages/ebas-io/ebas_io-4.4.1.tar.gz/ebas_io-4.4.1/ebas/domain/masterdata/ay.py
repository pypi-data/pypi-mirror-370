"""
$Id: ay.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for analyticalinstrument type masterdata

This module implements the class EbasMasterAY.

History:
V.1.0.0  2016-10-17  pe  initial version

"""

from .offline_masterdata import AYOfflineMasterData
from .base import EbasMasterBase

class EbasMasterAY(EbasMasterBase, AYOfflineMasterData):
    """
    Domain Class for analyticalinstrument type masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for AY (analyticalinstrument type)
    # Those are fallback values, will be read from database as soon as possible.
    AYOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read at masterdata if dbh is provided.
        """
        AYOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
