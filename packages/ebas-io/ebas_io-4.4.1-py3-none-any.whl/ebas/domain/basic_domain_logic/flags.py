"""
ebas.domain.basic_domain_logic.flags
$Id: flags.py 2561 2020-12-07 23:09:30Z pe $
Basic ebas domain logic for flags.
"""

from ebas.domain.masterdata.fl import EbasMasterFL
from .base import EbasDomainIssueList, \
    ISSUE_SEVERITY_ERROR, ISSUE_SEVERITY_WARNING, \
    MSGID_FLAGCHECK_ILLEGAL, MSGID_FLAGCHECK_MISSING_100, \
    MSGID_FLAGCHECK_VALID_VALUE_MISSIG_FLAG, \
    MSGID_FLAGCHECK_MISSING_VALUE_FLAG_100, \
    MSGID_FLAGCHECK_MISSING_VALUE_NO_FLAG, \
    MSGID_FLAGCHECK_PRECIP_FLAG_782_783_784_DROPPED, \
    MSGID_FLAGCHECK_PRECIP_FLAG_782_783_784_ERROR, \
    MSGID_FLAGCHECK_PRECIP_FLAG_890_DROPPED, \
    MSGID_FLAGCHECK_PRECIP_FLAG_890_SET_ZERO, \
    MSGID_FLAGCHECK_PRECIP_FLAG_890_ERROR, \
    MSGID_FLAGCHECK_AUX_VALID_VALUE_MISSING_FLAG

def get_flag_summary(flags, want_issues=True):
    """
    Get a summary of flag validity.
    Parameters:
        flags        list of flags for one sample (list of int)
        want_issues  bool, True if a list of issues should be returned
                     (not needed for export from DB...)
    Returns:
        tupel (valid, invalid, missing, issues) if issues == True
        else tupel (valid, invalid, missing)
        numbers for invalid, valid and missing flags
        as well as list of issues (EbasDomainIssueList)
    """
    emfl = EbasMasterFL()
    valid, invalid, missing = 0, 0, 0
    if want_issues:
        issues = EbasDomainIssueList(
            keys=('severity', 'msg_id', 'message'),
            msg_id=(MSGID_FLAGCHECK_ILLEGAL, MSGID_FLAGCHECK_MISSING_100))
    for flag in flags:
        try:
            validity = emfl[flag]['FL_VALIDITY']
        except KeyError:
            if want_issues:
                issues.add(
                    ISSUE_SEVERITY_ERROR, MSGID_FLAGCHECK_ILLEGAL,
                    "illegal flag: {0}".format(flag))
            continue
        if validity == 'V' or validity == 'H':
            valid += 1
        if validity == 'I':
            invalid += 1
        elif validity == 'M':
            missing += 1
    if 100 in flags:
        if missing > 1 and want_issues:
            issues.add(
                ISSUE_SEVERITY_ERROR, MSGID_FLAGCHECK_MISSING_100,
                "invalid combination of missing flag and flag 100")
        # force re-validation of invalid flagged data
        # data must not be missing!
        invalid = 0
    return (valid, invalid, missing, issues) if want_issues \
        else (valid, invalid, missing)

def check_value_flag_consistency(
        values, flags, ds_special, ignore_flagconsistency, fix_flagconsistency):
    """
    Checks consistency of values and flags for samples.
    Does not directly log issues but collects issues in a EbasDomainIssueList.
    Thus, the caller can employ a message condenser object to condense messages
    to be logged.
    Parameters:
        values     list of values for a time series
        flags      list fo flags (list of lists) of a time series
        ds_special special type of data
                    1 precipitation amount
                    2 auxiliary data
                      (special case: delete value if missing flag)
    Returns:
        EbasDomainIssueList with issues found (empty list if OK)
    """
    issues = EbasDomainIssueList()
    if len(values) != len(flags):
        RuntimeError('Values and flag lists not equal size')
    for i in range(len(values)):  # pylint: disable=C0200
        # C0200: Consider using enumerate instead of iterating with range/len
        # --> only using index
        # change value, drop some flags in advance:
        if ds_special == 1:  # precipitation amount
            _check_value_flag_precip_amount(
                values, flags, ignore_flagconsistency, fix_flagconsistency, i,
                issues)
        if ds_special == 2:  # auxiliary data
            _check_value_flag_auxiliary_ds(
                values, flags, ignore_flagconsistency, fix_flagconsistency, i,
                issues)
        _, invalid, missing, flag_issues = get_flag_summary(flags[i])
        for err in flag_issues:
            issues.add(err['severity'], err['msg_id'], i,
                       err['message'] + " value={}, flags={}".format(
                           values[i], flags[i]))
        if missing > 0 and values[i] != None:
            sev = ISSUE_SEVERITY_ERROR
            msg = ("value/flag inconsistent: value={}, flags={}; valid "
                   "value and missing flag")
            if fix_flagconsistency:
                sev = ISSUE_SEVERITY_WARNING
                values[i] = None
                msg += "; Setting value to MISSING (fix_flagconsistency)"
            elif ignore_flagconsistency:
                sev = ISSUE_SEVERITY_WARNING
            issues.add(
                sev, MSGID_FLAGCHECK_VALID_VALUE_MISSIG_FLAG, i, msg.format(
                    values[i], flags[i]))
        if values[i] is None and 100 in flags[i]:
            sev = ISSUE_SEVERITY_ERROR
            msg = ("value/flag inconsistent: value={}, flags={}; missing "
                   "value and flag 100 is not allowed")
            if fix_flagconsistency:
                sev = ISSUE_SEVERITY_WARNING
                flags[i] = [x for x in flags[i] if x != 100]
                msg += "; Removing flag 100 (fix_flagconsistency)"
            elif ignore_flagconsistency:
                sev = ISSUE_SEVERITY_WARNING
            issues.add(
                sev, MSGID_FLAGCHECK_MISSING_VALUE_FLAG_100, i, msg.format(
                    values[i], flags[i]))
        elif missing == 0 and invalid == 0 and values[i] is None:
            issues.add(
                ISSUE_SEVERITY_WARNING, MSGID_FLAGCHECK_MISSING_VALUE_NO_FLAG,
                i,
                "value/flag inconsistent: value={}, flags={}; no "
                "missing or invalid flag: flag 999 added"
                .format(values[i], flags[i]))
            flags[i].append(999)
            missing += 1
    return issues

