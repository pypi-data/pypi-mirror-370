"""
$Id: sz.py 2743 2021-11-23 15:48:15Z pe $
"""

from __future__ import absolute_import
# otherwise re is imported relative as masterdata.re
import re
import six
from .offline_masterdata import SZOfflineMasterData
from .base import EbasMasterBase

class EbasMasterSZ(EbasMasterBase, SZOfflineMasterData):
    """
    Domain Class for station auxiliary masterdata.
    """

    # read offline masterdata for ST (stations)
    # Those are fallback values, will be read from database as soon as possible.
    SZOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read sz masterdata if dbh is provided.
        """
        SZOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

