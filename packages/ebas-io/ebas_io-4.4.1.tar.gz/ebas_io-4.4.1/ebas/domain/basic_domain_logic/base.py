"""
$Id: base.py 2427 2020-03-19 23:09:09Z pe $
"""

from nilutility.datatypes import ControlledDictList


ISSUE_SEVERITY_ERROR = 1
ISSUE_SEVERITY_WARNING = 2

###
### Message IDs (centralized here, to make sure IDs are unique
###

# flag issues, used in ebas.domain.basic_domain_logic.flags
MGGID_OFFSET_FLAGCHECK = 0
MSGID_FLAGCHECK_ILLEGAL = MGGID_OFFSET_FLAGCHECK + 1
MSGID_FLAGCHECK_MISSING_100 = MGGID_OFFSET_FLAGCHECK + 2
# flag issues based on checking flags/value cjnsistency or considering
# properties of the time series (precipitation amount, axiliary data)
# (checked in check_value_flag_consistency):
MSGID_FLAGCHECK_VALID_VALUE_MISSIG_FLAG = MGGID_OFFSET_FLAGCHECK + 3
MSGID_FLAGCHECK_MISSING_VALUE_FLAG_100 = MGGID_OFFSET_FLAGCHECK + 4
MSGID_FLAGCHECK_MISSING_VALUE_NO_FLAG = MGGID_OFFSET_FLAGCHECK + 5
MSGID_FLAGCHECK_PRECIP_FLAG_782_783_784_DROPPED = MGGID_OFFSET_FLAGCHECK + 6
MSGID_FLAGCHECK_PRECIP_FLAG_782_783_784_ERROR = MGGID_OFFSET_FLAGCHECK + 7
MSGID_FLAGCHECK_PRECIP_FLAG_890_DROPPED = MGGID_OFFSET_FLAGCHECK + 8
MSGID_FLAGCHECK_PRECIP_FLAG_890_SET_ZERO = MGGID_OFFSET_FLAGCHECK + 9
MSGID_FLAGCHECK_PRECIP_FLAG_890_ERROR = MGGID_OFFSET_FLAGCHECK + 10
MSGID_FLAGCHECK_AUX_VALID_VALUE_MISSING_FLAG = MGGID_OFFSET_FLAGCHECK + 11
# all possible issue IDs (used for initialization of issue list)
ALL_MSGID_FLAGCHECK = (
    MSGID_FLAGCHECK_ILLEGAL, MSGID_FLAGCHECK_MISSING_100,
    MSGID_FLAGCHECK_VALID_VALUE_MISSIG_FLAG,
    MSGID_FLAGCHECK_MISSING_VALUE_FLAG_100,
    MSGID_FLAGCHECK_MISSING_VALUE_NO_FLAG,
    MSGID_FLAGCHECK_PRECIP_FLAG_782_783_784_DROPPED,
    MSGID_FLAGCHECK_PRECIP_FLAG_782_783_784_ERROR,
    MSGID_FLAGCHECK_PRECIP_FLAG_890_DROPPED,
    MSGID_FLAGCHECK_PRECIP_FLAG_890_SET_ZERO,
    MSGID_FLAGCHECK_PRECIP_FLAG_890_ERROR,
    MSGID_FLAGCHECK_AUX_VALID_VALUE_MISSING_FLAG)

# value check issues (boundaries and spikes), used in
# ebas.domain.basic_domain_logic.value_check
MSGID_OFFSET_VALUECHECK = 100
MSGID_VALUECHECK_BNDCK_LOWER = MSGID_OFFSET_VALUECHECK + 1
MSGID_VALUECHECK_BNDCK_UPPER = MSGID_OFFSET_VALUECHECK + 2
MSGID_VALUECHECK_SPKCK_LOWER = MSGID_OFFSET_VALUECHECK + 3
MSGID_VALUECHECK_SPKCK_UPPER = MSGID_OFFSET_VALUECHECK + 4
MSGID_VALUECHECK_SPKCK_STD_LOWER = MSGID_OFFSET_VALUECHECK + 5
MSGID_VALUECHECK_SPKCK_STD_UPPER = MSGID_OFFSET_VALUECHECK + 6
# all possible issue IDs (used for initialization of issue list)
ALL_MSGID_VALUECHECK = (
    MSGID_VALUECHECK_BNDCK_LOWER, MSGID_VALUECHECK_BNDCK_UPPER,
    MSGID_VALUECHECK_SPKCK_LOWER, MSGID_VALUECHECK_SPKCK_UPPER,
    MSGID_VALUECHECK_SPKCK_STD_LOWER, MSGID_VALUECHECK_SPKCK_STD_UPPER)

# boundary and spike check selection issues, used in
# ebas.io.file.basefile.ceck_data and ebas.domain.entities.ts
MSGID_OFFSET_BCSEL = 100
MSGID_BCSEL_NO_PROJ = MSGID_OFFSET_BCSEL + 1
MSGID_BCSEL_DUPLICATES = MSGID_OFFSET_BCSEL + 2
ALL_MSGID_BCSEL = (MSGID_BCSEL_NO_PROJ, MSGID_BCSEL_DUPLICATES)


class EbasDomainIssueList(ControlledDictList):
    """
    List of issues to be reported to a caller. Multiple errors and warnings are
    possible. The caller can decide whhat to do with the issues (usually
    condense and log them).
    """
    def __init__(self, *args, **kwargs):
        """
        Set up the issue list.
        Parameters:
            keys    key names used for the elements of teach issue
        Returns:
            none
        """
        self.allowed = {}
        if 'keys' not in kwargs:
            # default keys for issue list
            kwargs['keys'] = ('severity', 'msg_id', 'row', 'message')
        if 'msg_id' not in kwargs or not kwargs['msg_id']:
            kwargs['msg_id'] = ALL_MSGID_FLAGCHECK + ALL_MSGID_VALUECHECK + \
                ALL_MSGID_BCSEL
        for key in kwargs['keys']:
            if key not in kwargs and key == 'severity':
                # default severities:
                kwargs[key] = [ISSUE_SEVERITY_ERROR,
                               ISSUE_SEVERITY_WARNING]
        super(EbasDomainIssueList, self).__init__(*args, **kwargs)