def _check_value_flag_precip_amount(
    values, flags, ignore_flagconsistency, fix_flagconsistency, idx, issues):
    """
    Special consistency checks and fixes for precipitation amount data.
    Parameters:
        values     list of values for a time series
        flags      list fo flags (list of lists) of a time series
        idx        index of sample to be checked/fixed
        issues     issues list
    Returns:
        None
    Raises:
        None
    """
    for flag in (782, 783, 784):
        # 784    I    Low precipitation, concentration estimated
        # 783    M    Low precipitation, concentration unknown
        # 782    V    Low precipitation, concentration estimated
        if flag in flags[idx]:
            if values[idx] != None:
                issues.add(
                    ISSUE_SEVERITY_WARNING,
                    MSGID_FLAGCHECK_PRECIP_FLAG_782_783_784_DROPPED, idx,
                    "invalid flag {} for precipitation_amount; dropped".format(
                        flag))
                while flag in flags[idx]:
                    flags[idx].remove(flag)
            else:
                sev = ISSUE_SEVERITY_ERROR
                msg = ("invalid flag {} for precipitation_amount with MISSING "
                       "value")
                if fix_flagconsistency:
                    sev = ISSUE_SEVERITY_WARNING
                    msg += "; Removing flag {} (fix_flagconsistency)".format(
                        flag)
                    while flag in flags[idx]:
                        flags[idx].remove(flag)
                elif ignore_flagconsistency:
                    sev = ISSUE_SEVERITY_WARNING
                issues.add(
                    sev, MSGID_FLAGCHECK_PRECIP_FLAG_782_783_784_ERROR, idx,
                    msg.format(flag))
    if 890 in flags[idx]:
        # 890    M    Concentration in precipitation undefined, no
        #             precipitation
        if set(flags[idx]) == {890} and values[idx] == 0.0:
            issues.add(
                ISSUE_SEVERITY_WARNING, MSGID_FLAGCHECK_PRECIP_FLAG_890_DROPPED,
                idx,
                "invalid flag 890 for precipitation amount; "
                "dropping flag 890")
            while 890 in flags[idx]:
                flags[idx].remove(890)
        elif set(flags[idx]) == {890} and values[idx] is None:
            issues.add(
                ISSUE_SEVERITY_WARNING,
                MSGID_FLAGCHECK_PRECIP_FLAG_890_SET_ZERO,
                idx,
                "invalid flag 890 for precipitation amount; "
                "changing MISSING value to 0.0, dropping flag 890")
            while 890 in flags[idx]:
                flags[idx].remove(890)
            values[idx] = 0.0
        else:
            # fix_flagconsistency? Can we fix this?
            sev = ISSUE_SEVERITY_ERROR
            if fix_flagconsistency or ignore_flagconsistency:
                sev = ISSUE_SEVERITY_WARNING
            issues.add(
                sev, MSGID_FLAGCHECK_PRECIP_FLAG_890_ERROR, idx,
                "invalid flag 890 for precipitation amount")

def _check_value_flag_auxiliary_ds(
    values, flags, ignore_flagconsistency, fix_flagconsistency, idx, issues):
    """
    Special consistency checks and fixes for auxiliary datasets.
    Parameters:
        values     list of values for a time series
        flags      list fo flags (list of lists) of a time series
        idx        index of sample to be checked/fixed
        issues     issues list
    Returns:
        None
    Raises:
        None
    """
    _, _, missing, _ = get_flag_summary(flags[idx])
    if missing > 0 and values[idx] != None:
        emfl = EbasMasterFL()
        rem = []
        for flg in flags[idx]:
            try:
                if emfl[flg]['FL_VALIDITY'] == 'M':
                    rem.append(flg)
            except KeyError:
                # non existing flag, ignore here, will be error in
                # general check_value_flag_consistency
                continue
        issues.add(
            ISSUE_SEVERITY_WARNING,
            MSGID_FLAGCHECK_AUX_VALID_VALUE_MISSING_FLAG,
            idx,
            "value/flag inconsistent: value={}, flags={}; valid value and "
            "missing flag{}; fix for auxiliary data: remove missing flag{} "
            "({})".format(
                values[idx], flags[idx], 's' if len(rem) > 1 else '',
                's' if len(rem) > 1 else '', ', '.join([str(x) for x in rem])))
        for fl_ in rem:
            flags[idx].remove(fl_)
