"""
$Id: sx.py 2743 2021-11-23 15:48:15Z pe $
"""

from __future__ import absolute_import
# otherwise re is imported relative as masterdata.re
import re
import six
from .offline_masterdata import SXOfflineMasterData
from .base import EbasMasterBase
from .sz import EbasMasterSZ

class EbasMasterSX(EbasMasterBase, SXOfflineMasterData):
    """
    Domain Class for station auxiliary masterdata.
    Objects of this class do not represent entities, this class provides class
    methods handling caches masterdata.
    Stations master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for SX (station auxiliary masterdata)
    # Those are fallback values, will be read from database as soon as possible.
    SXOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read st masterdata if dbh is provided.
        """
        SXOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
