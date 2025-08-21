"""
$Id: bc.py 2597 2021-01-19 13:36:24Z pe $

EBAS Masterdata Class for boundary check masterdata (BC and BA)

This module implements the class EbasMasterBC.

History:
V.1.0.0  2016-10-12  pe  initial version

"""

from .offline_masterdata import BCOfflineMasterData
from .base import EbasMasterBase

class EbasMasterBCNoProj(Exception):
    """
    Exception class, raise in case of no project specified in BC selection.
    """
    pass

class EbasMasterBCDuplicateError(Exception):
    """
    Exception class, raise in case of duplicate rules in BC
    """
    pass

class EbasMasterBCDuplicateErrorList(Exception):
    """
    Exception class, raise in case of duplicate rules in BC.
    Error list, generated in select() (possibly one error per project).
    """
    def __init__(self, message, errlist, retlist):  # pylint: disable=W0235
        # W0235: Useless super delegation in method
        # --> just for documenting what argument 0, 1, and 2 are used for
        """
        Initialize instance.
        Parameters:
            message    general exception text
            errlist    list of exceptions raised by _select_by_proj()
            retlist    list of bc rules found for projects w/o error
        """
        super(EbasMasterBCDuplicateErrorList, self).__init__(message, errlist,
                                                             retlist)

    @property
    def errlist(self):
        """
        Property method for errlist.
        Parameters:
            None
        Returns:
            errlist
        """
        return self.args[1]

    @property
    def retlist(self):
        """
        Property method for retlist.
        Parameters:
            None
        Returns:
            retlist
        """
        return self.args[2]


