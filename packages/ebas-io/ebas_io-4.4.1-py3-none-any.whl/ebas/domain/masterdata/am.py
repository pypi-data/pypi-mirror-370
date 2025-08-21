"""
$Id: am.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for analyticalinstrument manufacturer/model masterdata

This module implements the class EbasMasterAM.

History:
V.1.0.0  2016-10-17  pe  initial version

"""

from .offline_masterdata import AMOfflineMasterData
from .base import EbasMasterBase

class EbasMasterAM(EbasMasterBase, AMOfflineMasterData):
    """
    Domain Class for analyticalinstrument manufacturer/model masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling components and checking them against master data.
    Components master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for AM (analyticalinstrument manufacturer/model)
    # Those are fallback values, will be read from database as soon as possible.
    AMOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read am masterdata if dbh is provided.
        """
        AMOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    def list(self, at_type=None, am_manufacturer=None, am_model=None):
        """
        Generates a list of matching masterdata.
        Parameters:
            at_type           analyticalinstrument type
            am_manufacturer   instrument manufacturer
            am_model          instrument model name
        Returns:
            generator of AM dictionaries with matching criteria
        """
        for am_ in self.__class__.META.values:
            if (at_type is None or am_['AT_TYPE'] == at_type) and \
               (am_manufacturer is None or \
                am_['AM_MANUFACTURER'] == am_manufacturer) and \
               (am_model is None or am_['AM_MODEL'] == am_model):
                yield am_
