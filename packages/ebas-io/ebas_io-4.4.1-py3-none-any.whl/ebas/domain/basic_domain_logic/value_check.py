"""
ebas.domain.basic_domain_logic.value_check
$Id: value_check.py 2780 2022-03-09 13:20:02Z pe $
Basic ebas domain logic for value checks (boundary and spike checks).
"""

from nilutility.statistics import running_median, running_stddev
from .. import EbasDomainError
from .flags import get_flag_summary
from .base import EbasDomainIssueList, \
    ISSUE_SEVERITY_ERROR, ISSUE_SEVERITY_WARNING, \
    MSGID_VALUECHECK_BNDCK_LOWER, MSGID_VALUECHECK_BNDCK_UPPER, \
    MSGID_VALUECHECK_SPKCK_LOWER, \
    MSGID_VALUECHECK_SPKCK_UPPER, MSGID_VALUECHECK_SPKCK_STD_LOWER, \
    MSGID_VALUECHECK_SPKCK_STD_UPPER

class _BaseEbasDomBNDIssue(EbasDomainError):
    """
    Base class for boundary/spike check inconsistency exceptions.
    """
    def __init__(self, issues):
        """
        Parameters:
            issues   list of issues, each a tuple (severity, msg-id, value#,
                     message)
        """
        str_ = str([tuple(isu[key] for key in issues.keys)
                    for isu in issues])
        EbasDomainError.__init__(self, str_)
        self.issues = issues

class EbasDomBNDError(_BaseEbasDomBNDIssue):
    """
    Exception class for boundary/spike check inconsistencies (checks for lists).
    """
    def __init__(self, issues):
        """
        Parameters:
            issues   list of issues, each a tuple (severity, msg-id, value#,
                     message)
        """
        _BaseEbasDomBNDIssue.__init__(self, issues)

class EbasDomBNDWarning(_BaseEbasDomBNDIssue):
    """
    Exception class for boundary/spike check inconsistencies (checks for lists).
    """
    def __init__(self, issues):
        """
        Parameters:
            issues   list of issues, each a tuple (severity, msg-id, value#,
                     message)
        """
        _BaseEbasDomBNDIssue.__init__(self, issues)

def check_values(proj, values, flags,
                 minval, maxval,
                 spike_radius,
                 spike_minoffs, spike_maxoffs,
                 spike_stddev_minfact, spike_stddev_maxfact,
                 fix_bc211=False):
    """
    Perform all value checks of data series (values, flags). This includes
    a boudary check and spike detection.
    Parameters:
        proj          project which defines the rule (None or project acronym)
        values        list of values
        flags         list of flags (list of tuples)
                      !! be sure to pass the original list, flags may be
                      !! appenden when using fix_bc211
        minval        minimum allowed (absolute) value
        maxval        minimum allowed (absolute) value
        spike_radius  radius for spike detection
        spike_minoffs minimum factor for deviation from running median
        spike_maxoffs maximum factor for deviation from running median
        spike_stddev_minfact
                      minimum factor of stddev deviation from running median
        spike_stddev_maxfact
                      maximum factor of stddev deviation from running median
        fix_bc211     flag boundary check issues with flag 211
    Returns:
        EbasDomainIssueList with issues found (empty list if OK)
    """
    return EbasDomainIssueList(sorted(
        boundary_check(
            proj, values, flags, minval, maxval, fix_bc211=fix_bc211) +
        spike_check(
            proj, values, flags, spike_radius,
            spike_minoffs, spike_maxoffs, spike_stddev_minfact,
            spike_stddev_maxfact,
            fix_bc211=fix_bc211),
        key=lambda x: (x['row'], x['msg_id'])))

