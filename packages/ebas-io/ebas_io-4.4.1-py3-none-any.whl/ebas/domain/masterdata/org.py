"""
$Id: org.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for organization masterdata

Remark: or is a keyword in python, cannot be used as identifier (thus not as
module name, otherwise imports are syntactically wrong). Therefore this module
is named org, not or as it would be following the naming convention).

This module implements the class EbasMasterOR.

History:
V.1.0.0  2016-05-25  pe  initial version

"""

from .offline_masterdata import OROfflineMasterData
from .base import EbasMasterBase

class EbasMasterOR(EbasMasterBase, OROfflineMasterData):
    """
    Domain Class for organization masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling organizations and checking them against master data.
    Organization master data are retrieved from database or from offline
    storage when no database access is possible.
    """

    # read offline masterdata for OR (organizations)
    # Those are fallback values, will be read from database as soon as possible.
    OROfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read or masterdata if dbh is provided.
        """
        OROfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
