"""
$Id: fm.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for fieldinstrument manufacturer and model masterdata

This module implements the class EbasMasterFM.

History:
V.1.0.0  2014-02-25  pe  initial version

"""

from .offline_masterdata import FMOfflineMasterData
from .base import EbasMasterBase

class EbasMasterFM(EbasMasterBase, FMOfflineMasterData):
    """
    Domain Class for fieldinstrument manufacturer and model masterdata
    Objects of this class do not represent entities, this class provides class
    methods for handling fieldinstuments and checking them against master data.
    Instrument manufacturer / model master data are retrieved from database or
    from offline storage when no database access is possible.
    """

    # read offline masterdata for FM (fieldinstrument manufacturer and model)
    # Those are fallback values, will be read from database as soon as possible.
    FMOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read co masterdata if dbh is provided.
        """
        FMOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    def list(self, ft_type=None, fm_manufacturer=None, fm_model=None):
        """
        Generates a list of matching masterdata.
        Parameters:
            ft_type           fieldinstrument type
            fm_manufacturer   instrument manufacturer
            fm_model          instrument model name
        Returns:
            generator of FM dictionaries with matching criteria
        """
        for fm_ in self.__class__.META.values:
            if (ft_type is None or fm_['FT_TYPE'] == ft_type) and \
               (fm_manufacturer is None or \
                fm_['FM_MANUFACTURER'] == fm_manufacturer) and \
               (fm_model is None or fm_['FM_MODEL'] == fm_model):
                yield fm_