def boundary_check(proj, values, flags, minval, maxval, fix_bc211=False):
    """
    Boundary check of data series (values, flags).
    Parameters:
        proj          project which defines the rule (None or project acronym)
        values        list of values
        flags         list of flags (list of tuples)
                      !! be sure to pass the original list, flags may be
                      !! appenden when using fix_bc211
        minval        minimum allowed (absolute) value
        maxval        minimum allowed (absolute) value
        fix_bc211     flag boundary check issues with flag 211
    Returns:
        EbasDomainIssueList with issues found (empty list if OK)
    """
    proj = " ({})".format(proj) if proj else ""
    issues = EbasDomainIssueList()
    if minval is None and maxval is None:
        # no boundaries defined, no issues to report
        return issues
    for i, value in enumerate(values):
        if value is None:
            continue
        if minval is not None and value < minval and \
                not bc_exceptions(flags[i], False):
            if fix_bc211:
                flags[i].append(211)
                issues.add(
                    ISSUE_SEVERITY_WARNING, MSGID_VALUECHECK_BNDCK_LOWER, i,
                    "Boundary check{}: value {} is less than defined "
                    "minimum {}, --fix bc211: adding flag 211".format(
                        proj, value, minval))
            else:
                issues.add(
                    ISSUE_SEVERITY_ERROR, MSGID_VALUECHECK_BNDCK_LOWER, i,
                    "Boundary check{}: value {} is less than defined "
                    "minimum {}".format(proj, value, minval))
        if maxval is not None and value > maxval and \
                not bc_exceptions(flags[i], True):
            if fix_bc211:
                flags[i].append(211)
                issues.add(
                    ISSUE_SEVERITY_WARNING, MSGID_VALUECHECK_BNDCK_UPPER, i,
                    "Boundary check{}: value {} is greater than defined "
                    "maximum {}, --fix bc211: adding flag 211".format(
                        proj, value, maxval))
            else:
                issues.add(
                    ISSUE_SEVERITY_ERROR, MSGID_VALUECHECK_BNDCK_UPPER, i,
                    "Boundary check{}: value {} is greater than defined "
                    "maximum {}".format(proj, value, maxval))
    return issues

