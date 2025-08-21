"""
ebas/domain/masterdata/pm.py
$Id: pg_pl.py 2502 2020-10-14 16:57:35Z pe $

EBAS Masterdata Class for parameter masterdata

This module implements the class EbasMasterPG and PL.

History:
V.1.0.0  2014-10-06  pe  initial version

"""

from .offline_masterdata import PGOfflineMasterData, PLOfflineMasterData
from .base import EbasMasterBase


def uniq_list(lst):
    """
    List with only unique elements, keep order.
    """
    x = set()
    return [0 if x.add(y) else y for y in lst if y not in x]


class EbasMasterPG(EbasMasterBase, PGOfflineMasterData):
    """
    Domain Class for Parameter group masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling parameter and checking them against master data.
    Parameter master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for PG (parameter groups)
    # Those are fallback values, will be read from database as soon as possible.
    PGOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read pg masterdata if dbh is provided.
        """
        PGOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)


class EbasMasterPL(EbasMasterBase, PLOfflineMasterData):
    """
    Domain Class for Parameter group list masterdata.
    Objects of this class do not represent entities, this class provides class
    methods for handling parameter and checking them against master data.
    Parameter master data are retrieved from database or from offline storage
    when no database access is possible.
    """

    # read offline masterdata for PL (parameter group list)
    # Those are fallback values, will be read from database as soon as possible.
    PLOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read PL masterdata if dbh is provided.
        """
        PLOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)
        self._pg = EbasMasterPG(dbh=dbh)

    def list_groups(self, regime, matrix, comp_name):
        """
        List all groups for a given parameter
        Order the groups by descriptivity (i.e. comp_no ascending). Groups with
        many components are less descriptive than groups with less components.

        Does not use all_air and all_precip!
        Those are too wide and not descriptive.
        """
        raw = [(elem['PG_NAME'], self._pg[elem['PG_NAME']]['CO_COUNT'])
                for grp in self.META for elem in self.META[grp]
                if (elem['RE_REGIME_CODE'] is None or
                    regime == elem['RE_REGIME_CODE']) and \
                   (elem['MA_MATRIX_NAME'] is None or
                    matrix == elem['MA_MATRIX_NAME']) and \
                   (elem['CO_COMP_NAME'] is None or
                    comp_name == elem['CO_COMP_NAME'])]
        return [elem[0]
                for elem in sorted(raw, key=lambda x: x[1])
                if elem[0] not in ('all_air', 'all_precip')]

    def list_group_desc(self, regime, matrix, comp_name):
        """
        List all groups for a given parameter - prefer group desc if set, else
        name
        Order the groups by descriptivity (i.e. comp_no ascending). Groups with
        many components are less descriptive than groups with less components.
        """
        def pref_desc(name):
            """
            Returns the prefered description if exists, else the name
            """
            return (self._pg[name]['PG_DESC'] if self._pg[name]['PG_DESC']
                    else name)

        return uniq_list(
            [pref_desc(grp)
             for grp in self.list_groups(regime, matrix, comp_name)])
