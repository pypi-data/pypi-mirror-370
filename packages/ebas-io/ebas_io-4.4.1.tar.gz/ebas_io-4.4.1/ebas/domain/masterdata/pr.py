"""
ebas/domain/masterdata/pr.py
$Id: pr.py 2088 2018-06-29 13:46:38Z pe $

EBAS Masterdata Class for Projects

This module implements the class EbasMasterPR.

History:
V.1.0.0  2014-02-25  pe  initial version

"""

from .. import EbasDomainError
from .offline_masterdata import PROfflineMasterData
from .base import EbasMasterBase

class EbasMasterPR(EbasMasterBase, PROfflineMasterData):
    """
    Domain Class for station masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling stations and checking them against master data.
    Stations master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for PR (projects)
    # Those are fallback values, will be read from database as soon as possible.
    PROfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read pr masterdata if dbh is provided.
        """
        PROfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    @classmethod
    def lookup_project(cls, project_acronym):
        """
        Lookup a project acronym (from command line parameter).
        Valid are:
            - full matching project acronym
        Parameters:
            project_acronym    string with project acronym
        Returns:
            string with project acronym:
        Raises:
            EbasDomainError if project acronym is invalid
        """
        if project_acronym in cls.META:
            # string can be found as a project acronym
            return project_acronym
        else:
            raise EbasDomainError("non existing project acronym '{}'"
                                  .format(project_acronym))