def spike_check(
        proj, values, flags, spike_radius, spike_minoffs, spike_maxoffs,
        spike_stddev_minfact, spike_stddev_maxfact, fix_bc211):
    """
    Spike check of data series (values, flags).
    Parameters:
        proj          project which defines the rule (None or project acronym)
        values        list of values
        flags         list of flags (list of tuples)
                      !! be sure to pass the original list, flags may be
                      !! appenden when using fix_bc211
        spike_radius  radius for spike detection
        spike_minoffs minimum factor for deviation from running median
        spike_maxoffs maximum factor for deviation from running median
        spike_stddev_minfact
                      minimum factor of stddev deviation from running median
        spike_stddev_maxfact
                      maximum factor of stddev deviation from running median
        fix_bc211     flag boundary check issues with flag 211
    Returns:
        EbasDomainIssueList with issues found (empty list if OK)
    """
    proj = " ({})".format(proj) if proj else ""
    issues = EbasDomainIssueList()
    if spike_radius is None and spike_minoffs is None and \
            spike_maxoffs is None and spike_stddev_minfact is None and \
            spike_stddev_maxfact is None:
        # no spike definitions, no issues to report
        return issues
    # modify values, only take those which are not flagged invalid
    values = [val if get_flag_summary(fla)[1] == 0 else None
              for val, fla in zip(values, flags)]
    medians = running_median(values, spike_radius)
    stddevs = []
    if spike_stddev_minfact is not None or spike_stddev_maxfact is not None:
        # we need to calculate running stddevs:
        stddevs = running_stddev(values, spike_radius)
    for i in range(len(values)):  # pylint: disable=C0200
        # C0200: Consider using enumerate instead of iterating with range/len
        # --> use same index for several lists, alternative would be a threefold
        # zip and additionally, I would need the index, which makes
        # an enumerate(zip(x, y, z)) -- ugly and less readable
        if values[i] is None:
            continue
        if spike_minoffs is not None and \
                values[i] < medians[i] + spike_minoffs and \
                not bc_exceptions(flags[i], False):
            if fix_bc211:
                flags[i].append(211)
                issues.add(
                    ISSUE_SEVERITY_WARNING, MSGID_VALUECHECK_SPKCK_LOWER, i,
                    "Spike check{}: value ({}) is less than running median "
                    "({}) {} {}; --fix bc211: adding flag 211".format(
                        proj, values[i], medians[i],
                        "-" if spike_minoffs < 0 else "+",
                        abs(spike_minoffs)))
            else:
                issues.add(
                    ISSUE_SEVERITY_ERROR, MSGID_VALUECHECK_SPKCK_LOWER, i,
                    "Spike check{}: value ({}) is less than running median "
                    "({}) {} {}".format(
                        proj, values[i], medians[i],
                        "-" if spike_minoffs < 0 else "+",
                        abs(spike_minoffs)))
        if spike_maxoffs is not None and \
                values[i] > medians[i] + spike_maxoffs and \
                not bc_exceptions(flags[i], True):
            if fix_bc211:
                flags[i].append(211)
                issues.add(
                    ISSUE_SEVERITY_WARNING, MSGID_VALUECHECK_SPKCK_UPPER, i,
                    "Spike check{}: value ({}) is greater than running median "
                    "({}) {} {}; --fix bc211: adding flag 211".format(
                        proj, values[i], medians[i],
                        "-" if spike_maxoffs < 0 else "+",
                        abs(spike_maxoffs)))
            else:
                issues.add(
                    ISSUE_SEVERITY_ERROR, MSGID_VALUECHECK_SPKCK_UPPER, i,
                    "Spike check{}: value ({}) is greater than running median "
                    "({}) {} {}".format(
                        proj, values[i], medians[i],
                        "-" if spike_maxoffs < 0 else "+",
                        abs(spike_maxoffs)))
        if spike_stddev_minfact is not None and stddevs[i] is not None and \
                values[i] < medians[i] + spike_stddev_minfact * stddevs[i] and \
                not bc_exceptions(flags[i], False):
                # stddevs[i] is None when there is less then 2 valid values
            if fix_bc211:
                flags[i].append(211)
                issues.add(
                    ISSUE_SEVERITY_WARNING, MSGID_VALUECHECK_SPKCK_STD_LOWER, i,
                    "Spike check{}: value ({}) is less than running median "
                    "({}) {} {} * running stddev ({}); "
                    "--fix bc211: adding flag 211".format(
                        proj, values[i], medians[i],
                        "-" if spike_stddev_minfact < 0 else "+",
                        abs(spike_stddev_minfact), stddevs[i]))
            else:
                issues.add(
                    ISSUE_SEVERITY_ERROR, MSGID_VALUECHECK_SPKCK_STD_LOWER, i,
                    "Spike check{}: value ({}) is less than running median ({}) "
                    "{} {} * running stddev ({})".format(
                        proj, values[i], medians[i],
                        "-" if spike_stddev_minfact < 0 else "+",
                        abs(spike_stddev_minfact), stddevs[i]))
        if spike_stddev_maxfact is not None and stddevs[i] is not None and \
                values[i] > medians[i] + spike_stddev_maxfact * stddevs[i] and \
                not bc_exceptions(flags[i], True):
                # stddevs[i] is None when there is less then 2 valid values
            if fix_bc211:
                flags[i].append(211)
                issues.add(
                    ISSUE_SEVERITY_WARNING, MSGID_VALUECHECK_SPKCK_STD_UPPER, i,
                    "Spike check{}: value ({}) is greater than running median "
                    "({}) {} {} * running stddev ({}); "
                    "--fix bc211: adding flag 211".format(
                        proj, values[i], medians[i],
                        "-" if spike_stddev_maxfact < 0 else "+",
                        abs(spike_stddev_maxfact), stddevs[i]))
            else:
                issues.add(
                    ISSUE_SEVERITY_ERROR, MSGID_VALUECHECK_SPKCK_STD_UPPER, i,
                    "Spike check{}: value ({}) is greater than running median "
                    "({}) {} {} * running stddev ({})".format(
                        proj, values[i], medians[i],
                        "-" if spike_stddev_maxfact < 0 else "+",
                        abs(spike_stddev_maxfact), stddevs[i]))
    return issues

def bc_exceptions(flags, upper_bnd):
    """
    Check if an exception for the boundary checks should be made.
    There is a defined list of valid flags that make an exception. In
    addition, any invalid flag makes an exception for the boundary checks.
    Parameters:
        flags      list of flags for the sample
        upper_bnd  bool, should the upper (True) or lower (False) boudary
                   be checked
    """
    # some valid flags make an exception:
    flaglist_exception = [100, 111, 211]
    if upper_bnd:
        flaglist_exception += [110, 210, 410, 559]
    else:
        flaglist_exception += [147]
    if any([x in flaglist_exception for x in flags]):
        return True

    # all invald flags make an exception:
    if get_flag_summary(flags)[1] > 0:
        return True
    return False
