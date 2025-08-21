"""
Basic functionality for handling parameters
(parameter groups, titles for sets of parameters)

Those methods are used both in ebas.io and ebas.domain.entities.ds.
In order to make them available for both modules they are separated in this
general domain module.
"""

from .dataset_types import is_auxiliary
from ..masterdata.pg_pl import EbasMasterPL, EbasMasterPG

EBAS_MASTER_PG = EbasMasterPG()
EBAS_MASTER_PL = EbasMasterPL()

def _optimise_groups(occ):
    """
    Optimise the use of component names and/or group names in order to describe
    the set of variables in the shortes possible way.
    Parameters:
        occ    occurance of different groups for each variable
               list of lists of tuples (list of variables, for each variable
               the list of possible groups and each of those is a tuple of
               (string [name], int [count of CO in the group]).
               The count of CO is set to 0 for comp_name (prefer comp name in
               case where only one variables is in a group)
    Result:
        list of groups/ components necessary to describe all variables (shortest
        possible combination of comp and groups)
    """
    # dictionary over all descriptions (keys), each element a list:
    #     [usable for # of variables, order number of occurances]
    descdict = {}
    for i in range(len(occ)):
        for j in range(len(occ[i])):
            if occ[i][j][0] not in descdict:
                descdict[occ[i][j][0]] = [1, occ[i][j][1]]
            else:
                descdict[occ[i][j][0]][0] += 1

    # convert to a list of tuples:
    #     (description, usable for # of variables, order number of
    #      occurances)
    # and sort the list: usable for # of variables (reversed!), order number
    # Thus, we get a list of descriptions in the order of preferred use:
    desclist = sorted(
        [(key, descdict[key][0], descdict[key][1])
         for key in descdict.keys()],
        key=lambda x: (-x[1], x[2]))

    # generate the result list: preferred description for each variable:
    res = []
    for i in range(len(occ)):
        vardescs = [x[0] for x in occ[i]]
        for desc in desclist:
            if desc[0] in vardescs:
                res.append(desc[0])
                break
    if len(res) != len(occ):
        # be safe
        raise RuntimeError()

    # return a set of all used descriptions, convert to sorted list
    return sorted(set(res))

def param_group(param_list):
    """
    Set of terms that describe the list of parameters in the shortest possible
    way (use group names and comp names)
    Parameters:
        param_list    list with parameter metadata (each tuple
                      (regime, matrix, comp_name))
    Returns:
        groups and/or components list for describing the parameters
    """
    all_groups = []
    for param in param_list:
        regime, matrix, comp_name = param
        if not is_auxiliary(matrix, comp_name):
            all_groups.append(
                [(comp_name, 0)] +
                [(x, EBAS_MASTER_PG[x].CO_COUNT)
                 for x in EBAS_MASTER_PL.list_groups(regime, matrix, comp_name)
                ])
            # Component name has score 0 (always use comp name if a group does
            # not lead to less expressions, i.e. only use a group if more
            # then one ds actually are in the group. See also below.
    # quickfix: if only aux...
    if not all_groups:
        for param in param_list:
            all_groups.append(
                [(comp_name, 0)] +
                [(x, EBAS_MASTER_PG[x].CO_COUNT)
                 for x in EBAS_MASTER_PL.list_groups(regime, matrix, comp_name)
                ])
    return _optimise_groups(all_groups)


def param_desc(param_list):
    """
    Set of terms that describe the list of parameters in the shortest possible
    way (use group descriptions (if not exists, group names) and comp names).
    Parameters:
        param_list    list with parameter metadata (each tuple
                      (regime, matrix, comp_name))
    Returns:
        description for parameters
    """
    return [group if group not in EBAS_MASTER_PG.META or
                not EBAS_MASTER_PG[group].PG_DESC
                else EBAS_MASTER_PG[group].PG_DESC
            for group in param_group(param_list)]

def title(param_list, station_list):
    """
    Generate a title for the series.
    Parameters:
        None
    Returns:
        description for parameters
    """
    desc = param_desc(param_list)
    stations = sorted(set(station_list))
    res = "{} at {}".format(
        ' and '.join([
            x for x in [', '.join(desc[:-1]), desc[-1]]
            if x]),
        ' and '.join([
            x for x in [', '.join(stations[:-1]), stations[-1]]
            if x]))
    if res.startswith('pH '):
        return res
    # first character uppercase
    return res[0:1].upper() + res[1:]