class EbasMasterBC(EbasMasterBase, BCOfflineMasterData):
    """
    Domain Class for boundary check masterdata (BA and BA)
    Objects of this class do not represent entities, this class provides class
    methods for handling boundary check rules and selecting applicable boundary
    checks.
    Boundary check master data are retrieved from database or from offline
    storage when no database access is possible.
    """

    # read offline masterdata for BC and BA (boundary checks)
    # Those are fallback values, will be read from database as soon as possible.
    BCOfflineMasterData.read_pickle_file()

    def __init__(self, dbh=None):
        """
        Read ac masterdata if dbh is provided.
        """
        BCOfflineMasterData.__init__(self)
        if not self.__class__.INIT and dbh:
            self.from_db(dbh)

    def select(self, crit_dict):
        """
        Select the best matching boundary check for a set of dataset metadata.
        Parameters:
            crit_dict    criteria dict (metadata for the dataset). Needed keys:
                         RE_REGIME_CODE, MA_MATRIX_NAME, CO_COMP_NAME,
                         PR_ACRONYM [list],
                         ST_STATION_CODE, FT_TYPE, FI_REF, DL_DATA_LEVEL,
                         SC_STATISTIC_CODE and characteristics
        Returns:
            List of boundary check rules (max one for each project), free of
            duplicates. Empty if no rules apply.
        Raises:
            EbasMasterBCDuplicateError in case of multiple rules matching per
            project
        """
        # Select all possible candidates
        # - regime, matrix, component MUST match exactly (they are not NULL in
        # the DB because the triple defines the parameter and thus the unit,
        # otherwise a boundery without defined unit does not make sense)
        # - most other criteria must either match or be set to None in BC
        # - special case characteristics: they must either be an empty list in
        # BC (no characteristics defined), or the complete set of
        # characteristics defined in BC must match.
        #
        # PR_ACRONYM overrule all others for sure. If a project defines
        # boundaries for a parameter it should be chosen over an exceptional
        # rule for station, instrument etc without project specified.
        # Exceptions for a project need to be defined explicidly.(with
        # project set)
        # Another complication is that a time series may be associated to
        # several projects. For each of those projects, the best fitting rule
        # is selected. In the end, for each check limit, the most restrictive
        # is selected to create the overal limits to be used.
        #
        # The rest of the priority chain is in reverse order of how restrictive
        # the criteria usually will be: FI_REF is very specific compared to
        # ST_STATION_CODE, and so on.
        #
        # for each project, find the best fitting rule:
        ret = []
        raise_ = []
        if 'PR_ACRONYM' not in crit_dict or not crit_dict['PR_ACRONYM']:
            raise EbasMasterBCNoProj('No framework specified')
        for proj in crit_dict['PR_ACRONYM']:
            try:
                proj_rule = self._select_by_proj(crit_dict, proj)
            except EbasMasterBCDuplicateError as excpt:
                raise_.append(excpt)
            else:
                if proj_rule and proj_rule not in ret:
                    ret.append(proj_rule)
        if raise_:
            raise EbasMasterBCDuplicateErrorList(
                'duplicate boundary check rules for dataset ({})'.format(
                    crit_dict), raise_, ret)
        return ret

    def _select_by_proj(self, crit_dict, pr_acronym):
        """
        Select the best matching boundary check for a set of dataset metadata
        and A SPECIFIC PROJECT ACRONYM.
        Parameters:
            crit_dict    criteria dict (metadata for the dataset). Needed keys:
                         RE_REGIME_CODE, MA_MATRIX_NAME, CO_COMP_NAME,
                         ST_STATION_CODE, FT_TYPE, FI_REF, DL_DATA_LEVEL,
                         SC_STATISTIC_CODE and characteristics
                         (PR_ACRONYM in the crit_dict is ignored, instead the
                         pr_acronym parameter is used (only one project))
            pr_acronym   project acronym for which the best fitting rule should
                         be found
        Returns:
            best matching BC dictionary for this project and the criteria
            metadata. If there is no project specific rule, the best matching
            general rule is returned.
            Thus, a project rule can both increase or decrease the general
            quality requirements. Exceptions (e.g. for a single station must
            then be done for all defined projects again.
            None in case of no match
        Raises:
            EbasMasterBCDuplicateError in case of multiple rules matching per
            project
        """
        cand = [bc_ for bc_ in sorted(list(self.META.values()),
                                      key=lambda x: x['BC_ID'])
                if bc_['RE_REGIME_CODE'] == crit_dict['RE_REGIME_CODE'] and \
                    bc_['MA_MATRIX_NAME'] == crit_dict['MA_MATRIX_NAME'] and \
                    bc_['CO_COMP_NAME'] == crit_dict['CO_COMP_NAME'] and \
                    bc_['PR_ACRONYM'] in (None, pr_acronym) and \
                    bc_['ST_STATION_CODE'] in \
                        (None, crit_dict['ST_STATION_CODE']) and \
                    bc_['FT_TYPE'] in (None, crit_dict['FT_TYPE']) and \
                    bc_['FI_REF'] in (None, crit_dict['FI_REF']) and \
                    bc_['DL_DATA_LEVEL'] in \
                        (None, crit_dict['DL_DATA_LEVEL']) and \
                    bc_['SC_STATISTIC_CODE'] in \
                        (None, crit_dict['SC_STATISTIC_CODE']) and \
                    (not bc_['characteristics'] or \
                     all([ct_ in crit_dict['characteristics'] and \
                          bc_['characteristics'][ct_] == \
                              crit_dict['characteristics'][ct_]
                          for ct_ in bc_['characteristics']]))]

        for prio in ('PR_ACRONYM', 'FI_REF', 'ST_STATION_CODE', 'FT_TYPE',
                     'DL_DATA_LEVEL', 'SC_STATISTIC_CODE'):
            if len(cand) == 1:
                return cand[0]
            if prio == 'PR_ACRONYM':
                newcand = [bc_ for bc_ in cand
                           if bc_['PR_ACRONYM'] == pr_acronym]
            else:
                newcand = [bc_ for bc_ in cand if bc_[prio] == crit_dict[prio]]
            if newcand:
                cand = newcand
        if len(cand) == 1:
            return cand[0]
        if cand:
            # still more then one candidate: count number of characteristics
            # matches for each candidate:
            cnt = [[ct_ in crit_dict['characteristics'] and
                        bc_['characteristics'][ct_] == \
                            crit_dict['characteristics'][ct_]
                    for ct_ in bc_['characteristics']].count(True)
                   for bc_ in cand]
            cand = [cand[i] for i in range(len(cnt)) if cnt[i] == max(cnt)]
        if len(cand) == 1:
            return cand[0]
        if cand:
            # still more then one candidate? Looks like we have identical rules?
            raise EbasMasterBCDuplicateError(
                'duplicate boundary check rules for dataset ({}), framework {}'
                .format(crit_dict, pr_acronym))
        return None
